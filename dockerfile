FROM python:3.9.1

WORKDIR /code

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --deploy --ignore-pipfile

RUN export $(cat .env)

COPY ./pitch_health /code/pitch_health

EXPOSE 8000
CMD ["uvicorn", "pitch_health.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]