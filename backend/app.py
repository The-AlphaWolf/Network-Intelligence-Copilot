import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

app = FastAPI(title="Network Intelligence Copilot API")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = os.path.join(os.path.dirname(__file__), "synthetic_data.json")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"kpis": [], "logs": {}, "neighbors": {}}

data_store = load_data()

class InvestigateRequest(BaseModel):
    query: str
    cell_id: str

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "message": "Network Intelligence Copilot is running."}

@app.get("/api/v1/cells/{cell_id}/kpis")
def get_cell_kpis(cell_id: str):
    kpis = [k for k in data_store.get("kpis", []) if k.get("cell_id") == cell_id]
    if not kpis:
        raise HTTPException(status_code=404, detail="KPIs not found for cell")
    return {"cell_id": cell_id, "kpis": kpis}

@app.get("/api/v1/cells/{cell_id}/logs")
def search_network_logs(cell_id: str):
    logs = data_store.get("logs", {}).get(cell_id)
    if logs is None:
        raise HTTPException(status_code=404, detail="Logs not found for cell")
    return {"cell_id": cell_id, "logs": logs}

@app.get("/api/v1/cells/{cell_id}/neighbors")
def get_neighbor_cells(cell_id: str):
    neighbors = data_store.get("neighbors", {}).get(cell_id)
    if neighbors is None:
        raise HTTPException(status_code=404, detail="Neighbors not found for cell")
    return {"cell_id": cell_id, "neighbors": neighbors}

@app.post("/api/v1/investigate")
def investigate(req: InvestigateRequest):
    try:
        from backend.agents import investigate_incident
        result = investigate_incident(req.query, req.cell_id)
        
        # Parse LangGraph state to structured response
        return {
            "summary": "Investigation completed successfully.",
            "kpi_anomalies": result.get("kpis", ""),
            "evidence": result.get("logs", ""),
            "root_causes": result.get("root_cause", ""),
            "recommendations": result.get("recommendation", ""),
            "citations": result.get("rag_context", []),
            "agent_trace": result.get("trace", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
