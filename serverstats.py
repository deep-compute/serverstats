import psutil
from time import sleep

from deeputil import keeprunning
from basescript import BaseScript

def get_system_metrics():
    # FIXME: look at this code and make it better
    load1, load5, load15 = psutil.os.getloadavg()
    cpu_count = psutil.cpu_count()
    load_avg_15_min = (load15 / float(cpu_count) * 100)
    load_avg_5_min = (load5 / float(cpu_count) * 100)
    load_avg_1_min = (load1 / float(cpu_count) * 100)

    network_traffic = psutil.net_io_counters(pernic=True)
    cpu_stats = psutil.cpu_times()
    memory = psutil.virtual_memory()
    swap_mem = psutil.swap_memory()
    disk = psutil.disk_usage('/')

    if swap_mem.total == 0:
        swapmemory_free_percent = 0
    else:
        swapmemory_free_percent = (swap_mem.free / float(swap_mem.total) * 100)

    network_traffic_info = dict()
    for interface in network_traffic:
        bytes_sent_interface='bytes_sent_%s' %interface
        bytes_rcvd_interface='bytes_rcvd_%s' %interface
        network_traffic_info[bytes_sent_interface]=network_traffic[interface].bytes_sent
        network_traffic_info[bytes_rcvd_interface]=network_traffic[interface].bytes_recv

    return dict(
        #load_avg info
        cpu = dict(
                usage_precent=load_avg_15_min,
                idle_percent=100.00 - load_avg_15_min,
                iowait=cpu_stats.iowait,
                load15=load15,
                load5=load5,
                load1=load1
                    ),

        #ram info
        ram = dict(
                total=memory.total,
                avail=memory.available,
                usage=memory.used,
                free=memory.free,
                usage_percent=memory.percent,
                avail_percent=(memory.available / float(memory.total) * 100)
                    ),

        #swap memory info
        swapmemory = dict(
                usage_percent=swap_mem.percent,
                free_percent=swapmemory_free_percent,
                total=swap_mem.total,
                usage=swap_mem.used,
                free=swap_mem.free,
                        ),

        #disk info
        disk = dict(
                disk_total=disk.total,
                disk_usage=disk.used,
                disk_free=disk.free,
                disk_usage_percent=disk.percent,
                disk_free_percent=(disk.free / float(disk.total) * 100),
                    ),

        #network traffic
        network_traffic = network_traffic_info
    )

class ServerStats(BaseScript):
    NAME = 'ServerStats'
    DESC = 'Gather load avg, ram usage and disk space statistics'

    def __init__(self):
        super(ServerStats, self).__init__()
        self.collection_wait = self.args.collection_wait

    def _log_exception(self, exp):
        self.log.exception('Error during run ', exp=exp)

    @keeprunning(on_error=_log_exception) #FIXME: configure this prop
    def _log_system_metrics(self):
        try:
            self.log.info('system_metrics', type='metric', **get_system_metrics())
        except: 
            raise
        finally:
            sleep(self.collection_wait)

    def define_args(self, parser):
        parser.add_argument('-n', '--collection-wait', type=int, default=5, 
                        help='Seconds to wait after collection of stats')

    def run(self):
        self._log_system_metrics()

def main():
    ServerStats().start()

if __name__ == '__main__':
    main()

