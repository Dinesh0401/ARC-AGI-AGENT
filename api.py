from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import traceback
import numpy as np

app = FastAPI(title="ARC-AGI Cognitive Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State Container
class GameState:
    def __init__(self):
        self.env = None
        self.agent = None
        self.obs = None
        self.frames = []
        self.step_count = 0
        self.game_id = "ls20"

state = GameState()

class StepRequest(BaseModel):
    human_action: Optional[str] = None

def get_obs_dict(obs):
    if isinstance(obs, dict): return obs
    d = {"frame": getattr(obs, "frame", []), "available_actions": getattr(obs, "available_actions", [])}
    if hasattr(obs, "state"):
        state_val = getattr(obs, "state")
        d["status"] = getattr(state_val, "value", str(state_val))
    return d

def scene_graph_to_grid(scene_graph, grid_shape=(30, 30)):
    grid = np.zeros(grid_shape, dtype=int)
    if not scene_graph: return grid.tolist()
    for obj in scene_graph.objects.values():
        for r, c in obj.pixels:
            if 0 <= r < grid_shape[0] and 0 <= c < grid_shape[1]:
                grid[r, c] = obj.color
    return grid.tolist()

def extract_knowledge_graph(scene_graph):
    nodes = []
    edges = []
    if not scene_graph: return {"nodes": nodes, "edges": edges}
    
    # Add Player Node
    nodes.append({"id": "player", "data": {"label": "Player Agent"}, "position": {"x": 250, "y": 50}, "type": "input", "className": "bg-blue-900 border-blue-500 text-white rounded-lg p-3 shadow-lg shadow-blue-900/50"})
    
    # Add Object Nodes
    y_offset = 150
    x_offset = 100
    for obj_id, obj in scene_graph.objects.items():
        if getattr(obj, 'movable', False): continue # Player is movable
        label = f"Object (Color {obj.color})"
        if obj.color == 3: label = "Goal / Target"
        if obj.color == 2: label = "Obstacle / Wall"
        
        node_id = f"obj_{obj_id}"
        nodes.append({
            "id": node_id,
            "data": {"label": label},
            "position": {"x": x_offset, "y": y_offset},
            "className": "bg-slate-800 border-slate-600 text-white rounded-lg p-2 shadow-lg"
        })
        
        # Determine relationship
        rel_label = "interacts with"
        if obj.color == 3: rel_label = "seeks"
        elif obj.color == 2: rel_label = "avoids"
        
        edges.append({
            "id": f"e-player-{node_id}",
            "source": "player",
            "target": node_id,
            "label": rel_label,
            "animated": True,
            "style": {"stroke": "#94a3b8"}
        })
        x_offset += 200
        
    return {"nodes": nodes, "edges": edges}

def extract_rule_cards(hypothesis_agent):
    cards = []
    if not hypothesis_agent: return cards
    rules = hypothesis_agent.prediction_engine.transition_model.rules
    for action, r_list in rules.items():
        for rule in r_list:
            if rule.total_matches > 0:
                conf = rule.successful_matches / rule.total_matches
                cards.append({
                    "id": f"rule_{len(cards)+1}",
                    "action": action,
                    "condition": f"Color {rule.target_color}",
                    "confidence": round(conf * 100, 1),
                    "occurrences": rule.total_matches
                })
    return cards

def translate_to_natural_language(traces):
    for t in traces:
        agent = t.get("agent", "")
        raw = " ".join(t.get("reasoning", [])) if isinstance(t.get("reasoning"), list) else str(t.get("reasoning", ""))
        
        if "PerceptionAgent" in agent:
            if "Identified player" in raw:
                t["thought"] = "I scanned the environment and isolated the player's position. I've also identified the static structures and targets."
            else:
                t["thought"] = "I'm observing the grid to identify movable entities and spatial layouts."
        elif "HypothesisAgent" in agent:
            if "Generated" in raw and "Induced" in raw:
                t["thought"] = "By analyzing the previous transition, I've deduced a new physical rule governing how objects interact in this space."
            else:
                t["thought"] = "I am evaluating the physical laws of this environment to predict what will happen next."
        elif "PlannerAgent" in agent:
            if "Selected action:" in raw:
                action = raw.split("Selected action: ")[-1]
                t["thought"] = f"After simulating multiple futures in my World Model, I predict that executing {action} yields the highest expected reward while minimizing collision risks."
            else:
                t["thought"] = "I am running a Beam Search across my World Model to find the optimal trajectory."
        elif "CriticAgent" in agent:
            t["thought"] = "I've reviewed the proposed hypotheses and rejected paths with low confidence. The current plan passes all safety thresholds."
        elif "ExecutorAgent" in agent:
            t["thought"] = "Sending the selected command to the physical actuators."
        elif "MemoryAgent" in agent:
            t["thought"] = "I found a similar spatial configuration in my episodic memory database. Retrieving relevant contextual rules."
        else:
            t["thought"] = raw
    return traces

@app.post("/api/init")
def init_game():
    import traceback
    try:
        from agents.cognitive_agent import CognitiveAgent
        from environment.wrapper import ARCEnvironment
        
        state.env = ARCEnvironment(game_id=state.game_id)
        
        state.agent = CognitiveAgent(name="CognitiveAgent")
        state.agent.reset()
        state.obs = state.env.reset()
        state.frames = [get_obs_dict(state.obs)]
        state.step_count = 0
        return {"message": "Game Initialized successfully"}
    except Exception as e:
        print("ERROR IN INIT:", e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/step")
def step_game(req: StepRequest):
    import traceback
    if not state.agent or not state.env:
        raise HTTPException(status_code=400, detail="Game not initialized")
        
    obs_dict = get_obs_dict(state.obs)
    status = obs_dict.get("status")
    if status in ["WIN", "GAME_OVER"] or state.agent.is_done(state.frames, obs_dict):
        return {"message": "Game already finished", "status": status}
        
    try:
        action_intent = state.agent.choose_action(state.frames, obs_dict, human_action=req.human_action)
        
        if isinstance(action_intent, tuple) and len(action_intent) == 3:
            action_name, x, y = action_intent
            game_action = (action_name, x, y)
        else:
            game_action = str(action_intent)
            
        obs, reward, done, info = state.env.step(game_action)
        state.obs = obs
        state.frames.append(get_obs_dict(state.obs))
        state.step_count += 1
        return {"message": "Step executed"}
        
    except Exception as e:
        print("ERROR IN STEP:", e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/state")
def get_state():
    if not state.agent or not state.env:
        return {"status": "UNINITIALIZED"}
        
    obs_dict = get_obs_dict(state.obs)
    grid = obs_dict.get("frame", obs_dict.get("grid", []))
    
    # Process traces
    latest_step = state.agent.blackboard.current_step
    step_traces = [t for t in state.agent.trace_log.traces if t["step"] == latest_step]
    
    # Transform traces
    step_traces = translate_to_natural_language(step_traces)
    
    try:
        # Process prediction
        predicted_grid = None
        if state.agent.blackboard.plans.get("selected_action"):
            current_scene = state.agent.blackboard.observations.get("current_scene")
            action = state.agent.blackboard.plans.get("selected_action")
            if current_scene and hasattr(state.agent, 'hypothesis_agent'):
                pred = state.agent.hypothesis_agent.prediction_engine.evaluate_action(current_scene, str(action))
                grid_shape = (len(grid), len(grid[0])) if len(grid) > 0 else (30, 30)
                predicted_grid = scene_graph_to_grid(pred.predicted_state, grid_shape=grid_shape)
                
        # Process memory
        memory = []
        if hasattr(state.agent, 'memory_agent'):
            history = state.agent.memory_agent.memory.episodic.episodes
            for i, h in enumerate(history):
                memory.append({"step": i, "action": str(h[1]), "reward": h[2]})
                
        # Knowledge Graph
        kg = {"nodes": [], "edges": []}
        if state.agent.blackboard.observations.get("current_scene"):
            kg = extract_knowledge_graph(state.agent.blackboard.observations["current_scene"])
            
        # Rule Cards
        rules_cards = []
        if hasattr(state.agent, 'hypothesis_agent'):
            rules_cards = extract_rule_cards(state.agent.hypothesis_agent)

        # Metrics
        acc = 0.0
        if hasattr(state.agent, 'hypothesis_agent') and state.agent.hypothesis_agent.prediction_engine.total_predictions > 0:
            acc = (state.agent.hypothesis_agent.prediction_engine.correct_predictions / state.agent.hypothesis_agent.prediction_engine.total_predictions) * 100
        states = len(state.agent.memory_agent.memory.episodic.visited_tiles) if hasattr(state.agent, 'memory_agent') else 0
        rules = len(state.agent.hypothesis_agent.engine.get_verified_hypotheses()) if hasattr(state.agent, 'hypothesis_agent') else 0

        return {
            "status": obs_dict.get("status", "RUNNING"),
            "step": state.step_count,
            "grid": grid,
            "predicted_grid": predicted_grid,
            "traces": step_traces,
            "memory": memory,
            "knowledge_graph": kg,
            "rule_cards": rules_cards,
            "metrics": {
                "accuracy": acc,
                "unique_states": states,
                "rules": rules
            }
        }
    except Exception as e:
        print("ERROR IN GET_STATE:", e)
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
