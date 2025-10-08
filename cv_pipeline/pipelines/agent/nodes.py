import logging
from .state import AgentState
import logging
from ... import utils as ut
from ...services import services, tables
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict
import base64
import io
import os
from PIL import Image
from pdf2image import convert_from_path
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy import create_engine, select, Table, MetaData, Column, String
from sqlalchemy.dialects.postgresql import JSONB

log = logging.getLogger(__name__)


class CVModel(BaseModel):
    """Structured information about an applicant."""

    name: str = Field(description="The applicants's full name.")
    email: Optional[EmailStr] = Field(
        description="The applicants's email address, if available."
    )
    city: Optional[str] = Field(description="The applicants's city, if available.")
    education: Optional[str] = Field(
        description="""
        Summary of applicants education, summarising degree details such as
        title and institution.
        """
    )
    experience: Optional[str] = Field(
        description="Summary of applicants experience, summarising job titles, "
        "job description, employer, time spent in the role and location."
    )
    skills: Optional[str] = Field(
        description="Summary of applicants experience, summarising job titles, "
        "job description, employer, time spent in the role and location."
    )
    qualifications: Optional[str] = Field(
        description="Summary of applicants qualifications."
    )


class Recommendation(BaseModel):
    """
    Structured information about an applicant's suitability for a role,
    including a detailed breakdown of the assessment.
    """

    assessment: str = Field(
        description="Overall assessment of the candidate's suitability. Do not include names."
    )
    recommendation: bool = Field(
        description="A True/False indicator of the candidate's suitability."
    )
    # details: Dict[str, str] = Field(
    #     description=(
    #         "A dictionary providing a detailed breakdown of the assessment against key criteria, "
    #         "such as 'narrative', 'skills', 'education', and 'values'."
    #     )
    # )


# This is a messy workaround to access the vectorstore because I didn't put the position summaries
# in the relational db
metadata = MetaData()
langchain_pg_embedding_table = Table(
    "langchain_pg_embedding",
    metadata,
    # Only need to define the columns we intend to query.
    Column("cmetadata", JSONB),
    Column("document", String),
)


class Nodes:

    def __init__(self, config):
        self.config = config
        self.system_prompt_shared_part = """
        ### Persona ###
        You are an AI assistant who is an expert at evaluating cvs and resumes
        for job applicants to the Van Gogh Museum in Amsterdam.
        """

    def check_cv_for_validity(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>check_cv_for_validity</ENTER NODE>")

        # Placeholder for business logic that determines whether cv is valid to process with AI.

        # This protects the expensive AI parts of the system from dumps of invalid CVs.

        # Things to consider here:
        # - File format
        # - File size
        # - File corruption
        # - Basic "is this a cv?" check by looking for keywords
        # - Gibberish (e.g. Lorem Ipsum)
        # - Prompt injection based on key phrases

        valid = True
        if not valid:
            invalid_reason = "placeholder for invalid reason"
        else:
            invalid_reason = None

        log.info("<EXIT NODE>check_cv_for_validity</EXIT NODE>")

        return {"invalid_reason": invalid_reason}

    def clean_up_invalid_cv(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>clean_up_invalid_cv</ENTER NODE>")

        # Placeholder for cleaning up steps required due to receiving
        # unsuitable cv

        log.info("<EXIT NODE>clean_up_invalid_cv</EXIT NODE>")

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

    def extract_cv_information(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>extract_cv_information</ENTER NODE>")

        cv_pdf_file_path = (
            f'data/raw/cvs/{state["position_number"]}/{state["application_id"]}.pdf'
        )

        # # Convert PDF pages to a list of PIL Image objects
        images = convert_from_path(cv_pdf_file_path)

        # Prepare the content for the LangChain message
        # Start with text prompt
        text_part = [
            {
                "type": "text",
                "text": """
            You are an expert AI assistant specializing in roles within the arts and cultural
            heritage sector. Your task is to extract, synthesize, and structure key information
            from the provided museum position description.
            """,
            },
        ]

        cv_pdf_parts = []

        # Loop through each image, encode it, and add it to the content list
        for image in images:
            # In-memory buffer to save the image without writing to disk
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")  # Save image to buffer in JPEG format

            # Base64 encode the image
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Add the image part to the content list
            cv_pdf_parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                }
            )

        content_parts = text_part + cv_pdf_parts

        # Create the final HumanMessage
        message = HumanMessage(content=content_parts)

        # Need to use the base llm from services (does not yet have retry applied)
        structured_llm = services.base_llm.with_structured_output(CVModel)

        # Apply the retry logic to the *structured* LLM.
        # handles retries AND structured output.
        llm = structured_llm.with_retry(
            stop_after_attempt=5, wait_exponential_jitter=True
        )

        cv_info = llm.invoke([message]).model_dump()

        log.info("<EXIT NODE>extract_cv_information</EXIT NODE>")
        return {
            "cv_info": cv_info,
            "cv_pdf_parts": cv_pdf_parts,
            "calibration_needed": False,
        }

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

        statement = select(langchain_pg_embedding_table).where(
            langchain_pg_embedding_table.c.cmetadata["id"]
            .as_string()
            .contains(state["position_number"])
        )

        with services.engine_vectorstore.connect() as connection:
            results = connection.execute(statement).all()

        position_description = results[0].document

        filter_criteria = {
            "level": state["level"],
            "id": {
                "$ne": f'{state["position_number"]}_cv_{os.environ.get("EMBEDDINGS_PROVIDER")}_{os.environ.get("EMBEDDINGS_MODEL")}'  # noqa: E501
            },
        }

        # The plan is to put a threshold on this and ensure that only very similar positions are returned
        similar_pds = services.vector_store_cv.similarity_search_with_score(
            position_description,
            k=3,  # Retrieve top N chunks
            filter=filter_criteria,
        )

        similar_position_numbers = [
            s[0].id.replace(
                f'_cv_{os.environ.get("EMBEDDINGS_PROVIDER")}_{os.environ.get("EMBEDDINGS_MODEL")}',
                "",
            )
            for s in similar_pds
        ]

        stmt = select(tables["applicant_suitability_manual"].suitability_comment).where(
            tables["applicant_suitability_manual"].position_number.in_(
                similar_position_numbers
            ),
            tables["applicant_suitability_manual"].suitability_manual == "Y",
        )

        # Get comments about suitable applications
        with services.get_session() as session:
            suitability_comments_positive = session.scalars(stmt).all()

        stmt = select(tables["applicant_suitability_manual"].suitability_comment).where(
            tables["applicant_suitability_manual"].position_number.in_(
                similar_position_numbers
            ),
            tables["applicant_suitability_manual"].suitability_manual == "N",
        )

        # Get comments about unsuitable applications
        with services.get_session() as session:
            suitability_comments_negative = session.scalars(stmt).all()

        log.info("<EXIT NODE>retrieve_related_applications</EXIT NODE>")
        return {
            "similar_position_numbers": similar_position_numbers,
            "suitability_comments_positive": suitability_comments_positive,
            "suitability_comments_negative": suitability_comments_negative,
            "position_description": position_description,
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

    def preliminary_assessment(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>preliminary_assessment</ENTER NODE>")
        # Placeholder for now.
        pd_pdf_file_path = f'data/raw/pds/{state["position_number"]}.pdf'

        # Convert PDF pages to a list of PIL Image objects
        images = convert_from_path(pd_pdf_file_path)

        # Prepare the content for the LangChain message
        # Start with text prompt
        # NOTE: This version has been commented out because it was making gemini-2.5-flash hang.
        # For now we will use the much shorter prompt below.
        # text_part = [
        #     {
        #         "type": "text",
        #         "text": f"""
        #             ## ROLE ##
        #             You are an expert AI recruitment assistant for the arts and cultural heritage sector.

        #             ## CONTEXT ##
        #             - **Employer**: The Van Gogh Museum, Amsterdam.
        #             - **Core Values**: Authentic, In Connection, Original.

        #             ## TASK ##
        #             Analyze the candidate's CV against the Position Description (PD) provided in the image.
        #             Your analysis must be fast, objective, and strictly based on the provided documents.

        #             ## INPUTS ##
        #             - **CANDIDATE_CV**: {str(state["cv_info"])}
        #             - **POSITION_DESCRIPTION**: Provided as an image.

        #             ## Example output ##
        #             {{
        #             "overall_assessment": "A brief summary paragraph (2-3 sentences) assessing the candidate's
        #               suitability.",
        #             "recommendation": "YES",
        #             "detailed_analysis": {{
        #                 "narrative": "Assessment text.",
        #                 "skills": "Assessment text.",
        #                 "education_and_qualifications": "Assessment text.",
        #                 "values_alignment": "Assessment text."
        #             }}
        #             }}
        #     """,
        #     },
        # ]

        text_part = [
            {
                "type": "text",
                "text": f"""
            **Role:** AI Recruitment Specialist for the Arts & Cultural Heritage sector.
            **Goal:** Rapidly assess candidate suitability based on their CV and the Position Description image.

            **Candidate Information:**
            {str(state["cv_info"])}

            **Instructions:**
            1.  Identify the key requirements from the Position Description image.
            2.  Compare the candidate's information against these requirements.
            3.  Generate a 1-2 sentence assessment.
            4.  Provide a definitive YES/NO recommendation.
            5.  Adhere strictly to the format below.

            **Output Format:**
            **Assessment:** [Insert 1-2 sentence summary here, don't use names]
            **Recommendation:** [YES or NO]
            """,
            },
        ]

        pd_pdf_parts = []

        # Loop through each image, encode it, and add it to the content list
        for image in images:
            # In-memory buffer to save the image without writing to disk
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")  # Save image to buffer in JPEG format

            # Base64 encode the image
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Add the image part to the content list
            pd_pdf_parts.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                }
            )

        content_parts = text_part + pd_pdf_parts

        # Create the final HumanMessage
        message = HumanMessage(content=content_parts)

        # Need to use the base llm from services (does not yet have retry applied)
        structured_llm = services.base_llm.with_structured_output(Recommendation)

        # Apply the retry logic to the *structured* LLM.
        # handles retries AND structured output.
        llm = structured_llm.with_retry(
            stop_after_attempt=5, wait_exponential_jitter=True
        )

        preliminary_assessment_response = llm.invoke([message]).model_dump()

        log.info("<EXIT NODE>preliminary_assessment</EXIT NODE>")
        return {
            "preliminary_reasoning": preliminary_assessment_response["assessment"],
            "preliminary_assessment": preliminary_assessment_response["recommendation"],
            "pd_pdf_parts": pd_pdf_parts,
        }

    def check_for_prompt_injection_signs(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>check_for_prompt_injection_signs</ENTER NODE>")
        # Placeholder for now.

        log.info("<EXIT NODE>check_for_prompt_injection_signs</EXIT NODE>")

        return {"prompt_injection": False}

    def final_assessment(
        self,
        state: AgentState,
    ) -> AgentState:
        log.info("<ENTER NODE>final_assessment</ENTER NODE>")

        text_part = [
            {
                "type": "text",
                "text": f"""
            **Role:** AI Recruitment Specialist for the Arts & Cultural Heritage sector.
            **Goal:** Rapidly assess candidate suitability based on their CV and the Position Description image.
            **Background:** You already did an initial assessment, with details included below.
            **Special consideration:** Access has been provided to comments of historical CV evaluations of
            similar positions. These may indicate things you missed in your initial assessment. These may
            be blank if historical information could not be found, if so ignore this content, do not make
            anything up.

            **Candidate Information:**
            {str(state["cv_info"])}

            **Comments of Historical CVs that were __suitable__**
            {str(state["suitability_comments_positive"])}

            **Comments of Historical CVs that were __not suitable__**
            {str(state["suitability_comments_negative"])}
            
            **Instructions:**
            1.  Identify the key requirements from the Position Description image.
            2.  Compare the candidate's information against these requirements.
            3.  Consider your previous 1-2 sentence assessment.
            4.  Consider your previous YES/NO recommendation.
            5.  Compare your previous assessment and recommendation with the historical comments.
            6.  Provide an updated 1-2 sentence assessment.
            7.  Provide an updated YES/NO final recommendation.
            8.  Adhere strictly to the format below.

            **Output Format:**
            **Assessment:** [Insert 1-2 sentence summary here, don't use names]
            **Recommendation:** [YES or NO]
            """,
            },
        ]

        content_parts = text_part + state["pd_pdf_parts"]

        # Create the final HumanMessage
        message = HumanMessage(content=content_parts)

        # Need to use the base llm from services (does not yet have retry applied)
        structured_llm = services.base_llm.with_structured_output(Recommendation)

        # Apply the retry logic to the *structured* LLM.
        # handles retries AND structured output.
        llm = structured_llm.with_retry(
            stop_after_attempt=5, wait_exponential_jitter=True
        )

        final_assessment_response = llm.invoke([message]).model_dump()

        log.info("<EXIT NODE>final_assessment</EXIT NODE>")

        return {
            "suitability_reasoning": final_assessment_response["assessment"],
            "suitability_automatic": (
                "Y" if final_assessment_response["recommendation"] else "N"
            ),
        }
