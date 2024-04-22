FROM python:3.9

RUN pip install --no-cache-dir docker

COPY entrypoint.py /entrypoint.py

ENV CONFIGURATION_FILE=/config.json

ENTRYPOINT ["python", "/entrypoint.py"]