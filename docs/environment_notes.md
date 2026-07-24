# ARC-AGI-3 Environment Specifications & Notes (Official Spec)

Understanding the underlying mechanics, observation structures, action taxonomy, and scoring system of ARC-AGI-3 interactive environments.

---

## 🎨 1. Palette & Color Representation (0–15)

ARC-AGI-3 grid observations use discrete integer values from `0` to `15` representing colors/states:

| Integer Value | Color Name | Hex Code | Visual Role |
|:---:|:---:|:---:|:---:|
| **0** | Black | `#000000` | Background / Void |
| **1** | Blue | `#0074D9` | Object / Primary |
| **2** | Red | `#FF4136` | Object / Target / Accent |
| **3** | Green | `#2ECC40` | Object / Success Indicator |
| **4** | Yellow | `#FFDC00` | Object / Key / Highlight |
| **5** | Gray | `#AAAAAA` | Wall / Obstacle / Neutral |
| **6** | Magenta | `#F012BE` | Object / Special |
| **7** | Orange | `#FF851B` | Object / Special |
| **8** | Teal | `#7FDBFF` | Object / Secondary |
| **9** | Maroon | `#870E25` | Object / Border |
| **10** | Lavender | `#B10DC9` | Extended Palette |
| **11** | Lime | `#01FF70` | Extended Palette |
| **12** | Navy | `#001F3F` | Extended Palette |
| **13** | Olive | `#3D9970` | Extended Palette |
| **14** | Coral | `#FF7F50` | Extended Palette |
| **15** | Gold | `#DAA520` | Extended Palette |

---

## 📦 2. Observation Payload (Frame JSON Schema)

When the agent observes the environment state at step `t`, the returned dictionary follows this official schema:

```json
{
  "game_id": "sample_game",
  "step": 12,
  "frame": [
    [0, 0, 1, 0, 0],
    [0, 2, 2, 2, 0],
    [0, 0, 1, 0, 0]
  ],
  "grid_shape": [3, 5],
  "available_actions": ["RESET", "ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION6"],
  "status": "NOT_FINISHED",
  "reward": 0.0,
  "diff_cells": 4,
  "timestamp": 1721820000.0
}
```

### Key Observation Fields:
- **`game_id`**: Unique string identifier for the environment instance.
- **`step`**: Current step counter in the episode.
- **`frame`**: 2D array of integers `[height, width]` containing cell values `0–15` (max 64×64).
- **`grid_shape`**: Tuple `(height, width)`.
- **`available_actions`**: List of valid action tokens available in the current state.
- **`status`**: Current game status (`"NOT_FINISHED"`, `"WIN"`, or `"GAME_OVER"`).
- **`reward`**: Cumulative or step reward.
- **`diff_cells`**: Count of modified grid cells relative to the previous step frame.

---

## 🕹️ 3. Abstract Action Taxonomy

The meaning of actions varies per game. Actions are treated as abstract tokens until their semantics are inferred by hypothesis engines:

- **`RESET`**: Start or restart the game environment.
- **`ACTION1` – `ACTION5`**: Simple discrete environment interactions (movement, toggling, pushing).
- **`ACTION6`**: Complex interactive action requiring `(x, y)` grid coordinates.
- **`ACTION7`**: Additional simple interaction.

---

## 🏆 4. Official Competition Scoring & Efficiency

For each level completed, the agent's action count is evaluated against a human test-tester baseline:

$$\text{Per-Level Score} = \min\left(\frac{\text{Human Actions}}{\text{Agent Actions}}, 1.0\right)^2$$

- **Per-Game Score**: Weighted average of level scores (weighted by 1-indexed level index).
- **Total Benchmark Score**: Average of all individual game scores (0% to 100%).
