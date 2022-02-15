FROM ubuntu:20.04 AS config

RUN apt-get update \
 && apt-get install \
      -y \
      --no-install-recommends \
      apt-transport-https \
      ca-certificates \
      curl \
      gnupg \
      lsb-release \
      software-properties-common \
 # Acquire Azure CLI package configuration
 && curl -sL https://packages.microsoft.com/keys/microsoft.asc | \
      gpg --dearmor | \
      tee /microsoft.gpg > /dev/null


FROM ubuntu:20.04

# install the necessary dependencies for the pipeline to be able to run

COPY --from=config /microsoft.gpg /etc/apt/trusted.gpg.d/

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Toronto

RUN apt-get update \
 && apt-get install \
      -y \
      --no-install-recommends \
      ca-certificates \
      git \
      lsb-release \
      make \
      python3 \
      python3-pip \
      python3-venv \
 && AZ_REPO=$(lsb_release -cs) \
 && echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | \
      tee /etc/apt/sources.list.d/azure-cli.list \
 && apt-get update \
 && apt-get install \
      -y \
      --no-install-recommends \
      azure-cli \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /

# keep requirements.txt up-to-date with the project with `pip freeze > docker/pipeline/requirements.txt` on a *clean*
# venv where the project is installed
RUN python3 -m venv /venv \
 && /venv/bin/pip install -r /requirements.txt
