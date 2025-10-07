from .agent.graph import CVAgent
import os
from .. import utils as ut
from ..services import services, tables
import uuid
import logging

log = logging.getLogger(__name__)


if __name__ == "__main__":
    config = {}  # Placeholder for config to pass to graph, nodes, and edges

    if os.environ.get("EXPERIMENT", None):
        config["experiment_id"] = str(uuid.uuid4())
        log.info(f"Running experiment {config["experiment_id"]}")

    cv_agent = CVAgent(config)

    cv_agent_response = cv_agent.agent.invoke(
        {
            "doc_id": "123abc",
        }
    )

    print(f"{cv_agent_response=}")
