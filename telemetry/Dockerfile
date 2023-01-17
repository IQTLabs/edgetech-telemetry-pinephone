FROM iqtlabs/edgetech-core:latest
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
ADD ./telemetry_pub_sub.py .
ENTRYPOINT [ "python3", "-u", "telemetry_pub_sub.py" ]