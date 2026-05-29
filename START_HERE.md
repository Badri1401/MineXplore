# START HERE 🚀

Welcome! You have a complete mining environment setup ready to use.

## What You Have

This folder now contains everything needed to run RL training on a mine tunnel navigation task:

```
~/mining_env_dataset_folder/
├── mining_env_complete/        Complete, self-contained environment package
├── rl_training.py              Standalone training script (1000+ lines)
├── RUN_TRAINING.sh             Bash wrapper for easy execution
└── Documentation (guides below)
```

## 3-Second Quick Start

```bash
cd ~/mining_env_dataset_folder
./RUN_TRAINING.sh --episodes 100
```

That's it! Results will appear in `Mining Env/outputs/trial_runs/`.

## Documentation Map

Read these in order based on what you want to do:

### 1. **System Overview** (Read First)
   - [SETUP_COMPLETE_SUMMARY.txt](SETUP_COMPLETE_SUMMARY.txt) — What was created, status, quick reference

### 2. **Complete User Guide**
   - [MINING_ENV_SETUP_GUIDE.md](MINING_ENV_SETUP_GUIDE.md) — Full guide to using everything
   - [mining_env_complete/README.md](mining_env_complete/README.md) — Detailed environment package info

### 3. **Training Script**
   - [TRAINING_SETUP_COMPLETE.md](TRAINING_SETUP_COMPLETE.md) — Quick training reference
   - [RL_TRAINING_GUIDE.md](RL_TRAINING_GUIDE.md) — Detailed training documentation

### 4. **Using the Environment in Your Code**
   - [mining_env_complete/QUICK_IMPORT.md](mining_env_complete/QUICK_IMPORT.md) — Import methods and examples
   - [mining_env_complete/PACKAGE_SUMMARY.txt](mining_env_complete/PACKAGE_SUMMARY.txt) — Package inventory

---

## Quick Decision Tree

**I want to...**

### ...run the training script
→ Execute: `./RUN_TRAINING.sh --episodes 100`
→ Read: [RL_TRAINING_GUIDE.md](RL_TRAINING_GUIDE.md)

### ...import the environment in my own code
→ Read: [mining_env_complete/QUICK_IMPORT.md](mining_env_complete/QUICK_IMPORT.md)
→ Example: 
```python
export PYTHONPATH=~/mining_env_dataset_folder/mining_env_complete:$PYTHONPATH
python
>>> from mining_env import MiningParallelEnv
>>> env = MiningParallelEnv()
```

### ...customize the environment (robot size, reward, spawn)
→ Edit: `mining_env_complete/mining_env/config.py`
→ Read: [mining_env_complete/README.md](mining_env_complete/README.md#configuration)

### ...understand the complete setup
→ Read: [MINING_ENV_SETUP_GUIDE.md](MINING_ENV_SETUP_GUIDE.md)

### ...troubleshoot an issue
→ Check: [SETUP_COMPLETE_SUMMARY.txt](SETUP_COMPLETE_SUMMARY.txt#troubleshooting) or specific guide

---

## File Structure

```
~/mining_env_dataset_folder/                      Your working directory
├── mining_env_complete/                          Complete environment package (~850 MB)
│   ├── mining_env/                               Python package (4 files, 40 KB)
│   │   ├── config.py          ← Edit this to customize
│   │   ├── parallel_env.py     Core environment logic
│   │   ├── single_agent_env.py Gymnasium wrapper
│   │   └── __init__.py
│   └── outputs/                Physics & geometry (~810 MB)
│       ├── chilean_mine_geometry.xml             MuJoCo model
│       ├── env_new_updated.xml
│       ├── meshes/                               1,188 geometry files
│       │   ├── rock_0000.obj ... rock_1185.obj
│       │   └── tunnel_polygon.pkl
│       └── trial_runs/                           Results directory
├── rl_training.py                                Standalone training script
├── RUN_TRAINING.sh                               Bash wrapper (executable)
├── START_HERE.md                                 This file
├── MINING_ENV_SETUP_GUIDE.md                    Master guide
├── SETUP_COMPLETE_SUMMARY.txt                   Status & reference
├── TRAINING_SETUP_COMPLETE.md                   Training quick ref
├── RL_TRAINING_GUIDE.md                         Training documentation
└── Mining Env/                                   Original environment
    ├── .venv/                                    Python virtualenv
    ├── scripts/                                  Utility scripts
    ├── mining_env/                               (also here)
    └── outputs/                                  Results go here
```

---

## Commands You'll Use

### Training

```bash
# Quick test (100 episodes, ~5-10 min)
./RUN_TRAINING.sh --episodes 100

# Full run (30k episodes, ~24-48 hours)
./RUN_TRAINING.sh --episodes 30000

# Custom parameters
./RUN_TRAINING.sh --episodes 5000 --max-steps 2000 --policy explore
```

### Monitoring

```bash
# Watch progress in real-time
tail -f Mining\ Env/outputs/trial_runs/trial_*/episode_metrics.csv

# View TensorBoard
tensorboard --logdir Mining\ Env/outputs/trial_runs/trial_*/tensorboard --port 6006
# Then visit: http://localhost:6006

# Check process
ps aux | grep rl_training
```

### Analysis

```python
import pandas as pd
df = pd.read_csv('Mining Env/outputs/trial_runs/trial_*/episode_metrics.csv')
print(df.describe())
print(f"Best coverage: {df['coverage_fraction'].max():.3f}")
```

---

## Key Concepts

### Environment
- **Robot**: 0.35m radius, max 1.5 m/s forward/backward, 1.5 rad/s rotation
- **Sensors**: 360-beam LiDAR (0.12-30m range)
- **Goal**: Navigate tunnel, maximize coverage
- **Reward**: 90% milestones + 10% progress, -10 for collision, +10 for goal

### Customize
Edit `mining_env_complete/mining_env/config.py`:
- Robot size: `robot_radius = 0.35`
- Spawn region: `spawn_mode = "local_curriculum"`
- Episode length: `max_episode_steps = 6000`
- Reward weights: `RewardConfig` class

### Results
After running, check:
- **CSV**: `Mining Env/outputs/trial_runs/trial_*/episode_metrics.csv` (23 columns per episode)
- **Plots**: `Mining Env/outputs/trial_runs/trial_*/plots/` (PNG graphs)
- **Summary**: `Mining Env/outputs/trial_runs/trial_*/summary.json` (aggregate stats)
- **TensorBoard**: `Mining Env/outputs/trial_runs/trial_*/tensorboard/` (interactive viz)

---

## Common Questions

**Q: What's the difference between mining_env_complete and Mining Env/?**
- `mining_env_complete/`: Portable package you can copy/import anywhere
- `Mining Env/`: Original environment with virtualenv and scripts

**Q: Where do results go?**
- `Mining Env/outputs/trial_runs/trial_YYYYMMDD_HHMMSS/` (auto-timestamped)

**Q: How do I customize the environment?**
- Edit: `mining_env_complete/mining_env/config.py`

**Q: Can I use this in my own Python project?**
- Yes! Set `PYTHONPATH=~/mining_env_dataset_folder/mining_env_complete:$PYTHONPATH` or copy the folder

**Q: What if training hangs?**
- Use unbuffered output: `python -u rl_training.py --episodes 100`

**Q: How long does training take?**
- 100 ep: 5-10 min | 1k: 1-2 hr | 5k: 6-10 hr | 30k: 24-48 hr

---

## Next Steps

### Option 1: Run Training (Simplest)
```bash
./RUN_TRAINING.sh --episodes 100
```
✅ Done! Check results in `Mining Env/outputs/trial_runs/`

### Option 2: Learn the Environment
```bash
cat mining_env_complete/README.md
cat mining_env_complete/QUICK_IMPORT.md
```

### Option 3: Use in Your Code
```bash
export PYTHONPATH=~/mining_env_dataset_folder/mining_env_complete:$PYTHONPATH
python your_script.py  # Import as: from mining_env import MiningParallelEnv
```

### Option 4: Customize & Experiment
```bash
# Edit config
nano mining_env_complete/mining_env/config.py

# Run with custom settings
./RUN_TRAINING.sh --episodes 5000
```

---

## Files at a Glance

| Document | What | Length | Purpose |
|----------|------|--------|---------|
| **START_HERE.md** | This file | 2 min | Overview & navigation |
| **SETUP_COMPLETE_SUMMARY.txt** | Status & quick ref | 3 min | What exists, how to use |
| **MINING_ENV_SETUP_GUIDE.md** | Complete guide | 10 min | Everything explained |
| **TRAINING_SETUP_COMPLETE.md** | Training ref | 2 min | Quick training reference |
| **RL_TRAINING_GUIDE.md** | Training details | 5 min | Training script documentation |
| **mining_env_complete/README.md** | Package info | 5 min | Environment package details |
| **mining_env_complete/QUICK_IMPORT.md** | Import methods | 3 min | How to use in your code |
| **mining_env_complete/PACKAGE_SUMMARY.txt** | Inventory | 5 min | File checklist |

---

## Status ✅

- ✅ Mining environment package created (850 MB, 1,199 files)
- ✅ Training script created (1000+ lines, fully documented)
- ✅ Bash wrapper created (easy execution)
- ✅ All documentation created (6+ guides)
- ✅ All files verified (geometry, meshes, code)
- ✅ Ready to use

**You can start right now:**
```bash
cd ~/mining_env_dataset_folder
./RUN_TRAINING.sh --episodes 100
```

---

## Support

**Need help?**
1. Check [SETUP_COMPLETE_SUMMARY.txt](SETUP_COMPLETE_SUMMARY.txt#troubleshooting) troubleshooting section
2. Read [MINING_ENV_SETUP_GUIDE.md](MINING_ENV_SETUP_GUIDE.md)
3. Review script output and error messages
4. Check original project: `~/Desktop/IISC/ICRA/Mining Env/CLAUDE.md`

---

**Created:** 2026-04-10  
**Status:** Ready to use  
**Next:** Read one of the guides or run training!

🚀 Let's go!
