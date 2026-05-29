#!/bin/bash
# Run RL Training Script for Mining Environment
# This script sets up the environment and runs the training

set -e

cd "$(dirname "$0")"

echo "========================================================================"
echo "Mining Environment - RL Training Script"
echo "========================================================================"
echo ""

# Check if Mining Env folder exists
if [ ! -d "Mining Env" ]; then
    echo "ERROR: Mining Env folder not found in $(pwd)"
    echo "Please ensure you're in ~/mining_env_dataset_folder/"
    exit 1
fi

# Activate virtual environment
if [ ! -f "Mining Env/.venv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found at Mining Env/.venv/bin/activate"
    echo "Please ensure Python environment is initialized"
    exit 1
fi

cd Mining\ Env
source .venv/bin/activate
cd ..

PYTHON_BIN="$(python -c 'import sys; print(sys.executable)')"
if [[ "$PYTHON_BIN" == *" "* ]]; then
    ACTIVE_VENV="$(python -c 'import sys; print(sys.prefix)')"
    SAFE_VENV_LINK="/tmp/mining_env_venv_$(id -u)"
    ln -sfn "$ACTIVE_VENV" "$SAFE_VENV_LINK"
    PYTHON_BIN="$SAFE_VENV_LINK/bin/python"
fi

echo "✓ Environment activated"
echo "✓ Python executable: $PYTHON_BIN"
echo "✓ Working directory: $(pwd)"
echo ""

# PPO-only launcher (legacy heuristic trial pipeline intentionally disabled).
ENGINE="ppo"
ARGS=()
EPISODES_VALUE=""
TOTAL_EPISODES_SEEN=0
MODE_SEEN=0
RAY_TEMP_SEEN=0
NUM_WORKERS_SEEN=0
TRAIN_BATCH_SEEN=0
SGD_MINIBATCH_SEEN=0
POLICY_MODEL_SEEN=0
TORCH_THREADS_SEEN=0
WORKER_BLAS_THREADS_SEEN=0
NUM_ENVS_PER_WORKER_SEEN=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --engine)
            if [[ $# -lt 2 ]]; then
                echo "ERROR: --engine requires a value: ppo"
                exit 1
            fi
            ENGINE="$2"
            if [[ "$ENGINE" != "ppo" ]]; then
                echo "ERROR: Unsupported engine '$ENGINE'. Only 'ppo' is allowed."
                exit 1
            fi
            shift 2
            ;;
        --engine=*)
            ENGINE="${1#*=}"
            if [[ "$ENGINE" != "ppo" ]]; then
                echo "ERROR: Unsupported engine '$ENGINE'. Only 'ppo' is allowed."
                exit 1
            fi
            shift
            ;;
        --episodes)
            if [[ $# -lt 2 ]]; then
                echo "ERROR: --episodes requires a numeric value"
                exit 1
            fi
            EPISODES_VALUE="$2"
            shift 2
            ;;
        --episodes=*)
            EPISODES_VALUE="${1#*=}"
            shift
            ;;
        --total-episodes|--total-episodes=*)
            TOTAL_EPISODES_SEEN=1
            ARGS+=("$1")
            if [[ "$1" == "--total-episodes" && $# -ge 2 ]]; then
                ARGS+=("$2")
                shift 2
            else
                shift
            fi
            ;;
        --mode|--mode=*)
            MODE_SEEN=1
            ARGS+=("$1")
            if [[ "$1" == "--mode" && $# -ge 2 ]]; then
                ARGS+=("$2")
                shift 2
            else
                shift
            fi
            ;;
        --ray-temp-dir|--ray-temp-dir=*)
            RAY_TEMP_SEEN=1
            ARGS+=("$1")
            if [[ "$1" == "--ray-temp-dir" && $# -ge 2 ]]; then
                ARGS+=("$2")
                shift 2
            else
                shift
            fi
            ;;
        --num-workers|--num-workers=*)
            NUM_WORKERS_SEEN=1
            ARGS+=("$1")
            if [[ "$1" == "--num-workers" && $# -ge 2 ]]; then
                ARGS+=("$2")
                shift 2
            else
                shift
            fi
            ;;
        --train-batch-size|--train-batch-size=*)
            TRAIN_BATCH_SEEN=1
            ARGS+=("$1")
            if [[ "$1" == "--train-batch-size" && $# -ge 2 ]]; then
                ARGS+=("$2")
                shift 2
            else
                shift
            fi
            ;;
        --sgd-minibatch-size|--sgd-minibatch-size=*)
            SGD_MINIBATCH_SEEN=1
            ARGS+=("$1")
            if [[ "$1" == "--sgd-minibatch-size" && $# -ge 2 ]]; then
                ARGS+=("$2")
                shift 2
            else
                shift
            fi
            ;;
        --policy-model|--policy-model=*)
            POLICY_MODEL_SEEN=1
            ARGS+=("$1")
            if [[ "$1" == "--policy-model" && $# -ge 2 ]]; then
                ARGS+=("$2")
                shift 2
            else
                shift
            fi
            ;;
        --torch-num-threads|--torch-num-threads=*)
            TORCH_THREADS_SEEN=1
            ARGS+=("$1")
            if [[ "$1" == "--torch-num-threads" && $# -ge 2 ]]; then
                ARGS+=("$2")
                shift 2
            else
                shift
            fi
            ;;
        --worker-blas-threads|--worker-blas-threads=*)
            WORKER_BLAS_THREADS_SEEN=1
            ARGS+=("$1")
            if [[ "$1" == "--worker-blas-threads" && $# -ge 2 ]]; then
                ARGS+=("$2")
                shift 2
            else
                shift
            fi
            ;;
        --num-envs-per-worker|--num-envs-per-worker=*)
            NUM_ENVS_PER_WORKER_SEEN=1
            ARGS+=("$1")
            if [[ "$1" == "--num-envs-per-worker" && $# -ge 2 ]]; then
                ARGS+=("$2")
                shift 2
            else
                shift
            fi
            ;;
        *)
            ARGS+=("$1")
            shift
            ;;
    esac
done

TRAIN_SCRIPT="Mining Env/scripts/20_train_rllib_ppo.py"

if [ ! -f "$TRAIN_SCRIPT" ]; then
    echo "ERROR: Missing training script: $TRAIN_SCRIPT"
    exit 1
fi

# Check critical files
if [ ! -f "Mining Env/mining_env/config.py" ]; then
    echo "ERROR: Missing critical file: Mining Env/mining_env/config.py"
    exit 1
fi

resolve_required_file() {
    local label="$1"
    shift
    for candidate in "$@"; do
        if [ -f "$candidate" ]; then
            echo "$candidate"
            return 0
        fi
    done
    echo "ERROR: Missing critical $label file. Tried: $*" >&2
    exit 1
}

XML_FILE="$(resolve_required_file "xml" \
    "Mining Env/mining information xml/chilean_mine_geometry.xml" \
    "Mining Env/outputs/chilean_mine_geometry.xml")"

POLY_FILE="$(resolve_required_file "polygon" \
    "Mining Env/mining information xml/meshes/tunnel_polygon.pkl" \
    "Mining Env/outputs/meshes/tunnel_polygon.pkl")"

if [[ "$ENGINE" == "ppo" ]]; then
    if [[ $MODE_SEEN -eq 0 ]]; then
        ARGS+=("--mode" "full")
    fi
    if [[ $NUM_WORKERS_SEEN -eq 0 ]]; then
        ARGS+=("--num-workers" "2")
    fi
    if [[ $TRAIN_BATCH_SEEN -eq 0 ]]; then
        ARGS+=("--train-batch-size" "6000")
    fi
    if [[ $SGD_MINIBATCH_SEEN -eq 0 ]]; then
        ARGS+=("--sgd-minibatch-size" "512")
    fi
    if [[ $POLICY_MODEL_SEEN -eq 0 ]]; then
        ARGS+=("--policy-model" "mlp")
    fi
    if [[ $TORCH_THREADS_SEEN -eq 0 ]]; then
        ARGS+=("--torch-num-threads" "4")
    fi
    if [[ $WORKER_BLAS_THREADS_SEEN -eq 0 ]]; then
        ARGS+=("--worker-blas-threads" "1")
    fi
    if [[ $NUM_ENVS_PER_WORKER_SEEN -eq 0 ]]; then
        ARGS+=("--num-envs-per-worker" "1")
    fi
    if [[ -n "$EPISODES_VALUE" && $TOTAL_EPISODES_SEEN -eq 0 ]]; then
        ARGS+=("--total-episodes" "$EPISODES_VALUE")
    fi
    if [[ $RAY_TEMP_SEEN -eq 0 ]]; then
        if [[ -d "/dev/shm" ]]; then
            ARGS+=("--ray-temp-dir" "/dev/shm/mining_raytmp")
        else
            ARGS+=("--ray-temp-dir" "Mining Env/outputs/raytmp")
        fi
    fi
    ARGS+=(
        "--xml-path" "mining information xml/chilean_mine_geometry.xml"
        "--tunnel-polygon-pkl" "mining information xml/meshes/tunnel_polygon.pkl"
    )
fi

echo "✓ All critical files present"
echo "✓ Engine: $ENGINE"
echo "✓ XML asset: $XML_FILE"
echo "✓ Polygon asset: $POLY_FILE"
echo "✓ Ready to run training"
echo ""

# Run the training script with all arguments passed through
echo "========================================================================"
echo "Starting RL Training..."
echo "========================================================================"
echo ""

"$PYTHON_BIN" -u "$TRAIN_SCRIPT" "${ARGS[@]}"

echo ""
echo "========================================================================"
echo "Training Complete!"
echo "========================================================================"
