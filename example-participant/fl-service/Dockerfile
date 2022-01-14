FROM python:3.9

RUN mkdir -p /app
WORKDIR /app

# Update and install python
RUN apt-get update
RUN apt-get install -y git python-dev python3-dev

# Install poetry and move src
RUN pip install poetry 
COPY poetry.lock pyproject.toml app.py /app/
COPY /src /app/src/

# Install dependencies
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes
RUN pip3 install -r requirements.txt
RUN pip3 install torch torchvision torchaudio opacus

# ENTRYPOINT [ "python3", "-m", "src" ]
ENTRYPOINT [ "python3", "app.py" ]