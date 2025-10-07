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
        builder.set_entry_point("classify_cv")

        # Add nodes
        builder.add_node("classify_cv", nodes.classify_cv)

        builder.add_node("clean_up_inappropriate_cv", nodes.clean_up_inappropriate_cv)

        builder.add_node("first_cv_step", nodes.first_cv_step)

        builder.add_node("second_cv_step", nodes.first_cv_step)

        # Add edges

        builder.add_conditional_edges("classify_cv", edges.route_inappropriate)

        builder.add_edge("clean_up_inappropriate_cv", END)

        builder.add_edge("first_cv_step", "second_cv_step")

        builder.add_edge("second_cv_step", END)

        # Create compiled graph
        self.compiled_agent = builder.compile()

        return self.compiled_agent

    def draw_compiled_agent_graph(self):
        directory_path_pathlib = Path("experiment_files")
        directory_path_pathlib.mkdir(parents=True, exist_ok=True)
        ut.graph_drawer(
            self.compiled_agent,
            f'cv_pipeline/experiment_files/cv_agent_graph_{os.environ.get("EXPERIMENT")}.png',
        )
