import streamlit as st
import time
import numpy as np
import traceback

st.set_page_config(page_title="ARC-AGI Copilot", layout="wide")

# ARC Colors
COLOR_MAP = {
    0: "#000000", 1: "#0074D9", 2: "#FF4136", 3: "#2ECC40",
    4: "#FFDC00", 5: "#AAAAAA", 6: "#F012BE", 7: "#FF851B",
    8: "#7FDBFF", 9: "#85144b", 10: "#39CCCC", 11: "#3D9970", 12: "#B10DC9"
}

def render_grid_html(grid, cell_size=15):
    """Render a NumPy array grid as an HTML table for Streamlit."""
    if isinstance(grid, list):
        grid = np.array(grid)
    if hasattr(grid, 'ndim') and grid.ndim == 3:
        grid = np.max(grid, axis=0) # Flatten layers
        
    html = f"<div style='max-width: 100%; overflow-x: auto;'><table style='border-collapse: collapse; margin: auto;'>"
    for row in grid:
        html += "<tr>"
        for val in row:
            color = COLOR_MAP.get(int(val), "#FFFFFF")
            html += f"<td style='width: {cell_size}px; height: {cell_size}px; background-color: {color}; border: 1px solid #555;'></td>"
        html += "</tr>"
    html += "</table></div>"
    return html

def scene_graph_to_grid(scene_graph, grid_shape=(30, 30)):
    """Convert a SceneGraph back to a numpy grid for visualization."""
    grid = np.zeros(grid_shape, dtype=int)
    if not scene_graph: return grid
    for obj in scene_graph.objects.values():
        for r, c in obj.pixels:
            if 0 <= r < grid_shape[0] and 0 <= c < grid_shape[1]:
                grid[r, c] = obj.color
    return grid

def init_game():
    from benchmark.config import DEFAULT_GAMES
    from agents.cognitive_agent import CognitiveAgent
    try:
        import arc_agi
        st.session_state.arc = arc_agi.Arcade()
        st.session_state.game_id = "ls20"
        st.session_state.env = st.session_state.arc.make(st.session_state.game_id, render_mode=None)
    except Exception as e:
        st.error(f"Failed to load environment: {e}")
        st.stop()
        
    st.session_state.agent = CognitiveAgent(name="CognitiveAgent")
    st.session_state.agent.reset()
    st.session_state.obs = st.session_state.env.reset()
    st.session_state.frames = [get_obs_dict(st.session_state.obs)]
    st.session_state.step_count = 0
    st.session_state.running_ai = False
    st.session_state.last_error = None

def get_obs_dict(obs):
    if isinstance(obs, dict): return obs
    d = {"frame": getattr(obs, "frame", []), "available_actions": getattr(obs, "available_actions", [])}
    if hasattr(obs, "state"):
        state_val = getattr(obs, "state")
        d["status"] = getattr(state_val, "value", str(state_val))
    return d

if "env" not in st.session_state:
    init_game()

st.title("🧠 ARC-AGI Copilot: Cognitive Game Intelligence")
st.markdown("Play manually (W/A/S/D) to teach the agent, or let the AI take over using Model-Based Planning.")

# Sidebar Controls
with st.sidebar:
    st.header("🎮 Control Panel")
    
    if st.button("🔄 Reset Environment"):
        init_game()
        st.rerun()
        
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Run AI"):
            st.session_state.running_ai = True
            st.rerun()
    with col2:
        if st.button("⏸ Pause AI"):
            st.session_state.running_ai = False
            st.rerun()
            
    if st.button("⏭ Next AI Step"):
        st.session_state.force_step = True
    else:
        st.session_state.force_step = False
        
    st.divider()
    st.markdown("### 🕹️ Human Manual Control")
    st.markdown("Agent learns from your actions!")
    
    col_w1, col_w2, col_w3 = st.columns([1,2,1])
    with col_w2:
        btn_up = st.button("W (Up)", use_container_width=True)
    col_a1, col_a2, col_a3 = st.columns([1,1,1])
    with col_a1:
        btn_left = st.button("A (Left)", use_container_width=True)
    with col_a2:
        btn_down = st.button("S (Down)", use_container_width=True)
    with col_a3:
        btn_right = st.button("D (Right)", use_container_width=True)
        
    human_action = None
    if btn_up: human_action = "ACTION3"
    elif btn_down: human_action = "ACTION4"
    elif btn_left: human_action = "ACTION1"
    elif btn_right: human_action = "ACTION2"

# Main Logic loop
agent = st.session_state.agent
env = st.session_state.env
obs = st.session_state.obs
frames = st.session_state.frames
obs_dict = get_obs_dict(obs)

status = obs_dict.get("status")
if status in ["WIN", "GAME_OVER"] or agent.is_done(frames, obs_dict):
    st.session_state.running_ai = False
    st.balloons() if status == "WIN" else None
    st.success(f"Game Finished! Status: {status}")

elif st.session_state.running_ai or st.session_state.force_step or human_action:
    try:
        from arcengine import GameAction
        
        # Determine internal action
        action_intent = agent.choose_action(frames, obs_dict, human_action=human_action)
        
        # Translate to game action
        if isinstance(action_intent, tuple) and len(action_intent) == 3:
            action_name, x, y = action_intent
            game_action = getattr(GameAction, action_name, GameAction.ACTION1)
            data = {"x": x, "y": y}
        else:
            action_name = str(action_intent)
            game_action = getattr(GameAction, action_name, GameAction.ACTION1)
            data = None
            
        # Step env
        st.session_state.obs = env.step(game_action, data=data)
        st.session_state.frames.append(get_obs_dict(st.session_state.obs))
        st.session_state.step_count += 1
        
        if st.session_state.running_ai:
            time.sleep(0.5)
            st.rerun()
            
    except Exception as e:
        st.session_state.running_ai = False
        st.session_state.last_error = traceback.format_exc()

# Layout
col_left, col_right = st.columns([1, 1.5])

with col_left:
    st.markdown(f"**Step:** {st.session_state.step_count} | **Status:** {obs_dict.get('status', 'RUNNING')}")
    grid = obs_dict.get("frame", obs_dict.get("grid", []))
    grid_shape = (len(grid), len(grid[0])) if len(grid) > 0 else (30, 30)
    st.write(render_grid_html(grid, cell_size=18), unsafe_allow_html=True)
    
    if st.session_state.last_error:
        st.error(st.session_state.last_error)
        
    st.divider()
    st.subheader("📊 Live Metrics")
    m1, m2, m3 = st.columns(3)
    
    acc = 0.0
    if hasattr(agent, 'prediction_engine') and agent.prediction_engine.total_predictions > 0:
        acc = (agent.prediction_engine.correct_predictions / agent.prediction_engine.total_predictions) * 100
        
    states = len(agent.memory_agent.memory.episodic.visit_counts) if hasattr(agent, 'memory_agent') else 0
    rules = len(agent.hypothesis_agent.engine.get_verified_hypotheses()) if hasattr(agent, 'hypothesis_agent') else 0
    
    m1.metric("Prediction Acc", f"{acc:.1f}%")
    m2.metric("Unique States", states)
    m3.metric("Rules Learned", rules)
    
    st.divider()
    st.subheader("🧠 Episodic Memory")
    if hasattr(agent, 'memory_agent'):
        history = agent.memory_agent.memory.episodic.action_history
        if history:
            for i, h in enumerate(history[-5:]): # Show last 5
                st.caption(f"**Step {len(history)-5+i if len(history)>5 else i}:** {h.get('action', 'N/A')} (Reward: {h.get('reward', 0)})")
        else:
            st.caption("Memory is empty.")

with col_right:
    st.subheader("⚙️ Cognitive Pipeline")
    
    # Retrieve Traces for the current step
    latest_step = agent.blackboard.current_step
    step_traces = [t for t in agent.trace_log.traces if t["step"] == latest_step]
    
    if step_traces:
        emoji_map = {
            "PerceptionAgent": ("👁️ Observe", "#e3f2fd"),
            "MemoryAgent": ("🧠 Remember", "#f3e5f5"),
            "HypothesisAgent": ("💡 Hypothesize", "#fff9c4"),
            "CriticAgent": ("⚖️ Critic", "#ffebee"),
            "PlannerAgent": ("🗺️ Plan", "#e8f5e9"),
            "ExecutorAgent": ("⚡ Act", "#fff3e0"),
            "HumanController": ("👤 Human", "#eceff1")
        }
        
        for trace in step_traces:
            agent_name = trace["agent"]
            reasoning = trace.get("reasoning", [])
            title, bg_color = emoji_map.get(agent_name, ("🤖 " + agent_name, "#f5f5f5"))
            
            # Stylized Agent Thought Box
            st.markdown(f"""
            <div style="background-color: {bg_color}; padding: 10px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #888;">
                <strong style="color: #333;">{title}</strong><br/>
                <span style="color: #444; font-size: 0.95em;">
                {"<br/>".join(reasoning) if isinstance(reasoning, list) else reasoning}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            # If Planner just ran, show the prediction view
            if agent_name == "PlannerAgent" and agent.blackboard.plans.get("selected_action"):
                current_scene = agent.blackboard.observations.get("current_scene")
                action = agent.blackboard.plans.get("selected_action")
                if current_scene and hasattr(agent, 'hypothesis_agent'):
                    pred = agent.hypothesis_agent.prediction_engine.evaluate_action(current_scene, action)
                    pred_grid = scene_graph_to_grid(pred.predicted_state, grid_shape=grid_shape)
                    
                    st.markdown("**🔮 Predicted Future State (World Model)**")
                    pc1, pc2, pc3 = st.columns([1, 0.2, 1])
                    with pc1:
                        st.caption("Current")
                        st.write(render_grid_html(grid, cell_size=8), unsafe_allow_html=True)
                    with pc2:
                        st.markdown("<div style='text-align: center; margin-top: 30px;'>➡️</div>", unsafe_allow_html=True)
                    with pc3:
                        st.caption(f"After {action}")
                        st.write(render_grid_html(pred_grid, cell_size=8), unsafe_allow_html=True)
                    st.markdown("<br/>", unsafe_allow_html=True)
                    
    else:
        st.info("Agent is idle. Press a manual control button or 'Run AI'.")

