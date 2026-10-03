"""
Custom Exception Hierarchy for PulseQA Framework.
"""

class FrameworkException(Exception):
    """Base exception for all PulseQA errors."""
    pass


class DriverInitializationError(FrameworkException):
    """Raised when WebDriver or AppiumDriver fails to initialize."""
    pass


class ElementTimeoutException(FrameworkException):
    """Raised when an explicit wait fails to locate or interact with an element."""
    pass


class ResourceThresholdExceededError(FrameworkException):
    """
    Raised when CPU % or RAM consumption violates defined performance thresholds.
    Directly supports the Resource Consumption Framework.
    """
    def __init__(self, metric_name: str, actual_value: float, threshold_value: float, test_name: str):
        self.metric_name = metric_name
        self.actual_value = actual_value
        self.threshold_value = threshold_value
        self.test_name = test_name
        super().__init__(
            f"Resource threshold breached in '{test_name}': {metric_name} reached "
            f"{actual_value:.2f} (Max permitted: {threshold_value:.2f})"
        )


class TestRailSyncError(FrameworkException):
    """Raised when synchronizing test results with TestRail fails."""
    pass
