FROM python:3.9.1

WORKDIR /

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc
COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --deploy --ignore-pipfile

RUN export $(cat .env)

COPY . .

EXPOSE 8000
