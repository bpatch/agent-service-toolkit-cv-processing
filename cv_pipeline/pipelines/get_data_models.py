from sqlalchemy import (
    Column,
    Integer,
    Text,
    Boolean,
    DateTime,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB


def get_data_models(Base, experiment=None):

    schema_name = "cv"

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

    class ApplicantSuitabilityManual(Base):
        # Provides details of applicants as per source data
        __tablename__ = "applicant_suitability_manual"
        __table_args__ = {"schema": schema_name}

        id = Column(Integer, primary_key=True, autoincrement=True)

        # Application id
        application_id = Column(Text, primary_key=True)

        # Position number
        position_number = Column(Text, index=True)

        # Y/N indicator of suitability
        suitability_manual = Column(Text)

        # Brief comment on reasons for or against suitability
        suitability_comment = Column(Text)

    class ApplicantSuitabilityAutomatic(Base):
        # Provides details of applicants as per source data
        __tablename__ = "applicant_suitability_automatic"
        __table_args__ = {"schema": schema_name}

        id = Column(Integer, primary_key=True, autoincrement=True)

        # Application id
        application_id = Column(Text, primary_key=True)

        # Position number
        position_number = Column(Text, index=True)

        # Y/N indicator of suitability
        suitability_automatic = Column(Text)

        # Place to capture information on AI reasoning. Is JSONB for flexibility.
        suitability_automatic_trace = Column(JSONB)

    class ApplicantSuitabilityAutomatiExperiment(Base):
        # Provides details of applicants as per source data
        __tablename__ = "applicant_suitability_automatic_experiment"
        __table_args__ = {"schema": schema_name}

        id = Column(Integer, primary_key=True, autoincrement=True)

        # Application id
        application_id = Column(Text, primary_key=True)

        # Position number
        position_number = Column(Text, index=True)

        # Y/N indicator of suitability
        suitability_automatic = Column(Text)

        # Place to capture information on AI reasoning. Is JSONB for flexibility.
        suitability_automatic_trace = Column(JSONB)

        # Experiment label
        experiment = Column(Text)

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

    tables = {
        "applicants": Applicants,
        "positions": Positions,
        "applicant_suitability_manual": ApplicantSuitabilityManual,
        "applicant_suitability_automatic": ApplicantSuitabilityAutomatic,
        "applicant_suitability_automatic_experiment": ApplicantSuitabilityAutomatiExperiment,
    }

    return tables
