"""
Demo state management — start/stop benign traffic and attacks.
Wraps dashboard.demo_state directly.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from demo_state import (
    read_state,
    set_benign,
    set_attack,
    set_all_attacks,
    stop_all,
    queue_burst,
    any_active,
)

router = APIRouter()


class BenignRequest(BaseModel):
    active: bool
    speed: float = 1.0


class AttackRequest(BaseModel):
    attack_type: str
    active: bool


class BurstRequest(BaseModel):
    attack_type: str
    count: int


@router.get("")
def get_state():
    return read_state()


@router.get("/active")
def is_active():
    return {"active": any_active()}


@router.post("/benign")
def post_benign(req: BenignRequest):
    set_benign(req.active, req.speed)
    return {"ok": True}


@router.post("/attack")
def post_attack(req: AttackRequest):
    set_attack(req.attack_type, req.active)
    return {"ok": True}


@router.post("/attack/all")
def post_all_attacks(req: AttackRequest):
    set_all_attacks(req.active)
    return {"ok": True}


@router.post("/stop")
def post_stop():
    stop_all()
    return {"ok": True}


@router.post("/burst")
def post_burst(req: BurstRequest):
    queue_burst(req.attack_type, req.count)
    return {"ok": True}
