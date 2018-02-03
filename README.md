
# ServerStats
**Collect important system metrics from a server and log them**


## Installation
> Prerequisites: Python2.7

> Note: tested and it works in python2.7 and not tested in other versions.

```bash
sudo pip install serverstats
```

## Usage
#### on python interpreter
```
>>> import serverstats

>>> serverstats.get_system_metrics()
{'disk': {'disk_usage': 33154150400, 'disk_total': 979718819840, 'disk_free_percent': 91.5338389178289, 'disk_free': 896774246400, 'disk_usage_percent': 3.6}, 'ram': {'avail': 4904124416, 'usage_percent': 40.7, 'avail_percent': 59.346262035465124, 'usage': 2394849280, 'total': 8263577600, 'free': 3126648832}, 'cpu': {'load1': 1.8, 'usage_precent': 53.75, 'load15': 2.15, 'idle_percent': 46.25, 'iowait': 570.01, 'load5': 1.85}, 'swapmemory': {'usage': 0, 'total': 4193251328, 'free_percent': 100.0, 'free': 4193251328, 'usage_percent': 0.0}, 'network_traffic': {'bytes_sent_lo': 126988710, 'bytes_sent_enp4s0': 98743690, 'bytes_sent_wlp5s0': 7857549, 'bytes_rcvd_enp4s0': 363820124, 'bytes_rcvd_lo': 126988710, 'bytes_rcvd_wlp5s0': 198589266}}
>>> 

```

![](https://i.imgur.com/qbnm2OV.gif)

