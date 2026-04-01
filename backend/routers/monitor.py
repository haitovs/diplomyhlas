"""
Live monitoring — WebSocket feed + history + stats endpoints.
Ingests flows from demo state (Traffic Simulator / Attacker Console),
runs ML predictions, and streams results to the React frontend.
"""

import random
import asyncio
from datetime import datetime
from pathlib import Path

import pandas as pd
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import sys

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.inference.realtime import RealtimePredictor
from demo_state import read_state, pop_bursts, any_active

router = APIRouter()

# ── Shared state ─────────────────────────────────────────────────────────

predictor = RealtimePredictor(model_path=str(PROJECT_ROOT / "models"))

SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"
from demo_state import STATE_FILE
print(f"[monitor] PROJECT_ROOT={PROJECT_ROOT}")
print(f"[monitor] STATE_FILE={STATE_FILE} writable={STATE_FILE.parent.exists()}")
print(f"[monitor] SAMPLES_DIR={SAMPLES_DIR} exists={SAMPLES_DIR.is_dir()}")
print(f"[monitor] Model loaded={predictor.loaded}")

try:
    import joblib
    feature_columns = list(joblib.load(PROJECT_ROOT / "models" / "feature_columns.joblib"))
    print(f"[monitor] feature_columns: {len(feature_columns)} features")
except Exception as e:
    feature_columns = []
    print(f"[monitor] ERROR loading feature_columns: {e}")

try:
    benign_data = pd.read_csv(SAMPLES_DIR / "benign_flows.csv")
    print(f"[monitor] benign_data: {len(benign_data)} rows, cols={list(benign_data.columns[:5])}")
except Exception as e:
    benign_data = pd.DataFrame()
    print(f"[monitor] ERROR loading benign_data: {e}")

try:
    malicious_data = pd.read_csv(SAMPLES_DIR / "malicious_flows.csv")
    print(f"[monitor] malicious_data: {len(malicious_data)} rows, labels={malicious_data['_label'].unique().tolist() if '_label' in malicious_data.columns else 'NO _label COL'}")
except Exception as e:
    malicious_data = pd.DataFrame()
    print(f"[monitor] ERROR loading malicious_data: {e}")

ATTACK_LABEL_MAP = {
    "ddos": ["DDoS"],
    "portscan": ["PortScan"],
    "ssh": ["SSH-Patator"],
    "ftp": ["FTP-Patator"],
}

history: list[dict] = []
total_processed: int = 0
blocked_ips: set[str] = set()
benign_idx: int = 0


# ── Helpers ──────────────────────────────────────────────────────────────

def ingest_flow(row: pd.Series, source: str) -> dict | None:
    global total_processed, benign_idx
    src_ip = row.get("_src_ip", "N/A")
    if src_ip in blocked_ips:
        return None

    flow = {col: float(row.get(col, 0)) for col in feature_columns}
    result = predictor.predict(flow)
    conf = result["confidence"]
    is_anomaly = result["is_anomaly"] and conf >= 0.70

    entry = {
        "timestamp": datetime.now().isoformat(),
        "src_ip": src_ip,
        "dst_ip": row.get("_dst_ip", "N/A"),
        "src_port": random.randint(1024, 65535),
        "dst_port": int(row.get("_dst_port", 0)),
        "protocol": row.get("_protocol", "TCP"),
        "prediction": result["prediction"],
        "confidence": conf,
        "is_anomaly": is_anomaly,
        "total_packets": int(
            flow.get("Total Fwd Packets", 0) + flow.get("Total Backward Packets", 0)
        ),
        "total_bytes": int(
            flow.get("Total Length of Fwd Packets", 0)
            + flow.get("Total Length of Bwd Packets", 0)
        ),
        "flow_bytes_per_s": flow.get("Flow Bytes/s", 0),
        "source": source,
    }
    history.append(entry)
    if len(history) > 2000:
        del history[: len(history) - 2000]
    total_processed += 1
    return entry


def process_tick() -> list[dict]:
    global benign_idx
    demo = read_state()
    new_entries: list[dict] = []

    # Benign traffic
    if demo["benign_active"] and len(benign_data) > 0:
        speed = max(1, int(demo.get("benign_speed", 1)))
        for _ in range(speed):
            idx = benign_idx % len(benign_data)
            e = ingest_flow(benign_data.iloc[idx], "Traffic Simulator")
            if e:
                new_entries.append(e)
            benign_idx += 1

    # Continuous attacks
    attacks = demo.get("attacks", {})
    active_attacks = {k: v for k, v in attacks.items() if v}
    if active_attacks:
        print(f"[tick] Active attacks: {active_attacks}, malicious_data rows: {len(malicious_data)}")
    if len(malicious_data) > 0:
        for atk_key, is_on in attacks.items():
            if not is_on:
                continue
            labels = ATTACK_LABEL_MAP.get(atk_key, [])
            matching = malicious_data[malicious_data["_label"].isin(labels)]
            if len(matching) == 0:
                matching = malicious_data
            for _ in range(random.randint(2, 5)):
                row = matching.iloc[random.randint(0, len(matching) - 1)]
                e = ingest_flow(row, f"Attack: {atk_key.upper()}")
                if e:
                    new_entries.append(e)

    # One-shot bursts
    bursts = pop_bursts()
    if len(malicious_data) > 0:
        for burst in bursts:
            atk_type = burst.get("type", "ddos")
            count = burst.get("count", 1)
            labels = ATTACK_LABEL_MAP.get(atk_type, [])
            matching = malicious_data[malicious_data["_label"].isin(labels)]
            if len(matching) == 0:
                matching = malicious_data
            for _ in range(count):
                row = matching.iloc[random.randint(0, len(matching) - 1)]
                e = ingest_flow(row, f"Burst: {atk_type.upper()}")
                if e:
                    new_entries.append(e)

    return new_entries


# ── REST endpoints ───────────────────────────────────────────────────────

@router.get("/history")
def get_history(limit: int = 500):
    return history[-limit:]


@router.get("/stats")
def get_stats():
    df = pd.DataFrame(history[-500:]) if history else pd.DataFrame()
    has_data = len(df) > 0 and "is_anomaly" in df.columns
    anomalies = int(df["is_anomaly"].sum()) if has_data else 0
    threat_pct = (anomalies / len(df) * 100) if has_data and len(df) > 0 else 0
    avg_conf = float(df["confidence"].mean() * 100) if has_data else 0

    distribution: dict = {}
    if has_data:
        anomaly_df = df[df["is_anomaly"]]
        if len(anomaly_df) > 0:
            distribution = anomaly_df["prediction"].value_counts().to_dict()

    unique_src = int(df["src_ip"].nunique()) if has_data else 0
    unique_dst = int(df["dst_ip"].nunique()) if has_data else 0

    top_port = "-"
    if has_data and "dst_port" in df.columns and not df["dst_port"].mode().empty:
        top_port = str(int(df["dst_port"].mode().iloc[0]))

    avg_throughput = float(df["flow_bytes_per_s"].mean()) if has_data and "flow_bytes_per_s" in df.columns else 0

    return {
        "total_flows": total_processed,
        "anomalies": anomalies,
        "threat_pct": round(threat_pct, 1),
        "avg_confidence": round(avg_conf, 1),
        "blocked_count": len(blocked_ips),
        "blocked_ips": list(blocked_ips),
        "distribution": distribution,
        "unique_src": unique_src,
        "unique_dst": unique_dst,
        "top_port": top_port,
        "avg_throughput": round(avg_throughput, 0),
    }


@router.post("/block")
def block_ip_endpoint(body: dict):
    blocked_ips.add(body["ip"])
    return {"ok": True, "blocked": list(blocked_ips)}


@router.post("/unblock")
def unblock_ip_endpoint(body: dict):
    blocked_ips.discard(body["ip"])
    return {"ok": True, "blocked": list(blocked_ips)}


@router.post("/clear")
def clear_history():
    global total_processed
    history.clear()
    total_processed = 0
    return {"ok": True}


# ── WebSocket — real-time feed ───────────────────────────────────────────

@router.websocket("/ws")
async def ws_monitor(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            new_entries = []
            try:
                if any_active():
                    new_entries = process_tick()
            except Exception as e:
                print(f"[ws] process_tick error: {e}")

            try:
                demo = read_state()
                await ws.send_json({
                    "type": "tick",
                    "flows": new_entries[-20:],  # cap payload size
                    "state": demo,
                    "active": any_active(),
                })
            except Exception as e:
                print(f"[ws] send error: {e}")
                break

            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[ws] connection error: {e}")
