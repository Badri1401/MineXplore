#!/bin/bash
# Quick-start script for 30k episode exploration trial

set -e

cd "$(dirname "$0")/Mining Env"

echo "======================================================================"
echo "Mining Environment — 30,000 Episode Exploration Trial"
echo "======================================================================"

# Activate environment
if [ ! -f .venv/bin/activate ]; then
    echo "ERROR: Virtual environment not found at .venv/bin/activate"
    echo "Please ensure Python environment is initialized"
    exit 1
fi

source .venv/bin/activate
echo "✓ Environment activated"

# Check critical files
for file in \
    mining_env/config.py \
    scripts/10_trial_pipeline_check.py \
    outputs/chilean_mine_geometry.xml \
    outputs/meshes/tunnel_polygon.pkl; do
    if [ ! -f "$file" ]; then
        echo "ERROR: Missing critical file: $file"
        exit 1
    fi
done
echo "✓ All critical files present"

# Check disk space
FREE_GB=$(df . | tail -1 | awk '{print $4}')
FREE_GB=$((FREE_GB / 1024 / 1024))
echo "✓ Disk space available: ${FREE_GB} GB"

if [ "$FREE_GB" -lt 5 ]; then
    echo "WARNING: Only ${FREE_GB} GB available; full 30k run may fill disk"
    echo "Consider cleaning up old trials before starting"
fi

# Run the trial
echo ""
echo "======================================================================"
echo "Starting 30,000-episode exploration trial..."
echo "======================================================================"
echo ""

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="trial_30k_${TIMESTAMP}.log"

echo "Run parameters:"
echo "  Episodes: 30000"
echo "  Policy: explore (reactive wall-avoidance heuristic)"
echo "  Max steps/episode: 6000"
echo "  Print summaries: every 10 episodes"
echo "  Refresh plots: every 5000 episodes"
echo "  Summary window: 100 episodes"
echo ""
echo "Output log: $LOG_FILE"
echo ""

python -u scripts/10_trial_pipeline_check.py \
    --episodes 30000 \
    --policy explore \
    --max-steps 6000 \
    --print-every 10 \
    --plot-every 5000 \
    --summary-window 100 \
    --run-dir outputs/trial_runs \
    2>&1 | tee "$LOG_FILE"

echo ""
echo "======================================================================"
echo "Trial Complete!"
echo "======================================================================"
echo "Artifacts saved to outputs/trial_runs/"
echo "Log saved to: $LOG_FILE"
echo ""
echo "Next steps:"
echo "  1. Check coverage trends: less outputs/trial_runs/*/plots/"
echo "  2. Evaluate final map: python scripts/12_eval_exploration.py --episodes 50 --policy random"
echo "  3. Analyze CSV: head -20 outputs/trial_runs/*/episode_metrics.csv"
