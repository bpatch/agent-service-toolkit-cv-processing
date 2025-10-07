from ..services import services, tables
from .. import utils as ut
import os
import shutil
import glob
import logging
import base64
import io
from PIL import Image
from pdf2image import convert_from_path
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document as LangchainDocument


if __name__ == "__main__":

    log = logging.getLogger(__name__)

    # Get objects for relevant db tables
    Applicants = tables["applicants"]
    Positions = tables["positions"]
    ApplicantSuitabilityManual = tables["applicant_suitability_manual"]

    collection_name = f'cv_{os.environ.get("EMBEDDINGS_PROVIDER")}_{os.environ.get("EMBEDDINGS_MODEL")}'

    search_pattern = os.path.join("data/source/cvs", "*.csv")

    # Find all files matching the pattern
    new_source_cv_csv_files = glob.glob(search_pattern)

    for csv_file_name in new_source_cv_csv_files:

        try:
            # Get the data out as a list of dictionaries
            csv_data = ut.read_from_csv(csv_file_name)
            folders = []
            if "manual-review" in csv_file_name:
                with services.get_session() as session:
                    # Create a list of data objects from the input data
                    applicant_suitability_manual = [
                        ApplicantSuitabilityManual(**data) for data in csv_data
                    ]

                    # session.add_all() efficiently adds all objects to the session
                    session.add_all(applicant_suitability_manual)
            else:
                with services.get_session() as session:
                    # Create a list of data objects from the input data
                    applicants = [Applicants(**data) for data in csv_data]

                    # session.add_all() efficiently adds all objects to the session
                    session.add_all(applicants)
                for data in csv_data:
                    try:
                        os.makedirs(
                            f'data/raw/cvs/{data["position_number"]}', exist_ok=True
                        )
                        shutil.move(
                            f'data/source/cvs/{data["position_number"]}/{data["application_id"]}.pdf',
                            f'data/raw/cvs/{data["position_number"]}/{data["application_id"]}.pdf',
                        )
                        folders.append(data["position_number"])
                    except Exception as e:
                        log.error(
                            f'Error preprocessing {data["position_number"]}/{data["application_id"]}.pdf --- {e}'
                        )

            # Move the file from source to raw
            shutil.move(csv_file_name, csv_file_name.replace("source", "raw"))
            for f in set(folders):
                os.rmdir(f"data/source/cvs/{f}")

        except Exception as e:
            log.error(f"Error preprocessing {csv_file_name} --- {e}")

    search_pattern = os.path.join("data/source/pds", "*.csv")

    # Find all files matching the pattern
    new_source_pd_csv_files = glob.glob(search_pattern)

    for csv_file_name in new_source_pd_csv_files:

        try:
            # Get the data out as a list of dictionaries
            csv_data = ut.read_from_csv(csv_file_name)

            with services.get_session() as session:
                # Create a list of data objects from the input data
                positions = [Positions(**data) for data in csv_data]

                # session.add_all() efficiently adds all objects to the session
                session.add_all(positions)
            for data in csv_data:
                try:

                    pdf_file_path = f'data/source/pds/{data["position_number"]}.pdf'

                    # Convert PDF pages to a list of PIL Image objects
                    images = convert_from_path(pdf_file_path)

                    # Prepare the content for the LangChain message
                    # Start with text prompt
                    content_parts = [
                        {
                            "type": "text",
                            "text": """
                        You are an expert AI assistant specializing in roles within the arts and cultural
                        heritage sector. Your task is to extract, synthesize, and structure key information
                        from the provided museum position description.

                        The output must be a concise, keyword-rich summary formatted in markdown. This output
                        will be converted into a vector embedding to find similar roles across cultural
                        institutions. Therefore, focus on capturing the essence of the role, its departmental
                        function, required specializations, and interaction with collections or the public.

                        **Instructions:**

                        1.  **Analyze the Text:** Carefully read the entire position description provided
                        below.
                        2.  **Extract and Synthesize:** Do not just copy-paste. Synthesize the information
                        into the specified categories. For example, consolidate skills mentioned in different
                        sections into a single list.
                        3.  **Use Keywords:** Be direct and use keywords that define the role (e.g.,
                        "API development," "Agile methodology," "stakeholder management").
                        4.  **Omit Fluff:** Exclude generic corporate boilerplate, benefits information, and
                        equal opportunity statements.
                        5.  **Format:** Use the exact markdown structure below. If a section is not
                        applicable, write
                        "N/A".

                        **Structured Output:**

                        **## Job Core**
                        * **Job Title:** [Extracted Job Title, e.g., Registrar, Curator of Modern Art,
                        Exhibition Designer]
                        * **Seniority:** [e.g., Assistant, Associate, Senior, Head of, Intern]
                        * **Team / Department:** [e.g., Curatorial, Collections Management, Conservation,
                        Education, Exhibitions, Visitor Services, Development]
                        * **Role Summary:** [A 1-2 sentence summary describing the core purpose of this
                        role within the museum.]

                        **## Key Responsibilities**
                        [A concise, bulleted list of the primary duties. Start each bullet with an action
                        verb relevant to museum work. Synthesize similar points.]
                        *
                        *
                        *

                        **## Core Competencies & Skills**
                        * **Specialized Skills & Systems:** [Comma-separated list of essential technical
                        systems, software, and practical skills. e.g., TMS, Vernon CMS, PastPerfect, Adobe
                        Creative Suite, object handling, condition reporting, archival processing, grant
                        writing, digital photography]
                        * **Subject Matter Expertise:** [Comma-separated list of required knowledge areas.
                        e.g., Art History, 19th-Century Photography, Material Culture, Conservation Science,
                        Museum Education Theory]
                        * **Soft Skills:** [Comma-separated list of key professional skills. e.g., Public
                        Speaking, Research and Writing, Attention to Detail, Stakeholder Engagement,
                        Cross-departmental Collaboration, Project Management]

                        **## Qualifications & Experience**
                        * **Education:** [Minimum or preferred educational background, e.g., MA in Museum
                        Studies, PhD in Art History, Certificate in Conservation]
                        * **Experience:** [Required years and type of experience, e.g., 3+ years in a museum
                        registration role, demonstrated experience curating exhibitions]
                        * **Collection Focus:** [The specific type of collection this role works with,
                        if mentioned. e.g., Textiles, Works on Paper, Digital Media, Natural History
                        Specimens, Archives]
                        """,
                        },
                    ]

                    # Loop through each image, encode it, and add it to the content list
                    for i, image in enumerate(images):
                        # In-memory buffer to save the image without writing to disk
                        buffered = io.BytesIO()
                        image.save(
                            buffered, format="JPEG"
                        )  # Save image to buffer in JPEG format

                        # Base64 encode the image
                        img_base64 = base64.b64encode(buffered.getvalue()).decode(
                            "utf-8"
                        )

                        # Add the image part to the content list
                        content_parts.append(
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                },
                            }
                        )

                    # Create the final HumanMessage
                    message = HumanMessage(content=content_parts)

                    # Invoke the model
                    response_pd = services.llm.invoke([message])
                    ut.upload_chunk_set(
                        0,
                        [
                            LangchainDocument(
                                page_content=response_pd.content,
                                metadata={
                                    "id": f'{data["position_number"]}_{collection_name}',
                                    "file": f'data/raw/pds/{data["position_number"]}.pdf',
                                    "type": "pd",
                                    "department": data["department"],
                                    "level": data["level"],
                                },
                            )
                        ],
                        services.vector_store_cv,
                        collection_name,
                    )

                    shutil.move(
                        f'data/source/pds/{data["position_number"]}.pdf',
                        f'data/raw/pds/{data["position_number"]}.pdf',
                    )
                except Exception as e:
                    log.error(
                        f'Error preprocessing {data["position_number"]}.pdf --- {e}'
                    )

            # Move the file from source to raw
            shutil.move(csv_file_name, csv_file_name.replace("source", "raw"))

        except Exception as e:
            log.error(f"Error preprocessing {csv_file_name} --- {e}")
