import logging
from .state import AgentState
import logging
from ... import utils as ut
from ...services import services, tables

log = logging.getLogger(__name__)


class Nodes:

    def __init__(self, config):
        self.config = config
        self.system_prompt_shared_part = """
        ### Persona ###
        You are an AI assistant who is an expert at evaluating cvs and resumes
        for job applicants to the Van Gogh Museum in Amsterdam.
        """

    def check_cv_content_for_safety(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>check_cv_content_for_safety</ENTER NODE>")

        # Placeholder for business logic that determines whether cv is safe to process
        safe = True

        log.info("<EXIT NODE>check_cv_content_for_safety</EXIT NODE>")

        return {"safe": safe}

    def clean_up_unsafe_cv(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>clean_up_unsafe_cv</ENTER NODE>")

        # Placeholder for cleaning up steps required due to receiving
        # unsafe cv

        log.info("<EXIT NODE>clean_up_unsafe_cv</EXIT NODE>")

        return {}

    def check_if_calibration_scheduled(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>check_if_calibration_scheduled</ENTER NODE>")
        # Placeholder for now. Checks whether the position has been scheduled for calibration.
        # Calibration means a human needs to assess some of the cvs for suitability.
        # Calibration occurs when a similar enough position cannot be found in historical data.

        log.info("<EXIT NODE>check_if_calibration_scheduled</EXIT NODE>")

        return {"calibration_scheduled": False}

    def retrieve_related_applications(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>retrieve_related_applications</ENTER NODE>")
        # Placeholder for now. Identifies similar position descriptions
        # at the same level (could also be adapted for same department).
        # Retrieves human reviewer comments for applications to the most
        # similar identified position. Could be adapted to retrieve more
        # information (such as the application files themselves).
        related_applications = "related applications placeholder"

        log.info("<EXIT NODE>retrieve_related_applications</EXIT NODE>")

        return {
            "related_applications": related_applications,
            "calibration_needed": False,
        }

    def schedule_calibration(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>schedule_calibration</ENTER NODE>")
        # Placeholder for now. Adds an entry to the database marking
        # the position associated with this application for calibration.

        log.info("<EXIT NODE>schedule_calibration</EXIT NODE>")

        return {}

    def assess_impression(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>assess_impression</ENTER NODE>")
        # Placeholder for now.

        log.info("<EXIT NODE>assess_impression</EXIT NODE>")

        return {}

    def assess_narrative(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>assess_narrative</ENTER NODE>")
        # Placeholder for now.

        log.info("<EXIT NODE>assess_narrative</EXIT NODE>")

        return {}

    def assess_skills(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>assess_skills</ENTER NODE>")
        # Placeholder for now.

        log.info("<EXIT NODE>assess_skills</EXIT NODE>")

        return {}

    def assess_education(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>assess_education</ENTER NODE>")
        # Placeholder for now.

        log.info("<EXIT NODE>assess_education</EXIT NODE>")

        return {}

    def assess_values(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>assess_values</ENTER NODE>")
        # Placeholder for now.

        log.info("<EXIT NODE>assess_values</EXIT NODE>")

        return {}

    def preliminary_assessment(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>preliminary_assessment</ENTER NODE>")
        # Placeholder for now.

        log.info("<EXIT NODE>preliminary_assessment</EXIT NODE>")

        return {}

    def compare_with_previous_applications(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>compare_with_previous_applications</ENTER NODE>")
        # Placeholder for now.

        log.info("<EXIT NODE>compare_with_previous_applications</EXIT NODE>")

        return {}

    def update_assessment(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>update_assessment</ENTER NODE>")
        # Placeholder for now.

        log.info("<EXIT NODE>update_assessment</EXIT NODE>")

        return {}

    def check_for_prompt_injection_signs(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>check_for_prompt_injection_signs</ENTER NODE>")
        # Placeholder for now.

        log.info("<EXIT NODE>check_for_prompt_injection_signs</EXIT NODE>")

        return {"prompt_injection": False}

    def final_summary(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>final_summary</ENTER NODE>")
        # Placeholder for now.

        log.info("<EXIT NODE>final_summary</EXIT NODE>")

        return {}

    def final_assessment(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>final_assessment</ENTER NODE>")
        # Placeholder for now.

        log.info("<EXIT NODE>final_assessment</EXIT NODE>")

        return {}
