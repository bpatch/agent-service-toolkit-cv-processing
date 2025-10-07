from .state import AgentState
from typing import Literal
from ... import utils as ut


class Edges:

    def __init__(
        self,
        config,
    ):
        self.config = config

    def route_inappropriate(
        self, state: AgentState
    ) -> Literal["clean_up_inappropriate_cv", "first_cv_step"]:
        # If the cv is not appropriate for AI, then don't do any further
        # processing, route to a clean up function
        if state["cv_type"] == "not_ai_appropriate":
            return "clean_up_inappropriate_cv"
        else:
            return "first_cv_step"
