"""
Chrome DevTools Protocol (CDP) Metrics Extractor.
Extracts internal V8 JS Heap, DOM Nodes, and Layout counts directly from the browser runtime.
"""

import logging
from typing import Any, Dict, Optional

from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger("PulseQA.CDPMetrics")


class CDPMetricsExtractor:
    """Extracts internal browser engine performance counters via CDP."""

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.is_supported = hasattr(driver, "execute_cdp_cmd")
        if self.is_supported:
            try:
                self.driver.execute_cdp_cmd("Performance.enable", {})
            except Exception as e:
                logger.debug(f"CDP Performance.enable failed: {e}")
                self.is_supported = False

    def get_browser_metrics(self) -> dict[str, Any]:
        if not self.is_supported:
            return {"supported": False}

        try:
            raw = self.driver.execute_cdp_cmd("Performance.getMetrics", {})
            metrics_dict = {m["name"]: m["value"] for m in raw.get("metrics", [])}

            js_heap_used_mb = round(metrics_dict.get("JSHeapUsedSize", 0) / (1024 * 1024), 2)
            js_heap_total_mb = round(metrics_dict.get("JSHeapTotalSize", 0) / (1024 * 1024), 2)
            dom_nodes = int(metrics_dict.get("Nodes", 0))
            layout_count = int(metrics_dict.get("LayoutCount", 0))

            return {
                "supported": True,
                "js_heap_used_mb": js_heap_used_mb,
                "js_heap_total_mb": js_heap_total_mb,
                "dom_nodes": dom_nodes,
                "layout_count": layout_count,
                "raw_metrics_count": len(metrics_dict)
            }
        except Exception as e:
            logger.warning(f"Failed to query CDP metrics: {e}")
            return {"supported": False, "error": str(e)}
