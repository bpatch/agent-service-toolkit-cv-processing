from typing import Optional
from typing_extensions import TypedDict, Optional, List


class AgentState(TypedDict):
    position_number: str
    application_id: str
    suitability_automatic: str  # Y/N indication of CV suitability
    suitability_reasoning: str  # Short summary of reason for or against suitability
    invalid_reason: Optional[str]  # Reason the cv is not suitable for AI processing
    calibration_scheduled: (
        bool  # Indicator that sourcing historical position information is scheduled
    )
    calibration_needed: bool  # Indicator that not enough historical position information available to process
    suitability_comments_positive: str  # Historical comments for suitable applicants
    suitability_comments_negative: str  # Historical comments for unsuitable applicants
    prompt_injection: bool  # Indicator for signs of prompt injection
    cv_info: dict  # Details extracted from cv file
    cv_pdf_parts: list  # cv pdf image parts put here so only need to be processed once
    pd_pdf_parts: list  # pd pdf image parts put here so only need to be processed once
    preliminary_assessment: (
        bool  # Indicator of assessment before historical comments injected
    )
    preliminary_reasoning: (
        str  # Reasoning for assessment before historical comments injected
    )
    level: str  # Level of position
    similar_position_numbers: List[
        str
    ]  # Positions identified as similar to the one being applied for
    # preliminary_details: dict
