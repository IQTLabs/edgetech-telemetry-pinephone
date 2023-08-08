FROM iqtlabs/edgetech-core:latest
RUN pip3 install poetry==1.5.1

COPY pyproject.toml .
COPY poetry.lock .
RUN poetry config virtualenvs.create false
RUN poetry install --without dev

COPY ./telemetry_pub_sub.py .
ENTRYPOINT [ "python3", "telemetry_pub_sub.py" ]
