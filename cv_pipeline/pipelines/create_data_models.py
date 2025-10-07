from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
    DateTime,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB


def create_data_models(Base, engine, experiment=None):

    schema_name = "cv_agent"

    if experiment:
        exe = "_experiment"
    else:
        exe = ""

    class Applicants(Base):
        # Provides details of applicants as per source data
        __tablename__ = "applicants"
        __table_args__ = {"schema": schema_name}

        id = Column(Integer, primary_key=True, autoincrement=True)

        # Application id
        application_id = Column(Text, primary_key=True)

        # Position number
        position_number = Column(Text, index=True)

        # ATSI identity, protected attribute used only for assessing model
        atsi_identity = Column(Text)

        # Disability status, protected attribute used only for assessing model
        disability_status = Column(Text)

        # Age range, protected attribute used only for assessing model
        age_range = Column(Text)

        # Gender identity, protected attribute used only for assessing model
        gender_identity = Column(Text)

        # LGBTQIA community, protected attribute used only for assessing model
        lgbtqia_community = Column(Text)

        # Carer responsibilities, protected attribute used only for assessing model
        carer_responsibilities = Column(Text)

        # LOTE status, protected attribute used only for assessing model
        speaks_language_other_than_english = Column(Text)

        # Application id
        application_id = Column(Text, primary_key=True)

    class Positions(Base):
        # Provides details of applicants as per source data
        __tablename__ = "positions"
        __table_args__ = {"schema": schema_name}

        id = Column(Integer, primary_key=True, autoincrement=True)

        # Position number
        position_number = Column(Text, primary_key=True, index=True)

        # Job title
        job_title = Column(Text)

        # Department
        job_title = Column(Text)

        # Level
        job_title = Column(Text)

    Base.metadata.create_all(engine)

    tables = {
        "applicants": Applicants,
        "positions": Positions,
    }

    return tables
