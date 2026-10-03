"""
Real-time Resource Consumption Monitor using psutil.
Monitors CPU %, Memory (RSS & VMS), and thread counts of process trees during test execution.
Directly substantiates the Resource Consumption Framework competency.
"""

import logging
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger("PulseQA.Telemetry")


@dataclass
class TelemetrySample:
    elapsed_sec: float
    cpu_percent: float
    memory_rss_mb: float
    memory_vms_mb: float
    thread_count: int


@dataclass
class TelemetryResult:
    test_name: str
    samples: list[TelemetrySample] = field(default_factory=list)
    peak_cpu_percent: float = 0.0
    avg_cpu_percent: float = 0.0
    start_memory_rss_mb: float = 0.0
    peak_memory_rss_mb: float = 0.0
    end_memory_rss_mb: float = 0.0
    memory_growth_mb: float = 0.0
    duration_sec: float = 0.0

    def compute_summary(self):
        if not self.samples:
            return
        cpus = [s.cpu_percent for s in self.samples]
        mems = [s.memory_rss_mb for s in self.samples]

        self.peak_cpu_percent = max(cpus)
        self.avg_cpu_percent = sum(cpus) / len(cpus)
        self.start_memory_rss_mb = mems[0]
        self.peak_memory_rss_mb = max(mems)
        self.end_memory_rss_mb = mems[-1]
        self.memory_growth_mb = self.end_memory_rss_mb - self.start_memory_rss_mb
        self.duration_sec = self.samples[-1].elapsed_sec


class ResourceMonitor:
    """Monitors CPU and memory metrics of a process and its child processes."""

    def __init__(self, target_pid: int | None = None, interval_sec: float = 0.2, test_name: str = "test"):
        self.target_pid = target_pid or os.getpid()
        self.interval_sec = interval_sec
        self.test_name = test_name
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._samples: list[TelemetrySample] = []
        self._start_time: float = 0.0
        self._result: TelemetryResult | None = None

    def start(self):
        self._samples.clear()
        self._stop_event.clear()
        self._result = None
        self._start_time = time.time()
        self._thread = threading.Thread(target=self._sampling_loop, daemon=True, name="ResourceMonitorThread")
        self._thread.start()
        logger.info(f"[Telemetry] Started resource tracking for PID {self.target_pid} (interval={self.interval_sec}s)")

    def stop(self) -> TelemetryResult:
        if self._result is not None:
            return self._result

        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=2.0)
            logger.info(f"[Telemetry] Stopped tracking for {self.test_name}. Collected {len(self._samples)} samples.")

        result = TelemetryResult(test_name=self.test_name, samples=list(self._samples))
        result.compute_summary()
        self._result = result
        return result

    def _sampling_loop(self):
        try:
            main_proc = psutil.Process(self.target_pid)
            # Warm up cpu_percent
            main_proc.cpu_percent(interval=None)
        except psutil.NoSuchProcess:
            logger.warning(f"[Telemetry] Target PID {self.target_pid} not found.")
            return

        while not self._stop_event.is_set():
            try:
                if not main_proc.is_running():
                    break

                # Collect from main process and all descendants
                procs = [main_proc]
                try:
                    procs.extend(main_proc.children(recursive=True))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

                total_cpu = 0.0
                total_rss_bytes = 0
                total_vms_bytes = 0
                total_threads = 0

                for p in procs:
                    try:
                        total_cpu += p.cpu_percent(interval=None)
                        mem_info = p.memory_info()
                        total_rss_bytes += mem_info.rss
                        total_vms_bytes += mem_info.vms
                        total_threads += p.num_threads()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                elapsed = time.time() - self._start_time
                sample = TelemetrySample(
                    elapsed_sec=round(elapsed, 3),
                    cpu_percent=round(total_cpu, 2),
                    memory_rss_mb=round(total_rss_bytes / (1024 * 1024), 2),
                    memory_vms_mb=round(total_vms_bytes / (1024 * 1024), 2),
                    thread_count=total_threads
                )
                self._samples.append(sample)

            except Exception as e:
                logger.debug(f"[Telemetry] Sample exception: {e}")

            time.sleep(self.interval_sec)
