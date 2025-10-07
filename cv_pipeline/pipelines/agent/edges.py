from .state import AgentState
from typing import Literal
from ... import utils as ut
from langgraph.graph import END


class Edges:

    def __init__(
        self,
        config,
    ):
        self.config = config

    def route_safety(
        self, state: AgentState
    ) -> Literal["clean_up_unsafe_cv", "check_if_calibration_scheduled"]:
        # If the cv is not appropriate for AI, then don't do any further
        # processing, route to a clean up function
        if state["safe"]:
            return "check_if_calibration_scheduled"
        else:
            return "clean_up_unsafe_cv"

    def route_calibration_scheduled(
        self, state: AgentState
    ) -> Literal["retrieve_related_applications", END]:
        # If the cv is not appropriate for AI, then don't do any further
        # processing, route to a clean up function
        print(state)
        if state["calibration_scheduled"]:
            return END
        else:
            return "retrieve_related_applications"

    def route_calibration_needed(
        self, state: AgentState
    ) -> Literal["schedule_calibration", "assess_impression"]:
        # If the cv is not appropriate for AI, then don't do any further
        # processing, route to a clean up function
        if state["calibration_needed"]:
            return "schedule_calibration"
        else:
            return "assess_impression"

    def route_prompt_injection(
        self, state: AgentState
    ) -> Literal["clean_up_unsafe_cv", "final_summary"]:
        # If the cv is not appropriate for AI, then don't do any further
        # processing, route to a clean up function
        if state["prompt_injection"]:
            return "clean_up_unsafe_cv"
        else:
            return "final_summary"
