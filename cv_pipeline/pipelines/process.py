from .agent.graph import CVAgent
import os
from .. import utils as ut
from ..services import services, tables
import uuid
import logging
from sqlalchemy import select

log = logging.getLogger(__name__)


if __name__ == "__main__":
    config = {}  # Placeholder for config to pass to graph, nodes, and edges

    Applicants = tables["applicants"]
    Positions = tables["positions"]
    ApplicantSuitabilityManual = tables["applicant_suitability_manual"]

    if os.environ.get("EXPERIMENT", None):
        config["experiment_id"] = str(uuid.uuid4())
        log.info(f"Running experiment {config["experiment_id"]}")
        # Will put results in the experiment variant of the table during experiment mode
        ApplicantSuitabilityAutomatic = tables[
            "applicant_suitability_automatic_experiment"
        ]
        # In experiment mode we want applications which have already been manually reviewed.
        # In future this should be limited to a specific set according to a sampling strategy.
        with services.get_session() as session:
            all_applicant_ids = select(Applicants.application_id)
            manual_ids = select(ApplicantSuitabilityManual.application_id)
            # .intersect() returns unique values
            common_ids_stmt = all_applicant_ids.intersect(manual_ids)
            # .scalars().all() executes the query and returns the results as a simple list.
            result = session.execute(common_ids_stmt)

            applications_to_process = result.scalars().all()
            print(applications_to_process)

    else:
        ApplicantSuitabilityAutomatic = tables["applicant_suitability_automatic"]
        # In operational mode we want to process all unprocessed applications
        with services.get_session() as session:
            # all application IDs from the source table.
            all_applicant_ids = select(Applicants.application_id)

            # all application IDs from the table to subtract.
            processed_ids = select(ApplicantSuitabilityAutomatic.application_id)

            # Use .except_() to find the difference between the two queries.
            stmt = all_applicant_ids.except_(processed_ids)

            result = session.execute(stmt)

            applications_to_process = result.scalars().all()

    cv_agent = CVAgent(config)

    for app_id in applications_to_process:

        cv_agent_response = cv_agent.agent.invoke(
            {
                "application_id": app_id,
            }
        )

        print(f"{cv_agent_response=}")
