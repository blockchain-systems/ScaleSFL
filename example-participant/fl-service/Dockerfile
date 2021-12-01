FROM python:3.9

RUN mkdir -p /app
WORKDIR /app

RUN apt-get update
RUN apt-get install -y git python-dev python3-dev

RUN pip install poetry 
COPY poetry.lock pyproject.toml app.py run.sh /app/
COPY /src /app/src/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN pip3 install -r requirements.txt

# ENTRYPOINT [ "python3", "-m", "src" ]
ENTRYPOINT [ "python3", "app.py" ]