# services.py
import os
import logging
from functools import cached_property
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, DeclarativeBase, sessionmaker
from langchain_postgres.vectorstores import PGVector
from contextlib import contextmanager

# Import custom utility functions
from cv_pipeline.pipelines import create_data_models
import cv_pipeline.utils as ut

# --- 1. Setup Logger ---
# Get a logger instance for this specific module
log = logging.getLogger(__name__)


# --- 2. Centralized Configuration ---
DB_USER = os.environ["POSTGRES_USER"]
DB_PASSWORD = os.environ["POSTGRES_PASSWORD"]
DB_HOST = os.environ.get("POSTGRES_HOST")
DB_PORT = os.environ.get("POSTGRES_PORT")
DB_NAME = os.environ["POSTGRES_DB"]

EMBEDDINGS_PROVIDER = os.environ["EMBEDDINGS_PROVIDER"]
EMBEDDINGS_MODEL = os.environ["EMBEDDINGS_MODEL"]
LLM_PROVIDER = os.environ["LLM_PROVIDER"]
LLM_MODEL = os.environ["LLM_MODEL"]


# --- 3. Service Provider Class ---
class ServiceProvider:
    """
    Manages and provides access to application services.
    Services are initialized lazily using @cached_property.
    """

    def __init__(self):
        self.db_url = URL.create(
            "postgresql+psycopg",
            username=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            query={"sslmode": "prefer"},
        )
        self.cv_schema = "cv"
        self.vectorstore_schema = "vectorstore"

    # --- Database Services ---
    @cached_property
    def engine(self):
        """SQLAlchemy engine for the main application schema."""
        log.info("Initializing main database engine...")
        return create_engine(
            self.db_url,
            connect_args={"options": f"-c search_path={self.cv_schema}"},
        )

    @cached_property
    def SessionLocal(self):
        """SQLAlchemy session factory, bound to the main engine."""
        log.info("Creating session factory...")
        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    @contextmanager
    def get_session(self):
        """Provide a transactional scope around a series of operations."""
        session = self.SessionLocal()
        log.debug("Database session created.")
        try:
            yield session
            session.commit()
            log.debug("Session committed.")
        except Exception:
            log.error("Session rolled back due to an exception.")
            session.rollback()
            raise
        finally:
            session.close()
            log.debug("Session closed.")

    @cached_property
    def engine_vectorstore(self):
        """SQLAlchemy engine for the vector store schema."""
        log.info("Initializing vector store engine...")
        return create_engine(
            self.db_url,
            connect_args={"options": f"-c search_path={self.vectorstore_schema}"},
        )

    @cached_property
    def Base(self) -> DeclarativeBase:
        """SQLAlchemy declarative base."""
        return declarative_base()

    @cached_property
    def tables(self):
        """Creates and returns the application's data models/tables."""
        log.info("Creating data models...")
        return create_data_models(self.Base, self.engine)

    # --- AI & Vector Store Services ---
    @cached_property
    def embeddings(self):
        """Embeddings model client provider"""
        log.info("Initializing embeddings model...")
        return ut.EmbeddingsFactory.create(EMBEDDINGS_PROVIDER, EMBEDDINGS_MODEL)

    @cached_property
    def vector_store_cv(self) -> PGVector:
        """Vector store for CV data."""
        log.info("Initializing CV vector store...")
        collection_name = f"cv_{EMBEDDINGS_PROVIDER}_{EMBEDDINGS_MODEL}"
        return PGVector(
            embeddings=self.embeddings,
            collection_name=collection_name,
            connection=self.engine_vectorstore,
            use_jsonb=True,
            create_extension=False,
        )

    @cached_property
    def llm(self):
        """Main LLM to invoke (has retry logic for Google and OpenAI)."""
        log.info(f"Initializing LLM provider {LLM_PROVIDER} model {LLM_MODEL} ...")
        return ut.ChatFactory.create(
            LLM_PROVIDER,
            LLM_MODEL,
            temperature=0,
        )

    @cached_property
    def llm_hot(self):
        """Main LLM to invoke (has retry logic for Google and OpenAI)."""
        temp = 0.9
        log.info(
            f"Initializing LLM provider {LLM_PROVIDER} model {LLM_MODEL} with temp {temp}..."
        )
        return ut.ChatFactory.create(
            LLM_PROVIDER,
            LLM_MODEL,
            temperature=temp,
        )


services = ServiceProvider()
