import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ARC-AGI Control Center", layout="wide")

# Paths
TRACE_FILE = "trace.json"

st.title("🧠 Neuro-Symbolic Cognitive Architecture for ARC-AGI")
st.markdown("### Live Agent Control Center")

def load_traces():
    if os.path.exists(TRACE_FILE):
        try:
            with open(TRACE_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

traces = load_traces()

if not traces:
    st.info("Waiting for agent execution... Run `python main.py` in another terminal.")
    st.stop()

# Get latest step
latest_step = max([t.get("step", 0) for t in traces])
step_traces = [t for t in traces if t.get("step") == latest_step]

col1, col2 = st.columns([1, 1])

with col1:
    st.header("1. Environment State")
    st.markdown(f"**Current Step:** {latest_step}")
    
    # We try to extract grid size or object counts from perception
    perception_trace = next((t for t in step_traces if t["agent"] == "PerceptionAgent"), None)
    if perception_trace:
        st.success("Grid Active & Monitored")
        st.write(perception_trace["reasoning"])
    else:
        st.warning("Awaiting Perception data...")

    st.header("4. Task Completion Metrics")
    # Get metrics from Planner or Hypothesis agent
    latest_metrics = {}
    for t in traces:
        if "metrics" in t and isinstance(t["metrics"], dict):
            latest_metrics.update(t["metrics"])
            
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Prediction Error", f"{latest_metrics.get('error', 0.0):.2f}")
        st.metric("States Explored", latest_metrics.get('states_explored', 0))
    with col_m2:
        st.metric("Hypotheses Generated", latest_metrics.get('hypotheses', 0))
        st.metric("Planner Success Rate", f"{latest_metrics.get('planner_success_rate', 0.0)*100:.1f}%")

with col2:
    st.header("2. Agent Status")
    
    expected_agents = [
        "PerceptionAgent", "MemoryAgent", "GoalAgent", 
        "HypothesisAgent", "WorldModelAgent", "CriticAgent", 
        "PlannerAgent", "ExecutorAgent"
    ]
    
    executed_agents = {t["agent"] for t in step_traces}
    
    for agent in expected_agents:
        if agent in executed_agents:
            st.markdown(f"✅ **{agent}** - *Executed*")
        else:
            st.markdown(f"⏳ **{agent}** - *Waiting*")

    st.header("5. Knowledge Base")
    with st.expander("Semantic Memory Contents", expanded=False):
        st.markdown("**Entities tracked:**")
        # Extract from memory trace if available
        memory_trace = next((t for t in step_traces if t["agent"] == "MemoryAgent"), None)
        if memory_trace:
            st.json(memory_trace.get("reasoning", []))
        else:
            st.write("Awaiting memory sync...")
            
    with st.expander("Rule Statistics", expanded=False):
        rules_verified = latest_metrics.get("rules_verified", 0)
        rules_rejected = latest_metrics.get("rejected_count", 0)
        st.metric("Total Rules Inducted & Verified", rules_verified)
        st.metric("Rules Pruned by Critic", rules_rejected)

st.divider()
st.header("3. Reasoning Pipeline")

for trace in step_traces:
    agent_name = trace["agent"]
    action = trace.get("action", "Run")
    conf = trace.get("confidence", 1.0)
    reasoning = trace.get("reasoning", [])
    
    with st.expander(f"{agent_name}: {action} (Confidence: {conf:.2f})", expanded=True):
        if isinstance(reasoning, list):
            for r in reasoning:
                st.markdown(f"- {r}")
        else:
            st.write(reasoning)
        
        metrics = trace.get("metrics")
        if metrics:
            st.json(metrics)

# Auto-refresh logic (Using Streamlit's built-in autorefresh workaround)
import time
time.sleep(1)
st.rerun()
