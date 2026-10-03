"""
Telemetry Visualizer: Generates time-series CPU & Memory consumption charts.
"""

import logging
import os
from typing import Optional

import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt

from telemetry.monitor import TelemetryResult

logger = logging.getLogger("PulseQA.Visualizer")


class TelemetryVisualizer:
    """Renders high-resolution resource consumption plots."""

    @staticmethod
    def render_resource_chart(
        result: TelemetryResult,
        output_dir: str = "reports/telemetry",
        max_cpu_threshold: float | None = None,
        max_ram_threshold: float | None = None
    ) -> str:
        os.makedirs(output_dir, exist_ok=True)
        safe_name = "".join([c if c.isalnum() or c in ("-", "_") else "_" for c in result.test_name])
        output_path = os.path.join(output_dir, f"{safe_name}_resource_curve.png")

        if not result.samples:
            logger.warning(f"No samples to plot for {result.test_name}")
            return ""

        timestamps = [s.elapsed_sec for s in result.samples]
        cpus = [s.cpu_percent for s in result.samples]
        rams = [s.memory_rss_mb for s in result.samples]

        fig, ax1 = plt.subplots(figsize=(9, 4.5), dpi=120)
        fig.patch.set_facecolor("#0f172a")
        ax1.set_facecolor("#1e293b")

        # CPU curve (left axis)
        color_cpu = "#38bdf8"
        ax1.set_xlabel("Elapsed Time (seconds)", color="#94a3b8", fontsize=10, fontweight="bold")
        ax1.set_ylabel("CPU Usage (%)", color=color_cpu, fontsize=10, fontweight="bold")
        ax1.plot(timestamps, cpus, color=color_cpu, linewidth=2.0, label="CPU %", zorder=3)
        ax1.tick_params(axis="x", colors="#94a3b8")
        ax1.tick_params(axis="y", labelcolor=color_cpu)
        ax1.grid(True, linestyle="--", alpha=0.2, color="#94a3b8")
        ax1.set_ylim(bottom=0, top=max(max(cpus) * 1.25, 100))

        # Memory curve (right axis)
        ax2 = ax1.twinx()
        color_ram = "#f59e0b"
        ax2.set_ylabel("Memory RSS (MB)", color=color_ram, fontsize=10, fontweight="bold")
        ax2.plot(timestamps, rams, color=color_ram, linewidth=2.0, linestyle="-.", label="RAM (MB)", zorder=3)
        ax2.tick_params(axis="y", labelcolor=color_ram)
        ax2.set_ylim(bottom=0, top=max(rams) * 1.3 if rams else 100)

        # Threshold indicators
        if max_cpu_threshold:
            ax1.axhline(max_cpu_threshold, color="#ef4444", linestyle=":", linewidth=1.5, label=f"Max CPU SLA ({max_cpu_threshold}%)")
        if max_ram_threshold:
            ax2.axhline(max_ram_threshold, color="#dc2626", linestyle=":", linewidth=1.5, label=f"Max RAM SLA ({max_ram_threshold}MB)")

        # Title & Summary Badge
        plt.title(f"PulseQA Resource Telemetry: {result.test_name}", color="#f8fafc", fontsize=12, fontweight="bold", pad=12)
        summary_text = (
            f"Peak CPU: {result.peak_cpu_percent:.1f}% | Avg: {result.avg_cpu_percent:.1f}%\n"
            f"Peak RAM: {result.peak_memory_rss_mb:.1f}MB | Growth: {result.memory_growth_mb:+.1f}MB"
        )
        ax1.text(
            0.02, 0.95, summary_text,
            transform=ax1.transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#334155", edgecolor="#64748b", alpha=0.9),
            color="#f8fafc", fontsize=8
        )

        fig.tight_layout()
        plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close(fig)

        logger.info(f"Generated telemetry chart: {output_path}")
        return output_path
