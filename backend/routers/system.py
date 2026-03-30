"""
Real system metrics — CPU, memory, disk, network I/O, uptime, hostname.
Uses psutil to report actual server stats.
"""

import time
import socket
import platform
from datetime import timedelta

import psutil
from fastapi import APIRouter

router = APIRouter()

_boot_time = psutil.boot_time()
_prev_net = psutil.net_io_counters()
_prev_time = time.time()


@router.get("")
def system_metrics():
    global _prev_net, _prev_time

    # CPU & memory
    cpu_pct = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory()

    # Disk
    disk = psutil.disk_usage("/")

    # Network throughput (bytes/sec since last call)
    now = time.time()
    net = psutil.net_io_counters()
    dt = max(now - _prev_time, 0.1)
    bytes_recv_sec = (net.bytes_recv - _prev_net.bytes_recv) / dt
    bytes_sent_sec = (net.bytes_sent - _prev_net.bytes_sent) / dt
    _prev_net = net
    _prev_time = now

    # Connections
    try:
        conns = len(psutil.net_connections(kind="inet"))
    except (psutil.AccessDenied, PermissionError):
        conns = 0

    # Uptime
    uptime_sec = time.time() - _boot_time
    uptime_str = str(timedelta(seconds=int(uptime_sec)))

    # Hostname & OS
    hostname = socket.gethostname()
    os_info = f"{platform.system()} {platform.release()}"

    return {
        "cpu_pct": round(cpu_pct, 1),
        "mem_pct": round(mem.percent, 1),
        "mem_used_gb": round(mem.used / (1024 ** 3), 1),
        "mem_total_gb": round(mem.total / (1024 ** 3), 1),
        "disk_pct": round(disk.percent, 1),
        "disk_used_gb": round(disk.used / (1024 ** 3), 1),
        "disk_total_gb": round(disk.total / (1024 ** 3), 1),
        "net_down_mbps": round(bytes_recv_sec / (1024 * 1024), 2),
        "net_up_mbps": round(bytes_sent_sec / (1024 * 1024), 2),
        "net_total_recv_gb": round(net.bytes_recv / (1024 ** 3), 2),
        "net_total_sent_gb": round(net.bytes_sent / (1024 ** 3), 2),
        "connections": conns,
        "packets_recv": net.packets_recv,
        "packets_sent": net.packets_sent,
        "hostname": hostname,
        "os": os_info,
        "uptime": uptime_str,
    }
