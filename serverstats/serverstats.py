import os
from time import sleep

from flatten_dict import flatten
from flatten_dict.reducers import make_reducer
import psutil
from deeputil import keeprunning
from basescript import BaseScript


def get_system_metrics():
    """
    For keys in fields

    >>> from serverstats import get_system_metrics
    >>> fields = dict()
    >>> dl = get_system_metrics()
    >>> _fields = {'cpu': ['avg_load_5_min',
    ...                   'avg_load_15_min',
    ...                   'idle_percent',
    ...                   'iowait',
    ...                   'avg_load_1_min',
    ...                   'usage_percent'],
    ...           'disk': ['usage', 'total', 'free_percent', 'usage_percent', 'free'],
    ...           'ram': ['avail', 'usage_percent', 'avail_percent', 'usage', 'total', 'free'],
    ...           'swap': ['usage', 'total', 'free_percent', 'free', 'usage_percent']}
    >>>
    >>> for key, value in dl.iteritems():
    ...     lst = list()
    ...     if type(value) is dict and key != 'network_traffic':
    ...         for t , c in value.iteritems():
    ...             lst.append(t)
    ...         fields[key] = lst
    ...
    >>> _fields == fields
    True

    For type of every field

    >>> from flatten_dict import flatten
    >>> flat_dl = flatten(dl)
    >>> for key in flat_dl:
    ...     assert isinstance(flat_dl[key], float)

    """
    load1, load5, load15 = psutil.os.getloadavg()
    cpu_percent = psutil.cpu_percent()
    cpu_times = psutil.cpu_times()._asdict()
    cpu_stats = psutil.cpu_stats()._asdict()
    percpu_percent = psutil.cpu_percent(interval=None, percpu=True)
    cpu_times_percent = psutil.cpu_times_percent(interval=None, percpu=False)
    cpu_count = psutil.cpu_count(logical=True)
    cpu_freq = [freq._asdict() for freq in psutil.cpu_freq(percpu=True)]

    network_traffic_info = psutil.net_io_counters(pernic=True)
    memory = psutil.virtual_memory()._asdict()
    swap_mem = psutil.swap_memory()._asdict()

    disk_partitions = {}
    fs_types = set()
    for part in psutil.disk_partitions(all=False):
        usage = {}
        if os.name == 'nt':
            if 'cdrom' in part.opts or part.fstype == '':
                continue
        usage = part._asdict()
        usage.pop("opts")
        device = usage["device"].split("/")[-1]
        fs_types.add(device)
        _usage = psutil.disk_usage(part.mountpoint)
        disk_partitions.update({device: {**usage, **_usage._asdict()}})

    disk_usage = {}
    disk_usage["total"] = 0
    disk_usage["free"] = 0
    disk_usage["used"] = 0
    disk_usage["percent"] = 0
    for k, v in disk_partitions.items():
        disk_usage["total"] += v.get("total")
        disk_usage["used"] += v.get("used")
        disk_usage["free"] += v.get("free")
        disk_usage["percent"] += v.get("percent")
    disk_usage["percent"] = disk_usage["percent"]/len(disk_partitions)

    disk_io_counters = {}
    for key, val in psutil.disk_io_counters(perdisk=True, nowrap=False).items():
        if key in fs_types:
            disk_io_counters[key] = val._asdict()

    network_traffic = dict()
    for interface in network_traffic_info:
        if any(st in interface for st in ["veth", "docker", "br"]):
            continue
        network_traffic[interface] = {
            "bytes_sent": float(network_traffic_info[interface].bytes_sent),
            "bytes_received": float(network_traffic_info[interface].bytes_recv),
            "packets_sent": float(network_traffic_info[interface].packets_sent),
            "packets_recv": float(network_traffic_info[interface].packets_recv)
        }
    net_connections = psutil.net_connections(kind='inet')
    num_pids = len(psutil.pids())
    num_users = len(psutil.users())


    return dict(
        # load_avg info
        cpu=dict(
            usage_percent=float(cpu_percent),
            idle_percent=float(100.00 - cpu_percent),
            iowait=float(cpu_times.get("iowait")),
            avg_load_15_min=float(load15),
            avg_load_5_min=float(load5),
            avg_load_1_min=float(load1),
        ),
        # cpu times
        cpu_times=cpu_times,
        # cpu stats
        cpu_stats=cpu_stats,
        # percpu pervents
        percpu_percent=percpu_percent,
        # cpu times percent
        cpu_times_percent=cpu_times_percent,
        # number of cpu
        cpu_count=cpu_count,
        # cpu frequency
        cpu_freq=cpu_freq,
        # ram info
        ram=memory,
        # swap memory info
        swap=swap_mem,
        # disk info
        disk=disk_usage,
        # disk partitions info
        disk_partitions = disk_partitions,
        # disk io counter
        disk_io_counters = disk_io_counters,
        # network traffic
        network_traffic=network_traffic,
        # number of net connections
        num_net_connections=len(net_connections),
        # number of pids
        num_pids=num_pids,
        # number of users
        num_users=num_users

    )


class ServerStats(BaseScript):
    NAME = "ServerStats"
    DESC = "Collect important system metrics from a server and log them"

    def __init__(self):
        super(ServerStats, self).__init__()
        self.interval = self.args.interval

    def _log_exception(self, exp):
        self.log.exception("error_during_run ", exp=exp)

    @keeprunning(on_error=_log_exception)
    def _log_system_metrics(self):
        metric = flatten(get_system_metrics(), reducer=make_reducer(delimiter='.'), enumerate_types=(list,))
        self.log.info("system_metrics", type="metric", **metric)
        sleep(self.interval)

    def define_args(self, parser):
        parser.add_argument(
            "-i",
            "--interval",
            type=int,
            default=5,
            help="Seconds to wait after collection of stats",
        )

    def run(self):
        self._log_system_metrics()


def main():
    ServerStats().start()


if __name__ == "__main__":
    main()
