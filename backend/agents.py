from typing import TypedDict, Annotated, Sequence, List, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from backend.rag import search_knowledge_base
import os
import json

DATA_FILE = os.path.join(os.path.dirname(__file__), "synthetic_data.json")

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"kpis": [], "logs": {}, "neighbors": {}}

data_store = load_data()

# Tools (simulated as functions for now)
def get_cell_kpis(cell_id: str) -> str:
    kpis = [k for k in data_store.get("kpis", []) if k.get("cell_id") == cell_id]
    if not kpis:
        return f"No KPIs found for {cell_id}"
    return json.dumps(kpis[0])

def search_network_logs(cell_id: str) -> str:
    logs = data_store.get("logs", {}).get(cell_id)
    if logs is None:
        return f"No logs found for {cell_id}"
    return "\n".join(logs)

# LangGraph State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    cell_id: str
    kpis: str
    logs: str
    rag_context: List[Dict[str, str]]
    root_cause: str
    recommendation: str
    trace: List[str]

# Initialize Gemini Model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.1)

def network_analyst(state: AgentState):
    cell_id = state.get("cell_id")
    state["trace"].append("Network Analyst: Retrieving KPIs and Logs...")
    kpis = get_cell_kpis(cell_id)
    logs = search_network_logs(cell_id)
    
    analysis_prompt = f"Analyze these KPIs and Logs for {cell_id}.\nKPIs: {kpis}\nLogs: {logs}\nWhat are the anomalies?"
    response = llm.invoke([HumanMessage(content=analysis_prompt)])
    
    return {"kpis": kpis, "logs": logs, "messages": [AIMessage(content=response.content, name="NetworkAnalyst")], "trace": ["Network Analyst completed analysis."]}

def rag_agent(state: AgentState):
    state["trace"].append("RAG Agent: Searching knowledge base for context...")
    query = "anomalies in " + state["cell_id"]
    if len(state["messages"]) > 0:
        query = state["messages"][-1].content[:100]
        
    context = search_knowledge_base(query)
    
    context_str = json.dumps(context)
    response = llm.invoke([HumanMessage(content=f"Summarize the relevant operating procedures based on this context: {context_str}")])
    
    return {"rag_context": context, "messages": [AIMessage(content=response.content, name="RAGAgent")], "trace": ["RAG Agent retrieved documentation."]}

def root_cause_agent(state: AgentState):
    state["trace"].append("Root Cause Agent: Determining root cause...")
    prompt = f"""
    Based on the following data:
    KPIs: {state.get('kpis')}
    Logs: {state.get('logs')}
    Knowledge Base: {state.get('rag_context')}
    
    Determine the most likely root cause. Provide a concise explanation and a confidence level (e.g., 90%).
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"root_cause": response.content, "messages": [AIMessage(content=response.content, name="RootCauseAgent")], "trace": ["Root Cause Agent identified cause."]}

def resolution_agent(state: AgentState):
    state["trace"].append("Resolution Agent: Formulating recommendations...")
    prompt = f"""
    The root cause identified is: {state.get('root_cause')}
    Based on the SOPs: {state.get('rag_context')}
    
    Recommend actionable remediation steps.
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"recommendation": response.content, "messages": [AIMessage(content=response.content, name="ResolutionAgent")], "trace": ["Resolution Agent generated recommendations."]}

def supervisor(state: AgentState):
    # A simple sequential router for MVP
    # Analyst -> RAG -> Root Cause -> Resolution -> END
    last_message = state["messages"][-1] if state["messages"] else None
    
    if not last_message or last_message.name not in ["NetworkAnalyst", "RAGAgent", "RootCauseAgent", "ResolutionAgent"]:
        return "network_analyst"
    elif last_message.name == "NetworkAnalyst":
        return "rag_agent"
    elif last_message.name == "RAGAgent":
        return "root_cause_agent"
    elif last_message.name == "RootCauseAgent":
        return "resolution_agent"
    else:
        return "__end__"

# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("network_analyst", network_analyst)
workflow.add_node("rag_agent", rag_agent)
workflow.add_node("root_cause_agent", root_cause_agent)
workflow.add_node("resolution_agent", resolution_agent)

workflow.set_conditional_entry_point(
    supervisor,
    {
        "network_analyst": "network_analyst",
        "rag_agent": "rag_agent",
        "root_cause_agent": "root_cause_agent",
        "resolution_agent": "resolution_agent",
        "__end__": END
    }
)
workflow.add_edge("network_analyst", "rag_agent")
workflow.add_edge("rag_agent", "root_cause_agent")
workflow.add_edge("root_cause_agent", "resolution_agent")
workflow.add_edge("resolution_agent", END)

app = workflow.compile()

def investigate_incident(query: str, cell_id: str):
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "cell_id": cell_id,
        "kpis": "",
        "logs": "",
        "rag_context": [],
        "root_cause": "",
        "recommendation": "",
        "trace": ["Supervisor initiated investigation."]
    }
    
    final_state = app.invoke(initial_state)
    return final_state
