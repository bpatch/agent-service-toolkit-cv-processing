import logging
from .state import AgentState
import logging
from ... import utils as ut

log = logging.getLogger(__name__)


class Nodes:

    def __init__(
        self,
        config,
    ):
        self.config = config
        self.agent_system_prompt = """
        ### Persona ###
        You are an AI assistant who is an expert at evaluating cvs and resumes.
        """

    def classify_cv(
        self,
        state: AgentState,
    ) -> AgentState:
        logging.info("<ENTER NODE>classify_cv</ENTER NODE>")

        # Placeholder for business logic that determines what type of cv is
        # being processed
        cv_type = "everyday"

        logging.info("<EXIT NODE>classify_cv</EXIT NODE>")

        return {"cv_type": cv_type}

    def clean_up_inappropriate_cv(
        self,
        state: AgentState,
    ) -> AgentState:
        logging.info("<ENTER NODE>clean_up_inappropriate_cv</ENTER NODE>")

        # Placeholder for cleaning up steps required due to receiving
        # inappropriate cv

        logging.info("<EXIT NODE>clean_up_inappropriate_cv</EXIT NODE>")

        return {}

    def first_cv_step(self, state: AgentState) -> AgentState:

        return {}

    def second_cv_step(self, state: AgentState) -> AgentState:

        return {}
