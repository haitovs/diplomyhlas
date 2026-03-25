"""
Shared demo state — file-based so it works across browser tabs.
The traffic simulator and attacker console write flags here.
The live monitor reads them and generates flows accordingly.
"""

import json
import time
from pathlib import Path

STATE_FILE = Path(__file__).parent.parent / "data" / ".demo_state.json"

DEFAULT_STATE = {
    "benign_active": False,
    "benign_speed": 1.0,
    "attacks": {
        "ddos": False,
        "portscan": False,
        "ssh": False,
        "ftp": False,
    },
    "bursts": [],
    "last_update": 0,
}


def read_state() -> dict:
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, "r") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return dict(DEFAULT_STATE)


def write_state(state: dict):
    state["last_update"] = time.time()
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def set_benign(active: bool, speed: float = 1.0):
    state = read_state()
    state["benign_active"] = active
    state["benign_speed"] = speed
    write_state(state)


def set_attack(attack_type: str, active: bool):
    state = read_state()
    state["attacks"][attack_type] = active
    write_state(state)


def set_all_attacks(active: bool):
    state = read_state()
    for key in state["attacks"]:
        state["attacks"][key] = active
    write_state(state)


def stop_all():
    write_state(dict(DEFAULT_STATE))


def queue_burst(attack_type: str, count: int):
    """Queue a one-shot burst of N packets. Monitor will process and clear it."""
    state = read_state()
    if "bursts" not in state:
        state["bursts"] = []
    state["bursts"].append({"type": attack_type, "count": count})
    write_state(state)


def pop_bursts() -> list:
    """Read and clear all pending bursts. Returns list of {type, count}."""
    state = read_state()
    bursts = state.get("bursts", [])
    if bursts:
        state["bursts"] = []
        write_state(state)
    return bursts


def any_active() -> bool:
    state = read_state()
    return (
        state["benign_active"]
        or any(state["attacks"].values())
        or len(state.get("bursts", [])) > 0
    )
