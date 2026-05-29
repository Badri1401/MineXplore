# RL Training Guide - Mining Environment

## Quick Start

```bash
cd ~/mining_env_dataset_folder
source Mining\ Env/.venv/bin/activate
python rl_training.py
```

This runs 30,000 episodes with default parameters. Results are saved to `Mining Env/outputs/trial_runs/`.

---

## File Location

**Script:** `~/mining_env_dataset_folder/rl_training.py`

**Run from:** `~/mining_env_dataset_folder/` (or any directory, it will find Mining Env/)

---

## Parameters

```bash
python rl_training.py [OPTIONS]
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--episodes` | 30000 | Total episodes to run |
| `--num-agents` | 1 | Agents per episode |
| `--max-steps` | 6000 | Max steps per episode |
| `--policy` | explore | Policy: `explore` (wall-avoid) or `random` |
| `--print-every` | 10 | Print summary every N episodes |
| `--plot-every` | 5000 | Update plots every N episodes |
| `--summary-window` | 100 | Rolling window size for stats |
| `--run-dir` | outputs/trial_runs | Output directory path |
| `--seed` | 42 | Random seed |

---

## Examples

### Run with default settings (30k episodes)
```bash
python rl_training.py
```

### Quick test (100 episodes)
```bash
python rl_training.py --episodes 100 --max-steps 500
```

### Custom output directory
```bash
python rl_training.py --run-dir my_results --episodes 5000
```

### Random policy instead of explore
```bash
python rl_training.py --policy random
```

### Print more frequently
```bash
python rl_training.py --print-every 5 --plot-every 1000
```

---

## Output Files

Results are saved to: `Mining Env/outputs/trial_runs/trial_YYYYMMDD_HHMMSS/`

```
trial_20260410_163209/
├── episode_metrics.csv      # 23 columns × N episodes
├── summary.json             # Aggregated statistics
├── plots/
│   ├── trends/
│   │   ├── reward_total.png
│   │   ├── reward_per_step.png
│   │   ├── coverage_fraction.png
│   │   ├── coverage_auc.png
│   │   ├── episode_length.png
│   │   ├── new_cells_total.png
│   │   └── collision_steps.png
│   └── rates/
│       ├── milestone_25_rate.png
│       ├── milestone_50_rate.png
│       ├── milestone_75_rate.png
│       └── timeout_rate.png
└── tensorboard/
    └── events.out.tfevents.* (TensorBoard logs)
```

### CSV Columns (episode_metrics.csv)

1. `episode` - Episode number
2. `reward_total` - Total reward earned
3. `reward_per_step` - Average reward per step
4. `episode_length` - Steps taken
5. `max_steps_budget` - Max allowed steps
6. `budget_utilization` - (steps / max_steps)
7. `coverage_fraction` - Final coverage [0-1]
8. `coverage_auc` - Area under coverage curve
9. `cells_seen_count` - Total cells visited
10. `total_tunnel_cells` - Total cells in environment
11. `new_cells_total` - New cells discovered
12. `avg_new_cells_per_step` - Discovery rate
13. `collision_steps` - Steps hitting walls
14. `timeout` - 1 if timed out, 0 otherwise
15. `no_movement_truncated` - 1 if stuck, 0 otherwise
16. `milestone_25_reached` - 1 if reached 25% coverage
17. `milestone_50_reached` - 1 if reached 50% coverage
18. `milestone_75_reached` - 1 if reached 75% coverage

Plus 5 more metadata columns.

---

## Monitoring Live Training

### Watch console output in real-time
```bash
tail -f Mining\ Env/trial_30k_*.log
```

### Check progress (episodes completed)
```bash
wc -l Mining\ Env/outputs/trial_runs/trial_*/episode_metrics.csv
```

### View summary JSON
```bash
cat Mining\ Env/outputs/trial_runs/trial_*/summary.json | python -m json.tool
```

### Launch TensorBoard visualization
```bash
tensorboard --logdir Mining\ Env/outputs/trial_runs/trial_*/tensorboard --port 6006
```
Then visit: `http://localhost:6006`

---

## Policy Details

### explore (Default)
**Strategy:** Reactive wall-avoidance heuristic

- Scans front, left, right via 16-beam LiDAR
- Moves forward (vel=1.0) if path clear, else slow (vel=0.3)
- Turns left/right proportional to wall proximity
- Simple but effective baseline for exploration

**Good for:** Initial exploration, feasibility testing

### random
**Strategy:** Pure random action sampling

- Velocity: [-1.5, 1.5] m/s (random uniform)
- Omega: [-1.5, 1.5] rad/s (random uniform)

**Good for:** Baseline comparison, stress testing

---

## Analyzing Results

### Python (Pandas)
```python
import pandas as pd
import json

# Load CSV
df = pd.read_csv('Mining Env/outputs/trial_runs/trial_*/episode_metrics.csv')
print(df.describe())
print(df['reward_total'].mean())
print(df['coverage_fraction'].max())

# Load summary JSON
with open('Mining Env/outputs/trial_runs/trial_*/summary.json') as f:
    summary = json.load(f)
    print(f"Avg Reward: {summary['avg_reward_total']:.3f}")
    print(f"Success Rate: {summary['milestone_75_rate']:.3f}")
```

### View PNG plots
```bash
open Mining\ Env/outputs/trial_runs/trial_*/plots/trends/reward_total.png
open Mining\ Env/outputs/trial_runs/trial_*/plots/rates/milestone_75_rate.png
```

---

## Performance Tips

### Speed up training
- **Reduce max-steps**: `--max-steps 1000` (faster episodes)
- **Fewer episodes**: `--episodes 1000` (test run)
- **Less plotting**: `--plot-every 10000` (fewer overhead)

### Reduce memory usage
- Use default `--num-agents 1` (not tested with >1)
- Reduce `--summary-window` (smaller rolling stats)

### Better results
- Train longer: `--episodes 100000` (more data)
- Adjust reward in `Mining Env/mining_env/config.py`
- Change spawn mode: Edit `cfg.spawn = replace(cfg.spawn, spawn_mode="...")`

---

## Troubleshooting

### "No module named mining_env"
```bash
cd ~/mining_env_dataset_folder
source Mining\ Env/.venv/bin/activate
python rl_training.py
```

### "chilean_mine_geometry.xml not found"
```bash
cd Mining\ Env
python scripts/01_build_mine_geometry.py --phase 2
```

### Script hangs / no output
Use `python -u` to unbuffer output:
```bash
python -u rl_training.py
```

### Out of memory
- Reduce episodes: `--episodes 5000`
- Use smaller window: `--summary-window 50`

---

## Customization

### Change reward function
Edit: `Mining Env/mining_env/config.py`
```python
reward = 90/10 rule (90% milestones, 10% progress)
# Modify RewardConfig in config.py
```

### Change spawn region
Edit line 412 in `rl_training.py`:
```python
# From:
cfg.spawn = replace(cfg.spawn, spawn_mode="region_a")

# To:
cfg.spawn = replace(cfg.spawn, spawn_mode="ae_opposite")  # or ae_feasible, auto_feasible
```

### Add custom policy
Modify the `explore_action()` function or add a new policy type in `parse_args()`.

---

## Command Line Arguments Explained

```bash
python rl_training.py \
    --episodes 30000 \         # Run 30,000 episodes
    --num-agents 1 \           # 1 agent per episode
    --max-steps 6000 \         # Each episode max 6000 steps
    --policy explore \         # Use wall-avoidance policy
    --print-every 10 \         # Print stats every 10 episodes
    --plot-every 5000 \        # Regenerate plots every 5000 episodes
    --summary-window 100 \     # Rolling stats over 100 episodes
    --run-dir outputs/trial_runs  # Save results here
```

---

## Expected Duration

- **100 episodes:** 5-10 minutes
- **1,000 episodes:** 1-2 hours
- **5,000 episodes:** 6-10 hours
- **30,000 episodes:** 24-48 hours (depends on hardware)

---

## What Gets Printed

Every `--print-every` episodes:
```
[ep    10] reward=    0.350 coverage=0.021 new_cells=   39 coll_steps=   0
+-------------------------------------------+
| Last 100 Episodes Summary                 |
| episodes             : 100                |
| avg_reward_total     : 0.350              |
| avg_reward_per_step  : 0.00035            |
| avg_episode_length   : 1000.0             |
| avg_coverage_fraction: 0.021              |
| avg_coverage_auc     : 0.015              |
| avg_new_cells_total  : 39.0               |
| avg_collision_steps  : 0.00               |
| milestone_75_rate    : 0.000              |
+-------------------------------------------+
```

---

## Support

For issues with the mining environment itself:
- Check: `Mining Env/docs/PHASE_WISE_PLAN_UPDATED.md`
- View config: `Mining Env/mining_env/config.py`
- Inspect geometry: `Mining Env/outputs/chilean_mine_geometry.xml`

For this script specifically:
- Run with `--help` for all options
- Check docstrings in the Python file
- Review output JSON for detailed run statistics

---

## Key Code Functions

| Function | Purpose |
|----------|---------|
| `main()` | Orchestrates the entire training loop |
| `run_episode()` | Simulates one episode, returns metrics |
| `explore_action()` | Wall-avoidance policy implementation |
| `make_plots()` | Generates all PNG graphs |
| `summarize()` | Aggregates episode statistics |
| `parse_args()` | Command-line argument parsing |

---

**Last Updated:** 2026-04-10  
**Script Location:** `~/mining_env_dataset_folder/rl_training.py`  
**Tested On:** Python 3.10, MuJoCo 2.x, PettingZoo 1.x
