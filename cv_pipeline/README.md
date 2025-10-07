
# Museum job applicant evaluation assistant
This tool demos a basic setup of an AI assistant for processing CVs of job
applicants. 

> :warning: This project is in the early days of development and has not been thoroughly tested. Some
instructions may not work as expected.

## Features (and planned features)
At the moment the project consists of two main parts:
1. A backend data pipeline which incorporates an AI agent for processing CVs. It populates a database where an
indication of applicant suitability for positions is provided. As a precursor to this a vector database is
created to store descriptions of processed position descriptions.
2. The ability to generate fake data for testing and demo purposes (see the section below for details on how
to run it).

The project is also planned to have:
3. A frontend AI agent for users to calibrate the AI system and manually approve its decisions.
4. An experimental loop. Check out a new branch, when ready this loop will allow you to commit some changes
and run `docker-compose run --env EXPERIMENT=True --build cv_process` to see how your changes impact results
and metrics (in the respective tables). This will also produce a mermaid diagram in the data/experiment_files
directory.
5. A streamlit dashboard to view the results of experiments.

## Get the database running
Before doing anything else it's a good idea to get the db running and check you can access it in dbeaver or
similar. 

`docker-compose up postgres -d`

## To set up with fake data for demo purposes

1. Do `docker-compose up --build fake_data` to create data to be processed.
2. Do `docker-compose run --env SIMULATE_MANUAL_REVIEW=True fake_data` to create data to initialise without
having to do manual review. 

## Run the pipelines
1. To process data from source use `docker-compose run --build cv_preprocess`. This uploads the csv files
into the database, embeds descriptions of the positions descriptions and moves all the source data to the
raw folder. 

## Changes to the database tables
The tables are managed with Alembic. To change them:
1. Update `pipelines/get_data_models.py` with new definitions.
2. Locally run `uv run --env-file .env alembic revision --autogenerate -m "description of change"`
3. Do `docker-compose up --build db-migrator`.

## Notes
- The ollama image uses lots of memory. If you're using colima use `colima start --memory 24 --cpu 4`. 