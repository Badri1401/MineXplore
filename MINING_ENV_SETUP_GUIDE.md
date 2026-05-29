# Mining Environment Setup Guide

You now have a **complete, portable mining environment package** in this folder. Here's how to use it.

## What You Have

```
~/mining_env_dataset_folder/
├── mining_env_complete/              ← Complete mining environment package
│   ├── mining_env/                   Python package (config, environment logic)
│   ├── outputs/                      Physics model + mesh geometry
│   ├── README.md                     Detailed documentation
│   └── QUICK_IMPORT.md              How to use in your projects
├── rl_training.py                    ← Standalone training script
├── RUN_TRAINING.sh                   ← Bash wrapper for easy execution
├── RL_TRAINING_GUIDE.md              ← Training documentation
└── TRAINING_SETUP_COMPLETE.md        ← Quick reference
```

## Quick Start: Run Training

### Easiest Method
```bash
cd ~/mining_env_dataset_folder
./RUN_TRAINING.sh --episodes 100
```

Results will be saved to: `Mining Env/outputs/trial_runs/trial_YYYYMMDD_HHMMSS/`

### With Custom Parameters
```bash
./RUN_TRAINING.sh --episodes 30000 --max-steps 3000 --policy explore
```

## Using Mining Environment in Your Own Code

### Method 1: Add to Python Path
```bash
export PYTHONPATH=~/mining_env_dataset_folder/mining_env_complete:$PYTHONPATH
```

Then in Python:
```python
from mining_env import MiningParallelEnv
from mining_env.config import DEFAULT_CONFIG

env = MiningParallelEnv(config=DEFAULT_CONFIG)
```

### Method 2: Copy to Your Project
```bash
cp -r ~/mining_env_dataset_folder/mining_env_complete/mining_env <your_project>/
cp -r ~/mining_env_dataset_folder/mining_env_complete/outputs <your_project>/
```

## Understanding the Package Structure

### Core Files (40 KB)

**`mining_env/config.py`** — Edit this to customize
- Robot size, sensor configuration, reward function
- Spawn modes and collision parameters
- Physics timestep and episode length

**`mining_env/parallel_env.py`** — Main environment (26 KB)
- Physics simulation with MuJoCo
- 360-beam LiDAR sensor
- Multi-agent support via PettingZoo
- Reward computation and observation generation

**`mining_env/single_agent_env.py`** — Gymnasium wrapper
- Single-agent interface for RL training
- Standard gym.Env API

### Geometry Files (550 KB)

**`outputs/chilean_mine_geometry.xml`** — MuJoCo model
- 276 KB XML file defining robot and environment
- References 1186 rock mesh pieces
- Physics properties and contact configurations

**`outputs/meshes/`** — Tunnel geometry (~800 MB)
- 1186 convex rock pieces (rock_0000.obj to rock_1185.obj)
- tunnel_polygon.pkl for feasibility validation
- DO NOT delete individual mesh files

## Configuration Quick Reference

Edit `mining_env_complete/mining_env/config.py`:

```python
# Robot physical properties
robot_radius = 0.35  # meters
max_velocity = 1.5   # m/s forward/backward
max_omega = 1.5      # rad/s rotation

# Sensor
num_lidar_beams = 360
lidar_max_range = 30.0  # meters

# Reward function
reward_weight_progress = 0.1
reward_weight_milestones = 0.9
collision_penalty = -10.0
goal_bonus = +10.0

# Episode
max_episode_steps = 6000

# Spawn region
spawn_mode = "local_curriculum"  # or ae_feasible, ae_opposite, auto_feasible
```

## Example: Complete Training Loop

```python
import numpy as np
from mining_env import MiningParallelEnv
from mining_env.config import DEFAULT_CONFIG

# Create environment with default config
env = MiningParallelEnv(config=DEFAULT_CONFIG)

# Run 10 episodes
total_rewards = []

for episode in range(10):
    observations, infos = env.reset(seed=episode)
    done = False
    episode_reward = 0
    
    while not done:
        # Random action for each agent
        actions = {agent: env.action_space.sample() for agent in env.agents}
        
        # Step environment
        observations, rewards, terminated, truncated, infos = env.step(actions)
        
        # Accumulate reward
        episode_reward += sum(rewards.values())
        
        # Check termination
        done = all(terminated.values()) or all(truncated.values())
    
    total_rewards.append(episode_reward)
    print(f"Episode {episode}: reward={episode_reward:.3f}")

env.close()

# Print statistics
print(f"\nAverage reward: {np.mean(total_rewards):.3f}")
print(f"Max reward: {np.max(total_rewards):.3f}")
```

## Example: Custom Configuration

```python
from mining_env import MiningParallelEnv
from mining_env.config import DEFAULT_CONFIG
from dataclasses import replace

# Create custom configuration
custom_config = replace(
    DEFAULT_CONFIG,
    # Reduce episode length
    max_episode_steps=2000,
    # Change spawn region
    spawn=replace(
        DEFAULT_CONFIG.spawn,
        spawn_mode="ae_feasible"  # Challenge: opposite ends
    ),
    # Modify robot speed
    max_velocity=2.0  # Faster robot
)

# Create environment with custom config
env = MiningParallelEnv(config=custom_config)
```

## Training with RL Algorithm

### Using Ray RLlib (if available)

```python
from ray.rllib.algorithms.ppo import PPO
from mining_env import SingleAgentMiningSyncEnv

# Create trainer
trainer = PPO(
    env=SingleAgentMiningSyncEnv,
    config={
        "framework": "torch",
        "num_workers": 4,
        "num_envs_per_worker": 2,
    }
)

# Train for 100k steps
for i in range(10):
    result = trainer.train()
    print(f"Iteration {i}: reward={result['episode_reward_mean']:.3f}")

# Save checkpoint
trainer.save("/tmp/mining_env_ppo_checkpoint")
```

### Using Stable-Baselines3 (if available)

```python
from stable_baselines3 import PPO
from mining_env import SingleAgentMiningSyncEnv

# Create environment
env = SingleAgentMiningSyncEnv()

# Create and train agent
agent = PPO("MlpPolicy", env, verbose=1)
agent.learn(total_timesteps=100000)

# Save
agent.save("mining_env_ppo")
```

## Training Results Structure

After running `rl_training.py`, results are saved to:

```
Mining Env/outputs/trial_runs/trial_20260410_163209/
├── episode_metrics.csv      # Per-episode data (23 columns)
├── summary.json             # Aggregate statistics
├── plots/
│   ├── trends/              # Reward, coverage curves
│   │   ├── reward_total.png
│   │   ├── coverage_fraction.png
│   │   └── new_cells_total.png
│   └── rates/               # Success, collision, timeout rates
│       ├── milestone_25_rate.png
│       ├── milestone_75_rate.png
│       └── timeout_rate.png
└── tensorboard/             # Event logs
    └── events.out.tfevents.*
```

## Analyzing Results

### Load CSV data with pandas
```python
import pandas as pd

df = pd.read_csv('Mining Env/outputs/trial_runs/trial_*/episode_metrics.csv')
print(df.describe())
print(f"Best coverage: {df['coverage_fraction'].max():.3f}")
print(f"Success rate: {(df['timeout'] == 0).mean():.3f}")
```

### View TensorBoard
```bash
tensorboard --logdir Mining\ Env/outputs/trial_runs/trial_*/tensorboard --port 6006
# Then visit: http://localhost:6006
```

## File Locations Quick Reference

| What | Path |
|------|------|
| **Package root** | `~/mining_env_dataset_folder/mining_env_complete/` |
| **Python code** | `~/mining_env_dataset_folder/mining_env_complete/mining_env/` |
| **Config file** | `~/mining_env_dataset_folder/mining_env_complete/mining_env/config.py` |
| **Geometry** | `~/mining_env_dataset_folder/mining_env_complete/outputs/chilean_mine_geometry.xml` |
| **Training script** | `~/mining_env_dataset_folder/rl_training.py` |
| **Training wrapper** | `~/mining_env_dataset_folder/RUN_TRAINING.sh` |
| **Results** | `~/mining_env_dataset_folder/Mining\ Env/outputs/trial_runs/trial_*` |

## Troubleshooting

### Import Error: "No module named 'mining_env'"
```bash
export PYTHONPATH=~/mining_env_dataset_folder/mining_env_complete:$PYTHONPATH
python your_script.py
```

### Missing geometry file
```bash
ls ~/mining_env_dataset_folder/mining_env_complete/outputs/chilean_mine_geometry.xml
# If missing, copy from original:
cp ~/Desktop/IISC/ICRA/Mining\ Env/outputs/chilean_mine_geometry.xml \
   ~/mining_env_dataset_folder/mining_env_complete/outputs/
```

### Environment won't step
Check that `outputs/meshes/` has ~1186 rock files:
```bash
ls ~/mining_env_dataset_folder/mining_env_complete/outputs/meshes/*.obj | wc -l
```

### Training script hangs
Run with unbuffered output:
```bash
python -u rl_training.py --episodes 100
```

## Next Steps

1. **Explore the package**
   ```bash
   cat ~/mining_env_dataset_folder/mining_env_complete/README.md
   cat ~/mining_env_dataset_folder/mining_env_complete/QUICK_IMPORT.md
   ```

2. **Run a quick training trial**
   ```bash
   cd ~/mining_env_dataset_folder
   ./RUN_TRAINING.sh --episodes 100
   ```

3. **Write your own RL algorithm**
   - Use `mining_env_complete` as your environment
   - Implement your own agent
   - Log results to the trial_runs folder

4. **Customize the environment**
   - Edit `mining_env_complete/mining_env/config.py`
   - Change robot properties, reward, spawn region
   - Re-run training with new config

## Documentation Files

- **[README.md](mining_env_complete/README.md)** — Comprehensive package overview
- **[QUICK_IMPORT.md](mining_env_complete/QUICK_IMPORT.md)** — Import methods and examples
- **[PACKAGE_SUMMARY.txt](mining_env_complete/PACKAGE_SUMMARY.txt)** — Complete inventory
- **[RL_TRAINING_GUIDE.md](RL_TRAINING_GUIDE.md)** — Training script documentation
- **[TRAINING_SETUP_COMPLETE.md](TRAINING_SETUP_COMPLETE.md)** — Quick reference

## Support

**For mining environment issues:**
- See config.py docstrings
- Check mining_env_complete/README.md
- Review CLAUDE.md in original repo

**For training script issues:**
- Read RL_TRAINING_GUIDE.md
- Check script output and error messages
- Ensure dependencies are installed

---

**Created:** 2026-04-10  
**Status:** ✅ Complete and ready to use  
**Total Size:** ~850 MB  
**File Count:** 4 Python files + 2 XML + 1188 mesh files + documentation

Now you have everything you need to run the mining environment and conduct RL training!
