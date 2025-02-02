FROM registry.redhat.io/ubi8/ubi:8.6

ARG PIP_INDEX_URL="https://pypi.org/simple"
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_INDEX_URL="${PIP_INDEX_URL}" \
    REQUESTS_CA_BUNDLE="/etc/pki/tls/certs/ca-bundle.crt"

LABEL maintainer="Red Hat Product Security Dev - Red Hat, Inc." \
      vendor="Red Hat Product Security Dev - Red Hat, Inc." \
      summary="Red Hat Component Registry (Corgi) application image" \
      distribution-scope="private"

ARG ROOT_CA_URL
RUN cd /etc/pki/ca-trust/source/anchors/ && \
    curl -O "${ROOT_CA_URL}" && \
    update-ca-trust

WORKDIR /opt/app-root/src/

RUN dnf --nodocs -y install --setopt install_weak_deps=false  \
        python39 \
        python39-setuptools \
        python39-devel \
        python39-pip \
        python39-wheel \
        # Kerberos-related utils such as kinit
        krb5-workstation \
        # To compile C bindings in certain Python dependencies
        gcc \
        # For gssapi compilation
        krb5-devel \
        # For psycopg2 compilation
        postgresql-devel \
        # Dependency for SSL support in the python-qpid-proton Python package
        openssl \
        openssl-devel \
        openldap-devel \
        https://github.com/anchore/syft/releases/download/v0.48.1/syft_0.48.1_linux_amd64.rpm \
        git \
    && dnf clean all

COPY ./requirements ./requirements

# Install Python package dependencies from requirements file passed in PIP_REQUIREMENT (local
# docker-compose may override this in the build step).
ARG PIP_REQUIREMENT="./requirements/base.txt"
RUN python3.9 -m pip install -r "${PIP_REQUIREMENT}"

# Limit copied files to only the ones required to run the app
COPY ./files/krb5.conf /etc
COPY ./*.sh ./*.py ./
COPY ./config ./config
COPY ./corgi ./corgi

RUN chgrp -R 0 /opt/app-root && \
    chmod -R g=u /opt/app-root
