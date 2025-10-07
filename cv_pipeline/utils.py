from langchain_core import language_models
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from google.api_core.exceptions import ResourceExhausted
from langchain_openai import OpenAI, OpenAIEmbeddings
from openai import RateLimitError
from tenacity import (
    retry,
    wait_exponential,
    stop_after_attempt,
)
import logging
import csv
from typing import List

log = logging.getLogger(__name__)


def log_retry_attempt(retry_state):
    log_message = f"""
    Retrying upload set {retry_state.args[0] + 1} in {retry_state.next_action.sleep}s
    """
    if retry_state.outcome:
        error = retry_state.outcome.exception()
        log_message += f"(Attempt {retry_state.attempt_number + 1}, Error: {error})"
    else:
        log_message += f"(Attempt {retry_state.attempt_number + 1})"
    log.info(log_message)


@retry(
    wait=wait_exponential(multiplier=1, min=60, max=180),
    stop=stop_after_attempt(5),
    reraise=True,
    before_sleep=log_retry_attempt,
)
def upload_chunk_set(doc_objects, vector_store, collection_name):
    """Uploads a set of document chunks to the vector store with retry."""
    vector_store.add_documents(
        doc_objects,
        ids=[f'{o.metadata["id"]}_{collection_name}' for o in doc_objects],
    )


class ChatFactory:
    """
    Standardised way to create llm objects with retry built in when needed.

    Args
    ----

    provider : str
        Developer of model. Should be one of `ollama`, `google` or `openai`.
        Support for other providers has not been added.

    model_name : str
        Model to use, which depends on provider. E.g. for provider `ollama` use
        `gemma3:4b`, for provider `google` use `gemini-2.5-flash`, or for
        provider `openai` use `gpt-4o`.

    temperature : float (optional)
        Controls the randomness of the output. A value of 0 makes the output
        nearly deterministic, maximizing reproducibility.


    SETUP
    -----

    To run models locally, install Ollama by following the steps below:

    For macOS, run:

    ```shell
    brew install ollama
    ```

    For other operating systems, refer to the
    [Ollama installation guide](https://ollama.com).

    Make sure Ollama is running by calling:

    ```shell
    ollama serve
    ```
    Note: This occupies a shell window that must be kept open and cannot be used for
    other prompts

    Get an LLM:
    Note: Must be done in a new shell window

    ```shell
    ollama pull gemma
    ```

    """

    @staticmethod
    def create(
        provider: str, model_name: str, temperature: float = 0, **params
    ) -> language_models.BaseChatModel:
        common_retry_config = {
            "stop_after_attempt": 5,
            "wait_exponential_jitter": True,
        }
        if provider == "ollama":
            return ChatOllama(model=model_name, temperature=temperature, **params)
        elif provider == "google":
            return ChatGoogleGenerativeAI(
                model=model_name, temperature=temperature, **params
            ).with_retry(**common_retry_config)
        elif provider == "openai":
            return OpenAI(
                model=model_name, temperature=temperature, **params
            ).with_retry(**common_retry_config)
        else:
            raise ValueError(f"Unknown chat type: {provider}")


class EmbeddingsFactory:
    """
    Standard way to create embeddings objects.

    provider : str
        Developer of embedding model. Should be one of `ollama`, `google` or `openai`.
        Support for other providers has not been added.

    model_name : str
        Model to use, which depends on provider. E.g. for provider `ollama` use
        `embeddinggemma:300m`, for provider `google` use `gemini-embedding-001`, or for
        provider `openai` use `text-embedding-3-large`.
    """

    @staticmethod
    def create(provider: str, model_name: str):
        if provider == "ollama":
            return OllamaEmbeddings(model=model_name)
        elif provider == "google":
            return GoogleGenerativeAIEmbeddings(model=model_name)
        elif provider == "openai":
            return OpenAIEmbeddings(model=model_name)
        else:
            raise ValueError(f"Unknown provider type: {provider}")


def write_to_csv(filename: str, header: List[str], data: List[List[str]]) -> None:
    """
    Writes a header and data to a specified CSV file.

    Args:
        filename (str): The path to the output CSV file.
        header (list): A list of strings representing the column headers.
        data (list of lists): A list where each inner list is a row of data.
    """
    try:
        # 'w' opens the file in write mode.
        # newline='' prevents extra blank rows from being inserted.
        with open(filename, "w", newline="") as csvfile:
            # Create a csv writer object.
            csv_writer = csv.writer(csvfile)

            # Write the header row first.
            csv_writer.writerow(header)

            # Write all the data rows.
            csv_writer.writerows(data)

        print(f"Successfully created '{filename}' with {len(data)} data rows.")

    except IOError:
        log.error(f" Could not write to the file '{filename}'.")
