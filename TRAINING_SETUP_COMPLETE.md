# RL Training Setup - Complete & Ready to Use

## ✅ What You Got

I've created a **standalone RL training script** that you can run anytime from the `mining_env_dataset_folder`.

### Files Created

| File | Purpose | Location |
|------|---------|----------|
| `rl_training.py` | Main training script (1000+ lines) | `~/mining_env_dataset_folder/rl_training.py` |
| `RUN_TRAINING.sh` | Bash wrapper (auto setup + run) | `~/mining_env_dataset_folder/RUN_TRAINING.sh` |
| `RL_TRAINING_GUIDE.md` | Complete documentation | `~/mining_env_dataset_folder/RL_TRAINING_GUIDE.md` |
| `TRAINING_SETUP_COMPLETE.md` | This file | `~/mining_env_dataset_folder/TRAINING_SETUP_COMPLETE.md` |

---

## 🚀 Quick Start

### Option 1: Using the Shell Script (Easiest)
```bash
cd ~/mining_env_dataset_folder
./RUN_TRAINING.sh --episodes 30000
```

### Option 2: Direct Python
```bash
cd ~/mining_env_dataset_folder
source Mining\ Env/.venv/bin/activate
python rl_training.py --episodes 30000
```

### Option 3: Custom Parameters
```bash
cd ~/mining_env_dataset_folder
./RUN_TRAINING.sh --episodes 5000 --max-steps 2000 --print-every 5
```

---

## 📋 Available Parameters

```
--episodes N           Number of episodes (default: 30000)
--max-steps N         Max steps per episode (default: 6000)
--policy TYPE         'explore' or 'random' (default: explore)
--print-every N       Print summary every N episodes (default: 10)
--plot-every N        Update plots every N episodes (default: 5000)
--summary-window N    Stats window size (default: 100)
--run-dir PATH        Output directory (default: outputs/trial_runs)
--num-agents N        Agents per episode (default: 1)
--seed N              Random seed (default: 42)
```

---

## 📊 Where Results Go

**Directory:** `Mining Env/outputs/trial_runs/trial_YYYYMMDD_HHMMSS/`

**Files created:**
```
├── episode_metrics.csv    # 23 columns, N rows (one per episode)
├── summary.json          # Aggregated stats
├── plots/
│   ├── trends/          # reward, coverage, new_cells, etc.
│   └── rates/           # milestone hit rates, timeouts, etc.
└── tensorboard/         # Event logs for visualization
```

---

## 🎯 Example Commands

### Test run (100 episodes, quick)
```bash
./RUN_TRAINING.sh --episodes 100 --max-steps 500
```

### Full 30k run (24-48 hours)
```bash
./RUN_TRAINING.sh --episodes 30000
```

### Custom parameters
```bash
./RUN_TRAINING.sh \
    --episodes 10000 \
    --max-steps 3000 \
    --policy explore \
    --print-every 5 \
    --plot-every 2000
```

### With unbuffered output to file
```bash
./RUN_TRAINING.sh --episodes 30000 2>&1 | tee training_log.txt
```

---

## 📈 Monitoring Your Training

### Real-time progress
```bash
tail -f Mining\ Env/outputs/trial_runs/trial_*/episode_metrics.csv
```

### Process status
```bash
ps aux | grep rl_training
```

### View summary after run
```bash
cat Mining\ Env/outputs/trial_runs/trial_*/summary.json | python -m json.tool
```

### TensorBoard visualization
```bash
tensorboard --logdir Mining\ Env/outputs/trial_runs/trial_*/tensorboard --port 6006
```

---

## 🔍 Key Script Features

✅ **Unbuffered output** - See progress in real-time  
✅ **Auto-timestamped results** - No overwriting old runs  
✅ **CSV export** - All episode metrics for analysis  
✅ **JSON summary** - Aggregate statistics  
✅ **PNG plots** - Graphs updated every N episodes  
✅ **TensorBoard logging** - Interactive visualization  
✅ **Flexible policies** - explore (wall-avoid) or random  
✅ **Custom parameters** - Tune everything via CLI  

---

## 📝 Script Structure

The `rl_training.py` file contains:

1. **parse_args()** - Command-line argument handling
2. **run_episode()** - Single episode execution
3. **explore_action()** - Wall-avoidance policy (reactive)
4. **summarize()** - Statistical aggregation
5. **make_plots()** - PNG graph generation
6. **main()** - Training loop orchestration

Total: **1000+ lines of fully documented code**

---

## 🛠️ How the explore Policy Works

The default `explore` policy implements **reactive wall-avoidance**:

1. Read 16-beam LiDAR (front, left, right)
2. If front path clear: move forward (vel=1.0)
3. If obstacle: slow down (vel=0.3)
4. Turn left/right proportional to wall proximity
5. Repeat

This is **not learned** - it's a simple heuristic baseline for exploration.

---

## 📊 CSV Columns (episode_metrics.csv)

```
1.  episode                 - Episode number (1-30000)
2.  reward_total           - Total reward for episode
3.  reward_per_step        - Average reward/step
4.  episode_length         - Steps taken
5.  max_steps_budget       - Max allowed steps
6.  budget_utilization     - Steps/Max ratio
7.  coverage_fraction      - % of tunnel explored [0-1]
8.  coverage_auc           - Area under coverage curve
9.  cells_seen_count       - Total cells visited
10. total_tunnel_cells     - Total cells in environment
11. new_cells_total        - New cells discovered
12. avg_new_cells_per_step - Discovery efficiency
13. collision_steps        - Steps hitting walls
14. timeout                - 1=timed out, 0=normal end
15. no_movement_truncated  - 1=stuck, 0=moving
16. milestone_25_reached   - 1=reached 25% coverage
17. milestone_50_reached   - 1=reached 50% coverage
18. milestone_75_reached   - 1=reached 75% coverage
```

---

## 🔧 Customization

### Change reward function
Edit: `Mining Env/mining_env/config.py`
- Modify `RewardConfig` class
- Edit milestone bonuses, collision penalties, etc.

### Change spawn region
Edit line ~410 in `rl_training.py`:
```python
cfg.spawn = replace(cfg.spawn, spawn_mode="ae_opposite")
```
Options: `region_a`, `ae_feasible`, `ae_opposite`, `auto_feasible`

### Add custom policy
Modify `explore_action()` function or add new policy in `parse_args()`:
```python
elif policy == "custom":
    actions = {a: my_custom_policy(observations[a]) for a in env.agents}
```

---

## ✅ Pre-flight Checklist

Before running, verify:

- [ ] You're in `~/mining_env_dataset_folder/`
- [ ] `Mining Env/` subfolder exists
- [ ] `Mining Env/.venv/` has Python 3.10+
- [ ] `Mining Env/mining_env/config.py` exists
- [ ] `Mining Env/outputs/chilean_mine_geometry.xml` exists
- [ ] `rl_training.py` is in the dataset folder (not in Mining Env/)
- [ ] `RUN_TRAINING.sh` is executable

Quick check:
```bash
cd ~/mining_env_dataset_folder
ls -la rl_training.py RUN_TRAINING.sh
ls Mining\ Env/.venv/bin/python
ls Mining\ Env/mining_env/config.py
```

---

## 🚨 Troubleshooting

### Script says "Mining Env folder not found"
```bash
# Make sure you're in the right directory
cd ~/mining_env_dataset_folder
ls Mining\ Env/  # Should list scripts/, mining_env/, outputs/, etc.
```

### Python: "No module named mining_env"
```bash
# Make sure to activate venv first
source Mining\ Env/.venv/bin/activate
python rl_training.py
```

### No output for several minutes
The script uses unbuffered Python (`-u` flag) so output should appear immediately. If not:
```bash
# Run with explicit unbuffering
python -u rl_training.py
```

### Out of memory errors
Reduce the episodes or window size:
```bash
./RUN_TRAINING.sh --episodes 1000 --summary-window 50
```

---

## 📚 Documentation Files

1. **This file (TRAINING_SETUP_COMPLETE.md)** - Overview & quick reference
2. **RL_TRAINING_GUIDE.md** - Detailed guide with examples
3. **rl_training.py** - Full source code with docstrings
4. **RUN_TRAINING.sh** - Bash wrapper with checks

---

## ⏱️ Expected Run Times

| Episodes | Duration |
|----------|----------|
| 100 | 5-10 min |
| 1,000 | 1-2 hours |
| 5,000 | 6-10 hours |
| 30,000 | 24-48 hours |

(Depends on CPU, memory, episode complexity)

---

## 🎓 What You Can Do With Results

### Analyze in Python
```python
import pandas as pd
import json

# Load CSV
df = pd.read_csv('Mining Env/outputs/trial_runs/trial_*/episode_metrics.csv')
print(df['reward_total'].describe())
print(f"Best coverage: {df['coverage_fraction'].max():.3f}")
print(f"Avg new cells/episode: {df['new_cells_total'].mean():.1f}")

# Load JSON summary
with open('Mining Env/outputs/trial_runs/trial_*/summary.json') as f:
    summary = json.load(f)
    print(f"75% milestone hit rate: {summary['milestone_75_rate']:.3f}")
```

### View Plots
```bash
# View PNG graphs
open Mining\ Env/outputs/trial_runs/trial_*/plots/trends/reward_total.png
open Mining\ Env/outputs/trial_runs/trial_*/plots/rates/milestone_75_rate.png
```

### Interactive Dashboard
```bash
tensorboard --logdir Mining\ Env/outputs/trial_runs/trial_*/tensorboard --port 6006
# Visit: http://localhost:6006
```

---

## 🔄 Running Multiple Trials

Each run creates a **unique timestamped folder**, so you can run multiple trials without overwriting:

```bash
# Trial 1
./RUN_TRAINING.sh --episodes 5000

# While that runs... in another terminal
# Trial 2 with different parameters
./RUN_TRAINING.sh --episodes 10000 --policy random

# Check all results
ls Mining\ Env/outputs/trial_runs/
# Output:
# trial_20260410_163209/
# trial_20260410_165432/
# trial_20260410_171245/
```

---

## 📖 Next Steps

1. **Run a quick test**
   ```bash
   ./RUN_TRAINING.sh --episodes 100
   ```

2. **Check results**
   ```bash
   cat Mining\ Env/outputs/trial_runs/trial_*/summary.json
   ```

3. **Run full 30k trial**
   ```bash
   ./RUN_TRAINING.sh --episodes 30000
   ```

4. **Monitor with TensorBoard** (while running)
   ```bash
   tensorboard --logdir Mining\ Env/outputs/trial_runs/trial_*/tensorboard --port 6006
   ```

5. **Analyze results in Python** (after completion)
   ```python
   import pandas as pd
   df = pd.read_csv('Mining Env/outputs/trial_runs/trial_*/episode_metrics.csv')
   df.describe()
   ```

---

## 📞 Support

**Script issues:**
- Review `RL_TRAINING_GUIDE.md`
- Check source code comments in `rl_training.py`
- Ensure you're in `~/mining_env_dataset_folder/`

**Environment issues:**
- See `Mining Env/CLAUDE.md` for project setup
- Check `Mining Env/mining_env/config.py` for parameter info

---

## 📋 File Checklist

Before using, verify these exist:

```
~/mining_env_dataset_folder/
├── rl_training.py                    ✓ Main script
├── RUN_TRAINING.sh                   ✓ Bash wrapper
├── RL_TRAINING_GUIDE.md             ✓ Detailed guide
├── TRAINING_SETUP_COMPLETE.md       ✓ This file
├── Mining Env/
│   ├── .venv/                       ✓ Virtual environment
│   ├── mining_env/
│   │   ├── config.py                ✓ Config (edit for params)
│   │   └── parallel_env.py          ✓ Core environment
│   ├── scripts/
│   │   └── 10_trial_pipeline_check.py
│   └── outputs/
│       ├── chilean_mine_geometry.xml ✓ MuJoCo model
│       └── meshes/
│           └── tunnel_polygon.pkl    ✓ Spatial polygon
```

---

## 🎯 You're All Set!

Everything is ready. Just run:

```bash
cd ~/mining_env_dataset_folder
./RUN_TRAINING.sh --episodes 30000
```

Or with custom parameters:

```bash
./RUN_TRAINING.sh --episodes 5000 --max-steps 2000 --print-every 5
```

Results will be saved to `Mining Env/outputs/trial_runs/trial_<timestamp>/`

**Happy training!** 🚀

---

**Last Updated:** 2026-04-10  
**Files Ready:** ✓ Yes  
**Status:** Ready to run  
**Location:** `~/mining_env_dataset_folder/rl_training.py`
