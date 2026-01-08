"""
Capture package
"""

from .network_capture import (
    NetworkInterface,
    PacketCapture,
    SimulatedCapture,
    get_available_interfaces,
    create_capture,
    SCAPY_AVAILABLE
)

# New modules
from .pcap_analyzer import PcapAnalyzer
from .live_capture import LiveCapture

__all__ = [
    'NetworkInterface',
    'PacketCapture', 
    'SimulatedCapture',
    'get_available_interfaces',
    'create_capture',
    'SCAPY_AVAILABLE',
    'PcapAnalyzer',
    'LiveCapture',
]

