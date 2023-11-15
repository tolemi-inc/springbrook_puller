#CONTAINER TEMPLATE
FROM python:3.9-slim-bookworm

RUN echo $PATH

WORKDIR /opt/springbrook_puller

#install requirements
COPY requirements.txt /opt/springbrook_puller/
RUN pip install -r requirements.txt

# copy the script
COPY springbrook_puller /opt/springbrook_puller/

# add the script callers to path
ENV PATH="/opt/springbrook_puller/bin:$PATH"