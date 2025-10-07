
# Museum job applicant evaluation assistant
This tool demos a basic setup of an AI assistant for processing CVs of job
applicants using. 

It consists of two main parts:
1. A frontend AI agent for users to calibrate the AI system and manually approve its decisions.
2. A backend data pipeline which incorporates an AI agent for processing CVs. It populates a database where an
indication of applicant suitability for positions is provided.

## Get the database running
Before doing anything else it's a good idea to get the db running and check you can access it in dbeaver or
similar. 

`docker-compose up postgres -d`

## To set up with fake data for demo purposes

1. Do `docker-compose up --build fake_data` to create data to be processed.
2. Do `docker-compose run --env SIMULATE_MANUAL_REVIEW=True fake_data` to create data to initialise without
having to do manual review. 



## Changes to the database tables
The tables are managed with Alembic. To change them:
1. Update pipelines/get_data_models.py with new definitions.
2. 


## Notes
- The ollama image uses lots of memory. If you're using colima use `colima start --memory 24 --cpu 4`. 