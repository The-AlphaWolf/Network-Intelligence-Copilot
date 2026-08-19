import json
import random
from datetime import datetime, timedelta

def generate_kpis(cell_id, scenario="normal"):
    base_kpis = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cell_id": cell_id,
        "rsrp_dbm": random.uniform(-95, -75),
        "rsrq_db": random.uniform(-15, -10),
        "sinr_db": random.uniform(10, 20),
        "latency_ms": random.uniform(10, 25),
        "packet_loss_percent": random.uniform(0, 0.1),
        "throughput_mbps": random.uniform(150, 400),
        "prb_utilization_percent": random.uniform(30, 60),
        "handover_success_rate": random.uniform(98, 100),
        "drop_rate_percent": random.uniform(0.1, 0.5),
        "active_users": int(random.uniform(50, 200))
    }

    if scenario == "congestion":
        base_kpis["prb_utilization_percent"] = random.uniform(90, 99)
        base_kpis["latency_ms"] = random.uniform(100, 250)
        base_kpis["packet_loss_percent"] = random.uniform(2, 5)
        base_kpis["throughput_mbps"] = random.uniform(10, 50)
        base_kpis["active_users"] = int(random.uniform(400, 600))
    elif scenario == "interference":
        base_kpis["rsrp_dbm"] = random.uniform(-110, -95)
        base_kpis["sinr_db"] = random.uniform(-5, 5)
        base_kpis["drop_rate_percent"] = random.uniform(3, 8)
        base_kpis["throughput_mbps"] = random.uniform(5, 20)
    elif scenario == "handover_problem":
        base_kpis["handover_success_rate"] = random.uniform(70, 85)
        base_kpis["drop_rate_percent"] = random.uniform(2, 5)
    elif scenario == "backhaul_degradation":
        base_kpis["latency_ms"] = random.uniform(300, 500)
        base_kpis["packet_loss_percent"] = random.uniform(5, 10)
        base_kpis["throughput_mbps"] = random.uniform(1, 10)

    return base_kpis

def generate_logs(cell_id, scenario="normal"):
    logs = []
    base_time = datetime.utcnow() - timedelta(minutes=60)
    
    if scenario == "normal":
        logs.append(f"{base_time.isoformat()} [INFO] {cell_id} - Cell operating normally.")
    elif scenario == "congestion":
        logs.append(f"{base_time.isoformat()} [WARN] {cell_id} - High PRB utilization detected.")
        logs.append(f"{(base_time + timedelta(minutes=15)).isoformat()} [ERROR] {cell_id} - Admission control rejected 45 connections.")
    elif scenario == "interference":
        logs.append(f"{base_time.isoformat()} [WARN] {cell_id} - High UL RSSI detected.")
        logs.append(f"{(base_time + timedelta(minutes=20)).isoformat()} [ERROR] {cell_id} - Radio link failure count exceeded threshold.")
    elif scenario == "handover_problem":
        logs.append(f"{base_time.isoformat()} [WARN] {cell_id} - Too many X2 handover preparation failures with neighbor BLR-5G-089.")
    elif scenario == "backhaul_degradation":
        logs.append(f"{base_time.isoformat()} [WARN] {cell_id} - S1 interface latency spike.")
        logs.append(f"{(base_time + timedelta(minutes=10)).isoformat()} [ERROR] {cell_id} - SCTP heartbeat failure on transport network.")

    return logs

if __name__ == "__main__":
    cells = {
        "KOL-5G-017": "backhaul_degradation",
        "DEL-5G-042": "interference",
        "BLR-5G-088": "handover_problem",
        "MUM-5G-101": "normal",
        "CHE-5G-200": "congestion"
    }

    data = {
        "kpis": [],
        "logs": {},
        "neighbors": {
            "KOL-5G-017": ["KOL-5G-018", "KOL-5G-019"],
            "DEL-5G-042": ["DEL-5G-043"],
            "BLR-5G-088": ["BLR-5G-089", "BLR-5G-090"],
            "MUM-5G-101": ["MUM-5G-102"],
            "CHE-5G-200": ["CHE-5G-201"]
        }
    }

    for cell_id, scenario in cells.items():
        data["kpis"].append(generate_kpis(cell_id, scenario))
        data["logs"][cell_id] = generate_logs(cell_id, scenario)

    with open("synthetic_data.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Generated synthetic_data.json")
