#!/usr/bin/env python3
"""
RL Training Script for Mining Environment
=========================================

This script runs a 30,000-episode exploration trial with the mining environment.
Results are saved to outputs/trial_runs/ in the current working directory.

Usage:
    python rl_training.py

    # Or with custom parameters:
    python rl_training.py --episodes 5000 --policy explore --max-steps 6000

Dependencies:
    - mujoco, pettingzoo, gymnasium, ray[rllib], opencv-python, shapely, trimesh, tensorboardX, matplotlib

Output Structure:
    outputs/trial_runs/<run_id>/
    ├── episode_metrics.csv       (23 columns × N episodes)
    ├── summary.json              (aggregated stats)
    ├── plots/
    │   ├── trends/              (reward, coverage curves)
    │   └── rates/               (success/collision rates)
    └── tensorboard/             (event logs)
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from dataclasses import replace
from pathlib import Path
from statistics import mean

import matplotlib
# Use a headless backend to avoid Tkinter teardown errors in long runs.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from tensorboardX import SummaryWriter

# Allow running this script directly from scripts/ while importing project modules.
REPO_ROOT = Path(__file__).resolve().parent / "Mining Env"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mining_env.config import EnvConfig
from mining_env.parallel_env import MiningParallelEnv


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="RL Training: 30,000-episode exploration trial"
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=30000,
        help="Number of episodes to run (default: 30000)"
    )
    parser.add_argument(
        "--num-agents",
        type=int,
        default=1,
        help="Number of agents per episode (default: 1)"
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=6000,
        help="Maximum steps per episode (default: 6000)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)"
    )
    parser.add_argument(
        "--policy",
        type=str,
        default="explore",
        choices=["random", "explore"],
        help="Action policy: 'random' or 'explore' (wall-avoidance)"
    )
    parser.add_argument(
        "--print-every",
        type=int,
        default=10,
        help="Print summary every N episodes (default: 10)"
    )
    parser.add_argument(
        "--plot-every",
        type=int,
        default=5000,
        help="Refresh plots every N episodes (default: 5000)"
    )
    parser.add_argument(
        "--summary-window",
        type=int,
        default=100,
        help="Window size for rolling summary (default: 100)"
    )
    parser.add_argument(
        "--run-dir",
        type=str,
        default="outputs/trial_runs",
        help="Base output directory (default: outputs/trial_runs)"
    )
    return parser.parse_args()


def rolling_mean(values: list[float], window: int) -> list[float]:
    """Calculate rolling mean over a window."""
    out = []
    for i in range(len(values)):
        lo = max(0, i - window + 1)
        out.append(float(mean(values[lo : i + 1])))
    return out


def summarize(rows: list[dict]) -> dict:
    """Aggregate statistics from episode rows."""
    if not rows:
        return {}

    def avg(key: str) -> float:
        return float(mean(float(r[key]) for r in rows))

    return {
        "episodes": len(rows),
        "avg_reward_total": avg("reward_total"),
        "avg_reward_per_step": avg("reward_per_step"),
        "avg_episode_length": avg("episode_length"),
        "avg_coverage_fraction": avg("coverage_fraction"),
        "avg_coverage_auc": avg("coverage_auc"),
        "avg_new_cells_total": avg("new_cells_total"),
        "avg_collision_steps": avg("collision_steps"),
        "timeout_rate": avg("timeout"),
        "no_movement_trunc_rate": avg("no_movement_truncated"),
        "collision_limit_trunc_rate": avg("collision_limit_truncated"),
        "milestone_25_rate": avg("milestone_25_reached"),
        "milestone_50_rate": avg("milestone_50_reached"),
        "milestone_75_rate": avg("milestone_75_reached"),
    }


def format_summary_box(summary: dict, title: str) -> str:
    """Format summary stats as a box."""
    lines = [
        f"{title}",
        f"episodes             : {summary.get('episodes', 0)}",
        f"avg_reward_total     : {summary.get('avg_reward_total', 0.0):.3f}",
        f"avg_reward_per_step  : {summary.get('avg_reward_per_step', 0.0):.5f}",
        f"avg_episode_length   : {summary.get('avg_episode_length', 0.0):.1f}",
        f"avg_coverage_fraction: {summary.get('avg_coverage_fraction', 0.0):.3f}",
        f"avg_coverage_auc     : {summary.get('avg_coverage_auc', 0.0):.3f}",
        f"avg_new_cells_total  : {summary.get('avg_new_cells_total', 0.0):.1f}",
        f"avg_collision_steps  : {summary.get('avg_collision_steps', 0.0):.2f}",
        f"collision_limit_rate : {summary.get('collision_limit_trunc_rate', 0.0):.3f}",
        f"milestone_75_rate    : {summary.get('milestone_75_rate', 0.0):.3f}",
    ]
    width = max(len(line) for line in lines) + 2
    top = "+" + "-" * width + "+"
    body = ["| " + line.ljust(width - 1) + "|" for line in lines]
    return "\n".join([top, *body, top])


def _save_single_metric_plot(
    episodes: list[int],
    values: list[float],
    ma_values: list[float] | None,
    out_path: Path,
    title: str,
    ylabel: str,
    summary_text: str | None = None,
    ylim: tuple[float, float] | None = None,
) -> None:
    """Save a single metric plot to PNG."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 4), dpi=140)
    ax.plot(episodes, values, alpha=0.30, label="episode")
    if ma_values is not None:
        ax.plot(episodes, ma_values, linewidth=2, label="moving avg")
    ax.set_title(title)
    ax.set_xlabel("Episode")
    ax.set_ylabel(ylabel)
    if ylim is not None:
        ax.set_ylim(*ylim)
    ax.grid(alpha=0.25)
    ax.legend(loc="upper left")

    if summary_text:
        ax.text(
            0.98,
            0.03,
            summary_text,
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=9,
            bbox={"facecolor": "white", "alpha": 0.88, "edgecolor": "gray"},
        )

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def make_plots(rows: list[dict], plot_root: Path, summary_window: int = 100) -> None:
    """Generate and save all metric plots."""
    if not rows:
        return

    trends_dir = plot_root / "trends"
    rates_dir = plot_root / "rates"
    for d in (trends_dir, rates_dir):
        d.mkdir(parents=True, exist_ok=True)

    ep = [int(r["episode"]) for r in rows]
    rew = [float(r["reward_total"]) for r in rows]
    rew_per_step = [float(r["reward_per_step"]) for r in rows]
    coverage = [float(r["coverage_fraction"]) for r in rows]
    coverage_auc = [float(r["coverage_auc"]) for r in rows]
    length = [float(r["episode_length"]) for r in rows]
    new_cells = [float(r["new_cells_total"]) for r in rows]
    collisions = [float(r["collision_steps"]) for r in rows]

    m25 = [float(r["milestone_25_reached"]) for r in rows]
    m50 = [float(r["milestone_50_reached"]) for r in rows]
    m75 = [float(r["milestone_75_reached"]) for r in rows]
    timeout = [float(r["timeout"]) for r in rows]

    tail = rows[-summary_window:]
    tail_summary = summarize(tail)
    summary_text = (
        f"Last {summary_window} eps\n"
        f"cov={tail_summary.get('avg_coverage_fraction', 0.0):.3f}\n"
        f"cov_auc={tail_summary.get('avg_coverage_auc', 0.0):.3f}\n"
        f"rew={tail_summary.get('avg_reward_total', 0.0):.2f}\n"
        f"len={tail_summary.get('avg_episode_length', 0.0):.1f}\n"
        f"m75={tail_summary.get('milestone_75_rate', 0.0):.2f}"
    )

    _save_single_metric_plot(
        ep,
        rew,
        rolling_mean(rew, summary_window),
        trends_dir / "reward_total.png",
        "Reward Total",
        "Reward",
        summary_text=summary_text,
    )
    _save_single_metric_plot(
        ep,
        rew_per_step,
        rolling_mean(rew_per_step, summary_window),
        trends_dir / "reward_per_step.png",
        "Reward Per Step",
        "Reward/Step",
        summary_text=summary_text,
    )
    _save_single_metric_plot(
        ep,
        coverage,
        rolling_mean(coverage, summary_window),
        trends_dir / "coverage_fraction.png",
        "Final Coverage Fraction",
        "Coverage",
        summary_text=summary_text,
        ylim=(-0.02, 1.02),
    )
    _save_single_metric_plot(
        ep,
        coverage_auc,
        rolling_mean(coverage_auc, summary_window),
        trends_dir / "coverage_auc.png",
        "Coverage AUC (Per Episode)",
        "AUC",
        summary_text=summary_text,
        ylim=(-0.02, 1.02),
    )
    _save_single_metric_plot(
        ep,
        length,
        rolling_mean(length, summary_window),
        trends_dir / "episode_length.png",
        "Episode Length",
        "Steps",
        summary_text=summary_text,
    )
    _save_single_metric_plot(
        ep,
        new_cells,
        rolling_mean(new_cells, summary_window),
        trends_dir / "new_cells_total.png",
        "New Cells Seen Per Episode",
        "Cells",
        summary_text=summary_text,
    )
    _save_single_metric_plot(
        ep,
        collisions,
        rolling_mean(collisions, summary_window),
        trends_dir / "collision_steps.png",
        "Collision Steps Per Episode",
        "Steps",
        summary_text=summary_text,
    )

    _save_single_metric_plot(
        ep,
        m25,
        rolling_mean(m25, summary_window),
        rates_dir / "milestone_25_rate.png",
        "Milestone 25% Hit Rate",
        "Rate",
        summary_text=summary_text,
        ylim=(-0.02, 1.02),
    )
    _save_single_metric_plot(
        ep,
        m50,
        rolling_mean(m50, summary_window),
        rates_dir / "milestone_50_rate.png",
        "Milestone 50% Hit Rate",
        "Rate",
        summary_text=summary_text,
        ylim=(-0.02, 1.02),
    )
    _save_single_metric_plot(
        ep,
        m75,
        rolling_mean(m75, summary_window),
        rates_dir / "milestone_75_rate.png",
        "Milestone 75% Hit Rate",
        "Rate",
        summary_text=summary_text,
        ylim=(-0.02, 1.02),
    )
    _save_single_metric_plot(
        ep,
        timeout,
        rolling_mean(timeout, summary_window),
        rates_dir / "timeout_rate.png",
        "Timeout/Truncation Rate",
        "Rate",
        summary_text=summary_text,
        ylim=(-0.02, 1.02),
    )


def explore_action(obs: np.ndarray) -> np.ndarray:
    """
    Lightweight reactive exploration baseline without goal features.

    Strategy: Wall-avoidance heuristic
    - Move forward if path is clear
    - Turn left/right based on left/right wall distances
    """
    lidar = np.asarray(obs[:16], dtype=np.float32)
    if lidar.size == 0:
        return np.array([0.0, 0.0], dtype=np.float32)

    n = int(lidar.size)
    front = min(float(lidar[0]), float(lidar[min(1, n - 1)]), float(lidar[-1]))

    q = max(1, n // 4)
    left_idx = [min(n - 1, q), min(n - 1, q + 1)]
    right_center = min(n - 1, 3 * q)
    right_idx = [right_center, min(n - 1, right_center + 1)]

    left = float(sum(float(lidar[i]) for i in left_idx))
    right = float(sum(float(lidar[i]) for i in right_idx))

    vel = 1.0 if front > 0.5 else 0.3
    omega = 0.5 * (left - right)

    return np.array([vel, omega], dtype=np.float32)


def run_episode(env: MiningParallelEnv, policy: str) -> dict:
    """Run a single episode and return metrics."""
    observations, infos = env.reset()
    _ = infos

    episode_reward = 0.0
    coverage_curve = []
    terminal_infos = []

    while env.agents:
        if policy == "explore":
            actions = {a: explore_action(observations[a]) for a in env.agents}
        else:
            actions = {a: env.action_space(a).sample() for a in env.agents}

        observations, rewards, _terms, _truncs, infos = env.step(actions)

        if rewards:
            episode_reward += float(mean(rewards.values()))

        for info in infos.values():
            coverage_curve.append(float(info.get("coverage_fraction", 0.0)))
            ep = info.get("episode")
            if ep is not None:
                terminal_infos.append(ep)

    if not terminal_infos:
        return {
            "reward_total": float(episode_reward),
            "reward_per_step": 0.0,
            "episode_length": 0.0,
            "max_steps_budget": float(env.config.max_steps),
            "budget_utilization": 0.0,
            "coverage_fraction": 0.0,
            "coverage_auc": 0.0,
            "cells_seen_count": 0,
            "total_tunnel_cells": int(env._total_tunnel_cells),
            "new_cells_total": 0,
            "avg_new_cells_per_step": 0.0,
            "collision_steps": 0,
            "timeout": 1,
            "no_movement_truncated": 0,
            "collision_limit_truncated": 0,
            "milestone_25_reached": 0,
            "milestone_50_reached": 0,
            "milestone_75_reached": 0,
        }

    row = {
        "reward_total": float(mean(float(ep["reward_total"]) for ep in terminal_infos)),
        "episode_length": float(mean(float(ep["steps"]) for ep in terminal_infos)),
        "max_steps_budget": float(
            mean(float(ep.get("max_steps_budget", env.config.max_steps)) for ep in terminal_infos)
        ),
        "coverage_fraction": float(mean(float(ep["coverage_fraction"]) for ep in terminal_infos)),
        "cells_seen_count": int(mean(int(ep["cells_seen_count"]) for ep in terminal_infos)),
        "total_tunnel_cells": int(mean(int(ep["total_tunnel_cells"]) for ep in terminal_infos)),
        "new_cells_total": int(mean(int(ep["new_cells_total"]) for ep in terminal_infos)),
        "avg_new_cells_per_step": float(
            mean(float(ep["avg_new_cells_per_step"]) for ep in terminal_infos)
        ),
        "collision_steps": int(mean(int(ep["collision_steps"]) for ep in terminal_infos)),
        "timeout": int(mean(int(ep["timeout"]) for ep in terminal_infos) >= 0.5),
        "no_movement_truncated": int(
            mean(int(ep["no_movement_truncated"]) for ep in terminal_infos) >= 0.5
        ),
        "collision_limit_truncated": int(
            mean(int(ep.get("collision_terminated", ep.get("collision_limit_truncated", 0))) for ep in terminal_infos) >= 0.5
        ),
        "milestone_25_reached": int(
            mean(int(ep["milestone_25_reached"]) for ep in terminal_infos) >= 0.5
        ),
        "milestone_50_reached": int(
            mean(int(ep["milestone_50_reached"]) for ep in terminal_infos) >= 0.5
        ),
        "milestone_75_reached": int(
            mean(int(ep["milestone_75_reached"]) for ep in terminal_infos) >= 0.5
        ),
    }

    row["reward_per_step"] = float(row["reward_total"] / max(row["episode_length"], 1.0))
    row["budget_utilization"] = float(row["episode_length"] / max(row["max_steps_budget"], 1.0))
    row["coverage_auc"] = float(np.mean(coverage_curve)) if coverage_curve else 0.0

    return row


def main() -> None:
    """Main training loop."""
    args = parse_args()

    run_root = Path(args.run_dir)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = run_root / f"trial_{stamp}"
    plot_dir = run_dir / "plots"
    run_dir.mkdir(parents=True, exist_ok=True)
    plot_dir.mkdir(parents=True, exist_ok=True)

    csv_path = run_dir / "episode_metrics.csv"
    summary_path = run_dir / "summary.json"
    tb_dir = run_dir / "tensorboard"

    cfg = EnvConfig(num_agents=args.num_agents, max_steps=args.max_steps)
    cfg.spawn = replace(cfg.spawn, spawn_mode="region_a")
    env = MiningParallelEnv(cfg)
    env._rng = np.random.default_rng(args.seed)

    writer = SummaryWriter(logdir=str(tb_dir), flush_secs=10)

    fieldnames = [
        "episode",
        "reward_total",
        "reward_per_step",
        "episode_length",
        "max_steps_budget",
        "budget_utilization",
        "coverage_fraction",
        "coverage_auc",
        "cells_seen_count",
        "total_tunnel_cells",
        "new_cells_total",
        "avg_new_cells_per_step",
        "collision_steps",
        "timeout",
        "no_movement_truncated",
        "collision_limit_truncated",
        "milestone_25_reached",
        "milestone_50_reached",
        "milestone_75_reached",
    ]

    rows = []

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        csv_writer = csv.DictWriter(f, fieldnames=fieldnames)
        csv_writer.writeheader()

        print("=" * 80)
        print("RL Training: Exploration Trial Pipeline")
        print("=" * 80)
        print(f"Run dir                : {run_dir}")
        print(f"Episodes               : {args.episodes}")
        print(f"Agents                 : {args.num_agents}")
        print(f"Max steps/episode      : {args.max_steps}")
        print(f"Policy                 : {args.policy}")
        print(f"Terminal print interval: {args.print_every} episodes")
        print(f"Plot save interval     : {args.plot_every} episodes")
        print(f"Summary window         : {args.summary_window} episodes")
        print("=" * 80)
        print()

        for ep in range(1, args.episodes + 1):
            row = run_episode(env, policy=args.policy)
            row["episode"] = ep
            rows.append(row)
            csv_writer.writerow(row)
            f.flush()

            writer.add_scalar("episode/reward_total", row["reward_total"], ep)
            writer.add_scalar("episode/reward_per_step", row["reward_per_step"], ep)
            writer.add_scalar("episode/episode_length", row["episode_length"], ep)
            writer.add_scalar("episode/coverage_fraction", row["coverage_fraction"], ep)
            writer.add_scalar("episode/coverage_auc", row["coverage_auc"], ep)
            writer.add_scalar("episode/new_cells_total", row["new_cells_total"], ep)
            writer.add_scalar("episode/collision_steps", row["collision_steps"], ep)
            writer.add_scalar("episode/milestone_25_reached", row["milestone_25_reached"], ep)
            writer.add_scalar("episode/milestone_50_reached", row["milestone_50_reached"], ep)
            writer.add_scalar("episode/milestone_75_reached", row["milestone_75_reached"], ep)
            writer.add_scalar("episode/timeout", row["timeout"], ep)
            writer.add_scalar("episode/no_movement_truncated", row["no_movement_truncated"], ep)
            writer.add_scalar("episode/collision_limit_truncated", row["collision_limit_truncated"], ep)

            if ep % args.print_every == 0:
                tail = rows[-args.summary_window :]
                tail_summary = summarize(tail)
                print(
                    f"[ep {ep:5d}] "
                    f"reward={row['reward_total']:8.3f} "
                    f"coverage={row['coverage_fraction']:.3f} "
                    f"new_cells={row['new_cells_total']:5d} "
                    f"coll_steps={row['collision_steps']:4d}"
                )
                print(format_summary_box(tail_summary, f"Last {len(tail)} Episodes Summary"))
                print()

            if ep % args.plot_every == 0:
                make_plots(rows, plot_dir, summary_window=args.summary_window)
                print(f"[ep {ep:5d}] plots refreshed at {plot_dir}")
                print()

    # Always save final plots even if episodes is not a multiple of plot interval.
    make_plots(rows, plot_dir, summary_window=args.summary_window)

    final_summary = summarize(rows)
    final_summary["run_dir"] = str(run_dir)
    final_summary["episodes_requested"] = int(args.episodes)
    final_summary["num_agents"] = int(args.num_agents)
    final_summary["max_steps"] = int(args.max_steps)
    final_summary["policy"] = args.policy
    final_summary["print_every"] = int(args.print_every)
    final_summary["plot_every"] = int(args.plot_every)
    final_summary["summary_window"] = int(args.summary_window)

    tail = rows[-args.summary_window :] if rows else []
    final_summary["last_window"] = summarize(tail)

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(final_summary, f, indent=2)

    writer.flush()
    writer.close()
    env.close()

    print("\n" + "=" * 80)
    print("Trial complete!")
    print("=" * 80)
    print(f"CSV metrics : {csv_path}")
    print(f"Summary JSON: {summary_path}")
    print(f"TensorBoard : {tb_dir}")
    print(f"Plots       : {plot_dir}")
    print()
    print("Launch TensorBoard with:")
    print(f"  tensorboard --logdir {tb_dir} --port 6006")
    print()


if __name__ == "__main__":
    main()
