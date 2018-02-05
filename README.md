
# ServerStats
**Collect important system metrics from a server and log them**

We support collecting metrics for the following components:
* cpu
* disk
* network_traffic
* ram
* swapmemory

## Installation
> Prerequisites: Python2.7

```bash
sudo pip install serverstats
```

## Usage
```
$ serverstats run
```
Shows you the system metrics collected at every 5 sec (configurable) interval
To set the time interval of collection:
```
$ serverstats run --interval <int value>
```
![](https://i.imgur.com/J4aUO7S.gif)

#### on python interpreter


```
>>> from serverstats import get_system_metrics
>>> from pprint import pprint

>>> pprint(get_system_metrics())
{'cpu': {'idle_percent': 78.75,
         'iowait': 2989.3,
         'load1': 0.5,
         'load15': 0.85,
         'load5': 0.63,
         'usage_precent': 21.25},
 'disk': {'disk_free': 890965590016,
          'disk_free_percent': 90.94094876747448,
          'disk_total': 979718819840,
          'disk_usage': 38962806784,
          'disk_usage_percent': 4.2},
 'network_traffic': {'enp4s0': {'recieved': 44961048, 'sent': 14742510},
                     'lo': {'recieved': 459583, 'sent': 459583},
                     'wlp5s0': {'recieved': 181141, 'sent': 99029}},
 'ram': {'avail': 5848301568,
         'avail_percent': 70.77202939317712,
         'free': 2760843264,
         'total': 8263577600,
         'usage': 1706135552,
         'usage_percent': 29.2},
 'swapmemory': {'free': 3534168064,
                'free_percent': 84.28228569084233,
                'total': 4193251328,
                'usage': 659083264,
                'usage_percent': 15.7}}
```
![](https://i.imgur.com/srfpubK.gif)


