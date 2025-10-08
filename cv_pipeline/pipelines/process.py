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

    applications_automatic = []
    for app_id in applications_to_process:
        print(f"Processing {app_id}")
        # Get position number from structured data
        with services.get_session() as session:
            stmt = select(Applicants.position_number).where(
                Applicants.application_id == app_id
            )

            # Execute the statement and get the first result
            pos_num = session.scalars(stmt).first()

            stmt = select(Positions.level).where(Positions.position_number == pos_num)

            # Execute the statement and get the first result
            level = session.scalars(stmt).first()

        cv_agent_response = cv_agent.agent.invoke(
            {"position_number": pos_num, "application_id": app_id, "level": level}
        )

        keys_to_keep_for_trace = [
            "invalid_reason",
            "suitability_reasoning",
            "calibration_scheduled",
            "calibration_needed",
        ]

        suitability_automatic_trace = {
            key: cv_agent_response[key]
            for key in keys_to_keep_for_trace
            if key in cv_agent_response
        }

        processed_application = {
            "application_id": app_id,
            "position_number": pos_num,
            "suitability_automatic": cv_agent_response["suitability_automatic"],
            "suitability_automatic_trace": suitability_automatic_trace,
        }

        if os.environ.get("EXPERIMENT", None):
            processed_application["experiment"] = config["experiment_id"]

        # Add to list of items to be db if not waiting for calibration
        # For now we never schedule calibration, so this is placeholder logic
        if (
            not cv_agent_response["calibration_needed"]
            and not cv_agent_response["calibration_scheduled"]
        ):
            applications_automatic.append(processed_application)

    log.info(
        f"Uploading {len(applications_automatic)} records to applicant_suitability_automatic"
    )
    with services.get_session() as session:
        # Create a list of data objects from the processed applications
        applicant_suitability_automatic = [
            ApplicantSuitabilityAutomatic(**data) for data in applications_automatic
        ]

        # session.add_all() efficiently adds all objects to the session
        session.add_all(applicant_suitability_automatic)
