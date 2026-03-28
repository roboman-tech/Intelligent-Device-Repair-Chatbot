from typing import Literal

DeviceType = Literal["mobile", "laptop", "desktop", "tablet", "generic"]
RiskLevel = Literal["low", "medium", "high"]
IntentType = Literal[
    "troubleshoot",
    "repair_step",
    "explain",
    "urgent_danger",
    "service",
]
