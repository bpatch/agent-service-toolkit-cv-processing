from .nodes import Nodes
from .edges import Edges
from .state import AgentState
from ... import utils as ut

from langgraph.graph import StateGraph, END
import os
from pathlib import Path
import logging


class CVAgent:

    def __init__(self, config):
        self.config = config
        self.agent = self.create_compiled_agent_graph()
        if os.environ.get("EXPERIMENT", None):
            self.draw_compiled_agent_graph()

    def create_compiled_agent_graph(self):
        """Define graph structure in this method."""

        # Initialise graph object from state object
        builder = StateGraph(AgentState)

        # Create custom nodes
        nodes = Nodes(
            self.config,
        )

        edges = Edges(
            self.config,
        )

        # Specify first node to run
        builder.set_entry_point("check_cv_content_for_safety")

        # Add nodes
        builder.add_node(
            "check_cv_content_for_safety", nodes.check_cv_content_for_safety
        )

        builder.add_node("clean_up_unsafe_cv", nodes.clean_up_unsafe_cv)

        builder.add_node(
            "check_if_calibration_scheduled", nodes.check_if_calibration_scheduled
        )

        builder.add_node(
            "retrieve_related_applications", nodes.retrieve_related_applications
        )

        builder.add_node("schedule_calibration", nodes.schedule_calibration)

        builder.add_node("assess_impression", nodes.assess_impression)

        builder.add_node("assess_narrative", nodes.assess_narrative)

        builder.add_node("assess_skills", nodes.assess_skills)

        builder.add_node("assess_education", nodes.assess_education)

        builder.add_node("assess_values", nodes.assess_values)

        builder.add_node("preliminary_assessment", nodes.preliminary_assessment)

        builder.add_node(
            "compare_with_previous_applications",
            nodes.compare_with_previous_applications,
        )

        builder.add_node("update_assessment", nodes.update_assessment)

        builder.add_node(
            "check_for_prompt_injection_signs", nodes.check_for_prompt_injection_signs
        )

        builder.add_node("final_summary", nodes.final_assessment)

        builder.add_node("final_assessment", nodes.final_assessment)

        # Add edges

        builder.add_conditional_edges("check_cv_content_for_safety", edges.route_safety)

        builder.add_conditional_edges(
            "check_if_calibration_scheduled", edges.route_calibration_scheduled
        )

        builder.add_edge("clean_up_unsafe_cv", END)

        builder.add_edge("schedule_calibration", END)

        builder.add_conditional_edges(
            "retrieve_related_applications", edges.route_calibration_needed
        )

        builder.add_edge("schedule_calibration", END)

        builder.add_edge("assess_impression", "assess_narrative")

        builder.add_edge("assess_narrative", "assess_skills")

        builder.add_edge("assess_skills", "assess_education")

        builder.add_edge("assess_education", "assess_values")

        builder.add_edge("assess_values", "preliminary_assessment")

        builder.add_edge("preliminary_assessment", "compare_with_previous_applications")

        builder.add_edge("compare_with_previous_applications", "update_assessment")

        builder.add_edge("update_assessment", "check_for_prompt_injection_signs")

        builder.add_conditional_edges(
            "check_for_prompt_injection_signs", edges.route_prompt_injection
        )

        builder.add_edge("final_summary", "final_assessment")

        builder.add_edge("final_assessment", END)

        # Create compiled graph
        self.compiled_agent = builder.compile()

        return self.compiled_agent

    def draw_compiled_agent_graph(self):
        directory_path_pathlib = Path("experiment_files")
        directory_path_pathlib.mkdir(parents=True, exist_ok=True)
        ut.graph_drawer(self.compiled_agent, self.config["experiment_id"])
