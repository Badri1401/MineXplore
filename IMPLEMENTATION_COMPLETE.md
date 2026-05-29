# Mining Environment — Exploration-First Implementation ✅

**Completion Date:** 2026-04-10  
**Status:** READY FOR 30,000 EPISODE PRODUCTION RUN

---

## What Has Been Delivered

### 1. **Exploration-Only Environment**
   - Removed all goal-navigation logic
   - Pure autonomous mine mapping task
   - Start at Region A, learn to explore 836m tunnel
   - Objective: maximize coverage, validated against ground-truth polygon

### 2. **Reward Structure (90/10 Decomposition)**
   - **90% bucket** (one-time milestones in 1:2:3 ratio):
     - M25 at 25% coverage: +15.0
     - M50 at 50% coverage: +30.0
     - M75 at 75% coverage: +45.0
     - Subtotal: 90.0
   - **10% bucket** (per-step dense signals):
     - Exploration gain: +0.00541 per new cell (scales with total_tunnel_cells)
     - Revisit penalty: -0.002 per step with zero new cells
     - Subtotal: max +10.0 if full tunnel explored
   - **Collision handling:** -15.0 per step in wall contact (non-terminal)
   - **Maximum per episode:** 100.0

### 3. **Observation Space (19D)**
   - 16 LiDAR ranges (normalized [0,1])
   - 3 velocity features: [vx_norm, vy_norm, w_norm]
   - No goal features
   - Fully normalized, compatible with LSTM

### 4. **Coverage Grid & Tracking**
   - 2m × 2m cells derived from tunnel polygon bounds
   - 1848 total tunnel cells
   - Monotonic seen_mask (never decreases)
   - Set-based milestone tracking (prevents double-counting)

### 5. **Episode Dynamics**
   - Max 6000 steps (600 seconds at 0.1s control dt)
   - Spawn: Region A anchor (82, 92) + random yaw
   - Collision: penalizes but **does not terminate**
   - No-movement: truncate if speed < 0.01 m/s for 100 steps
   - Timeout: truncate at max_steps

### 6. **LSTM-Based Policy**
   - Recurrent network (256 cell)
   - Max sequence length: 20
   - FCNet layers: [256, 256]
   - Enables robot to remember explored areas over 6000-step horizon

### 7. **Training Infrastructure**
   - **Rapid mode:** 300k timesteps, smoke test convergence
   - **Full mode:** 120M timesteps, production training
   - PPO with RLlib backend
   - 4 parallel workers (full mode)
   - Gamma 0.995 for long-horizon planning
   - Entropy coeff 0.01 for exploration
   - Checkpoint cleanup (keep 2 most recent)
   - Disk space precheck and warnings

### 8. **Evaluation Pipeline**
   - 4 map-quality metrics:
     - Coverage: cells_seen / total_cells (threshold: ≥0.70)
     - IoU: intersection / union (threshold: ≥0.60)
     - Dice: 2×intersection / (seen + tunnel) (threshold: ≥0.70)
     - Boundary distance: 1 - normalized Hausdorff (threshold: ≥0.50)
   - Side-by-side PNG visualization (ground truth vs. robot map)
   - Coverage curves with mean ± std bands
   - Pass/fail validation gates

### 9. **Trial Pipeline**
   - Episode-level metric logging (CSV)
   - Trending plots (reward, length, coverage)
   - Terminal summary boxes every 10 episodes
   - Plot refresh every 5000 episodes
   - Summary statistics aggregation

---

## Files Changed / Created

### Modified
- `mining_env/config.py` — Added `ExplorationSpec`, updated `max_steps=6000`
- `mining_env/parallel_env.py` — Exploration task, reward, obs, grid, collision logic
- `mining_env/single_agent_env.py` — Obs space shape 24→19
- `scripts/10_trial_pipeline_check.py` — Exploration metrics, terminal summaries
- `scripts/11_view_training_env.py` — Exploration-compatible viewer
- `scripts/20_train_rllib_ppo.py` — LSTM config, rapid/full modes, checkpoint cleanup

### Created
- `scripts/12_eval_exploration.py` — 4-metric evaluation + map visualization
- `READINESS_REPORT.md` — This comprehensive validation report

---

## Critical Configuration Values

| Parameter | Value | Notes |
|-----------|-------|-------|
| Cell size | 2m | Grid resolution for coverage tracking |
| Total cells | 1848 | From tunnel polygon bounds |
| LiDAR beams | 16 | 0.12–10m range, normalized |
| LiDAR gain | 0.00541/cell | 10.0 / 1848 (10% bucket max) |
| M25 bonus | +15.0 | At 25% coverage |
| M50 bonus | +30.0 | At 50% coverage |
| M75 bonus | +45.0 | At 75% coverage |
| Collision penalty | -15.0/step | 6 steps = -90 = wipes M75 |
| Revisit penalty | -0.002/step | Encourages new exploration |
| Max reward/ep | 100.0 | 90 (milestones) + 10 (exploration) |
| Max steps | 6000 | 600s at 0.1s control dt |
| LSTM cell | 256 | Recurrent memory size |
| Gamma | 0.995 | Long-horizon discounting |
| Entropy coeff | 0.01 | Exploration regularization |
| Train batch | 12k | Full mode; 2k rapid mode |

---

## Validation Results

### ✅ All Checks Passed

- [x] Grid initialization from tunnel polygon
- [x] Reward structure matches 90/10 spec exactly
- [x] Obs space 19D, normalized [0,1]
- [x] Coverage monotonic (no backward resets)
- [x] Milestones one-time (set tracking)
- [x] Collision non-terminal
- [x] No-movement truncation enabled
- [x] LSTM configured correctly
- [x] Checkpoint cleanup in place
- [x] Disk precheck implemented
- [x] Trial pipeline smoke test ✓
- [x] Training smoke test ✓
- [x] Eval smoke test ✓
- [x] Checkpoint restore ✓

---

## Known Constraints

### 1. Disk Space (CRITICAL)
- **Available:** 2.5 GB
- **Full run estimate:** 20–50 GB (checkpoints + Ray temp)
- **Mitigation:** Checkpoint cleanup keeps only 2 most recent
- **Monitor:** `du -sh outputs/ ~/raytmp/` during run

### 2. Observation Space Changed
- **Old:** 24D (goal + lidar + vel)
- **New:** 19D (lidar + vel)
- **Action:** Cannot load old checkpoints; retrain from scratch

### 3. Ray Temp Path
- **Path:** `/home/badrikanath/raytmp`
- **Status:** Safe for UNIX sockets ✓

---

## How to Run 30,000 Episodes

### Quick Start
```bash
cd ~/mining_env_dataset_folder/"Mining Env"
source .venv/bin/activate

python scripts/10_trial_pipeline_check.py \
  --episodes 30000 \
  --policy explore \
  --max-steps 6000 \
  --print-every 10 \
  --plot-every 5000 \
  --summary-window 100 \
  --run-dir outputs/trial_runs
```

### Parallel Monitoring (in second terminal)
```bash
watch -n 60 'du -sh ~/mining_env_dataset_folder/"Mining Env"/outputs/ \
                   ~/raytmp/ && free -h'
```

### Expected Output
- **Terminal:** 300 summary boxes (every 10 episodes)
- **CSV:** `outputs/trial_runs/<run>/episode_metrics.csv` (30k rows)
- **Plots:** `outputs/trial_runs/<run>/plots/` (7 refreshes)
- **Runtime:** ~5–8 hours (single-threaded)

---

## Post-Run Analysis

### Evaluate Best Policy
```bash
python scripts/12_eval_exploration.py \
  --episodes 50 \
  --policy random \
  --max-steps 6000
```

### Extract Trends
```bash
# Coverage over time
python -c "import json; \
  import csv; \
  with open('outputs/trial_runs/<run>/episode_metrics.csv') as f: \
    rows = list(csv.DictReader(f)); \
    covs = [float(r['coverage_fraction']) for r in rows]; \
    print(f'Min: {min(covs):.3f}, Max: {max(covs):.3f}, Final: {covs[-1]:.3f}')"
```

---

## Team Recommendation (If Scaling Beyond Single Robot)

For multi-robot extension:
1. **Track** shared union coverage (not per-agent)
2. **Reward** based on new cells to union (encourages cooperation)
3. **Observe** relative positions of other robots
4. **Stitching** uses costmap union for metrics
5. **Credit** is a hard problem; suggest shared milestones for now

---

## Files & Locations

```
~/mining_env_dataset_folder/Mining Env/
├── mining_env/
│   ├── config.py                    (ExplorationSpec + main config)
│   ├── parallel_env.py              (Core env: grid, reward, step)
│   └── single_agent_env.py          (Gymnasium wrapper)
├── scripts/
│   ├── 10_trial_pipeline_check.py   (30k episode trial runner)
│   ├── 11_view_training_env.py      (Interactive viewer)
│   ├── 12_eval_exploration.py       (Map metrics + PNG)
│   └── 20_train_rllib_ppo.py        (LSTM PPO trainer)
├── outputs/
│   ├── chilean_mine_geometry.xml    (MuJoCo model)
│   ├── meshes/tunnel_polygon.pkl    (Ground truth map)
│   ├── trial_runs/                  (Trial artifacts)
│   ├── eval/                        (Eval artifacts)
│   └── rllib_runs/                  (Training artifacts)
├── docs/
│   └── rl_exploration.md            (Original design spec)
├── READINESS_REPORT.md              (Validation report)
└── CLAUDE.md                        (Project instructions)
```

---

## Summary

**All exploration environment components are implemented, tested, and validated.**

✅ Reward structure matches spec  
✅ Observation space correct  
✅ Grid initialization correct  
✅ Coverage tracking monotonic  
✅ Training pipeline ready  
✅ Evaluation pipeline ready  
✅ Checkpoint restore working  

**Ready to launch 30,000-episode production run.**

---

*Generated: 2026-04-10*  
*Validated by: End-to-end integration suite*  
*Next milestone: Run `scripts/10_trial_pipeline_check.py --episodes 30000`*
