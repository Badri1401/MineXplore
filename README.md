# Mining Environment — Exploration-First Implementation

**Complete exploration-based RL environment for autonomous mine mapping.**

---

## 📁 Structure

```
mining_env_dataset_folder/
├── Mining Env/                          # Full codebase (ready to run)
│   ├── mining_env/
│   │   ├── config.py                   # ExplorationSpec + all parameters
│   │   ├── parallel_env.py             # Core env: grid, reward, dynamics
│   │   └── single_agent_env.py         # Gymnasium wrapper for training
│   ├── scripts/
│   │   ├── 10_trial_pipeline_check.py  # Run 30k episode trial
│   │   ├── 20_train_rllib_ppo.py       # Train PPO with LSTM
│   │   └── 12_eval_exploration.py      # Evaluate maps (4 metrics)
│   ├── outputs/                        # Generated models & results
│   ├── docs/rl_exploration.md          # Design specification
│   ├── READINESS_REPORT.md             # Validation report
│   └── CLAUDE.md                       # Project instructions
├── IMPLEMENTATION_COMPLETE.md          # What was delivered
├── QUICK_START.sh                      # Run 30k episodes in one command
└── raw_bags/                           # Raw dataset (reference)
```

---

## 🚀 Quick Start (30,000 Episodes)

### Option 1: Automated Script
```bash
cd mining_env_dataset_folder
bash QUICK_START.sh
```

### Option 2: Manual Command
```bash
cd mining_env_dataset_folder/"Mining Env"
source .venv/bin/activate

python scripts/10_trial_pipeline_check.py \
  --episodes 30000 \
  --policy explore \
  --max-steps 6000 \
  --print-every 10 \
  --plot-every 5000 \
  --summary-window 100
```

**Expected runtime:** 5–8 hours  
**Expected output:** Coverage metrics CSV + trending plots + summaries every 10 episodes

---

## 📋 What's Implemented

### ✅ Exploration-Only Environment
- Start at mine entrance (Region A), learn to explore 836m tunnel
- 19D observation: 16 LiDAR beams + 3 velocity features
- Non-terminal collision (penalizes but continues episode)
- No-movement truncation (stops if frozen)

### ✅ Reward Structure (90/10)
```
90% bucket (one-time milestones):
  ├─ M25 at 25% coverage: +15.0 (1 part)
  ├─ M50 at 50% coverage: +30.0 (2 parts)
  └─ M75 at 75% coverage: +45.0 (3 parts)
     Total: 90.0

10% bucket (per-step signals):
  ├─ Exploration gain: +0.00541/cell (scales with tunnel size)
  ├─ Revisit penalty: -0.002/step when no new cells
  └─ Total max: +10.0

Collision penalty: -15.0/step (non-terminal)
Max reward/episode: 100.0
```

### ✅ Coverage Grid & Tracking
- 2m × 2m cells, 1848 total tunnel cells
- Monotonic coverage (never decreases)
- Set-based milestone tracking (prevents double-counting)
- Occupancy grid visualization + side-by-side map comparison

### ✅ LSTM-Based Policy
- Recurrent network (256 cell) learns long-term exploration strategy
- Memory over 6000-step horizon
- FCNet backbone: [256, 256]
- Compatible with PPO training

### ✅ Training Pipeline
- **Rapid mode:** 300k timesteps, smoke test
- **Full mode:** 120M timesteps, production
- PPO with RLlib
- 4 parallel workers
- Gamma 0.995 (long-horizon planning)
- Checkpoint cleanup (saves disk space)

### ✅ Evaluation Metrics
1. **Coverage** (≥0.70): cells_seen / total_cells
2. **IoU** (≥0.60): intersection / union
3. **Dice** (≥0.70): 2×intersection / (seen + tunnel)
4. **Boundary distance** (≥0.50): normalized Hausdorff

---

## ⚙️ Key Configuration

| Parameter | Value |
|-----------|-------|
| Max episode length | 6000 steps (600s) |
| LiDAR range | 0.12–10.0m, 16 beams |
| Cell size | 2m × 2m |
| Total cells | 1848 (from tunnel polygon) |
| Spawn location | Region A (82, 92) + random yaw |
| Collision behavior | Penalizes (-15/step) but continues |
| M25 bonus | +15.0 at 25% coverage |
| M50 bonus | +30.0 at 50% coverage |
| M75 bonus | +45.0 at 75% coverage |
| Revisit penalty | -0.002/step (no new cells) |
| LSTM cell size | 256 |
| Gamma | 0.995 (long-horizon discount) |

---

## ✅ Validation Results

All components tested and verified:

- [x] Grid initialization from tunnel polygon
- [x] Reward structure (90/10 exact match)
- [x] Observation space (19D, normalized)
- [x] Coverage tracking (monotonic)
- [x] Milestones (one-time only)
- [x] Collision (non-terminal)
- [x] Training smoke test
- [x] Evaluation smoke test
- [x] Checkpoint restore

**Status: READY FOR 30,000 EPISODES**

---

## 📊 Expected Results After 30K Episodes

- Coverage: 50–70% (depends on policy)
- Reward: 30–50 per episode (average)
- Milestone 25 hit rate: 80–95%
- Milestone 50 hit rate: 30–60%
- Milestone 75 hit rate: 5–20%
- Collision steps: <5% of episode

---

## ⚠️ Known Constraints

1. **Disk Space:** Only 2.5 GB available
   - Full 120M-step training may need 50+ GB
   - Checkpoint cleanup keeps 2 most recent
   - Monitor with: `du -sh outputs/ ~/raytmp/`

2. **Observation Space Changed:** 19D (from old 24D)
   - Cannot load old checkpoints
   - Must retrain from scratch

3. **Ray Temp Path:** `/home/badrikanath/raytmp`
   - Safe for UNIX sockets ✓

---

## 📈 Post-Run Analysis

### Check Coverage Trends
```bash
cd Mining\ Env
python -c "
import json, csv
with open('outputs/trial_runs/*/episode_metrics.csv') as f:
    rows = list(csv.DictReader(f))
    covs = [float(r['coverage_fraction']) for r in rows]
    print(f'Coverage: min={min(covs):.1%} max={max(covs):.1%} final={covs[-1]:.1%}')
"
```

### Visualize Coverage Curve
```bash
cd Mining\ Env
open outputs/trial_runs/*/plots/coverage_vs_steps.png
```

### Evaluate Map Quality
```bash
cd Mining\ Env
python scripts/12_eval_exploration.py \
  --episodes 50 \
  --policy random \
  --max-steps 6000
```

---

## 📝 Files to Review

| File | Purpose |
|------|---------|
| `Mining Env/READINESS_REPORT.md` | Detailed validation report |
| `Mining Env/docs/rl_exploration.md` | Original design specification |
| `Mining Env/mining_env/config.py` | All configurable parameters |
| `IMPLEMENTATION_COMPLETE.md` | What was delivered |

---

## 🎯 Next Steps

1. **Run 30K episodes:**
   ```bash
   bash QUICK_START.sh
   ```

2. **Monitor progress:**
   ```bash
   watch -n 60 'du -sh outputs/ ~/raytmp/'
   ```

3. **Analyze results:**
   - Check plots in `outputs/trial_runs/<timestamp>/plots/`
   - Review CSV metrics in `outputs/trial_runs/<timestamp>/episode_metrics.csv`
   - View summary in `outputs/trial_runs/<timestamp>/summary.json`

4. **Evaluate trained policy:**
   ```bash
   python Mining\ Env/scripts/12_eval_exploration.py \
     --episodes 50 \
     --policy random \
     --max-steps 6000
   ```

---

## 📚 Documentation

- **Design:** `Mining Env/docs/rl_exploration.md`
- **Validation:** `Mining Env/READINESS_REPORT.md`
- **Configuration:** `Mining Env/mining_env/config.py`
- **Instructions:** `Mining Env/CLAUDE.md`

---

## 🔧 Troubleshooting

### Issue: Disk full during run
**Solution:** Checkpoint cleanup should keep space free. If not, manually delete old checkpoints:
```bash
rm -rf Mining\ Env/outputs/rllib_runs/ppo_*/checkpoints/
```

### Issue: Memory error
**Solution:** Reduce workers in full mode or use rapid mode for testing:
```bash
python Mining\ Env/scripts/20_train_rllib_ppo.py --mode rapid
```

### Issue: Ray temp dir fills up
**Solution:** Clear Ray temp directory:
```bash
rm -rf ~/raytmp/
mkdir ~/raytmp
```

---

## 📧 Questions?

Refer to:
1. `READINESS_REPORT.md` — Validation details
2. `Mining Env/CLAUDE.md` — Project instructions
3. `Mining Env/docs/rl_exploration.md` — Design spec

---

**Ready to explore! 🗺️**

Generated: 2026-04-10  
Status: ✅ READY FOR 30,000 EPISODE PRODUCTION RUN
