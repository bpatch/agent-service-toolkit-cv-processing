from typing import Optional
from typing_extensions import TypedDict


class AgentState(TypedDict):
    safe: bool
    calibration_scheduled: bool
    calibration_needed: bool
    related_applications: str
    prompt_injection: bool
