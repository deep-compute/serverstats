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
    >>> _fields = {
    ...     'cpu': ['usage_percent', 'idle_percent', 'iowait',
    ...             'avg_load_15_min', 'avg_load_5_min', 'avg_load_1_min'],
    ...     'cpu_times': ['user', 'nice', 'system', 'idle', 'iowait',
    ...             'irq', 'softirq', 'steal', 'guest', 'guest_nice'],
    ...     'cpu_stats': ['ctx_switches', 'interrupts', 'soft_interrupts', 'syscalls'],
    ...     'cpu_times_percent': ['user', 'nice', 'system', 'idle',
    ...             'iowait', 'irq', 'softirq', 'steal', 'guest', 'guest_nice'],
    ...     'ram': ['total', 'available', 'percent', 'used', 'free',
    ...             'active', 'inactive', 'buffers', 'cached', 'shared', 'slab'],
    ...     'swap': ['total', 'used', 'free', 'percent', 'sin', 'sout'],
    ...     'disk': ['total', 'free', 'used', 'percent'],
    ...     'disk_partitions': ['sda1', 'sda15'],
    ...     'disk_io_counters': ['sda1', 'sda15'],
    ...     'network_traffic': ['lo', 'eth0']}
    >>> for key, value in dl.items():
    ...     lst = list()
    ...     if type(value) is dict:
    ...         for t , c in value.items():
    ...             lst.append(t)
    ...         fields[key] = lst
    ...
    >>> _fields == fields
    True
    """

    load1, load5, load15 = psutil.os.getloadavg()
    cpu_percent = psutil.cpu_percent()
    cpu_times = psutil.cpu_times()._asdict()
    cpu_stats = psutil.cpu_stats()._asdict()
    percpu_percent = psutil.cpu_percent(interval=None, percpu=True)
    cpu_times_percent = psutil.cpu_times_percent(interval=None, percpu=False)._asdict()
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

    disk = {}
    disk["total"] = 0
    disk["used"] = 0
    disk["percent"] = 0
    for key, val in disk_partitions.items():
        disk["total"] += val.get("total")
        disk["used"] += val.get("used")
        disk["percent"] += val.get("percent")
    disk["free"] = disk["total"]-disk["used"]
    disk["percent"] = disk["percent"]/len(disk_partitions)

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
        disk=disk,
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
