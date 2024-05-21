# build stage
FROM python:3.11 as build

RUN apt update && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/code/myeshop
RUN mkdir -p /usr/uvicorn_socket_folder

WORKDIR /usr/code/myeshop

COPY eshop eshop
COPY requirements requirements
COPY setup.py setup.py
COPY alembic.ini alembic.ini

RUN pip install -e eshop/apps/user_identity && \
    pip install -e eshop/apps/user_identity_cqrs_contract && \
    pip install -e eshop/apps/test_app && \
    pip install -e eshop/framework && \
    pip install -e .

# build for run pytest stage
FROM build as build_for_run_pytest

COPY pytest.ini pytest.ini

RUN pip install -r requirements/for_run_tests.txt

# build for prod
FROM build as build_for_prod

COPY deploy/uvicorn deploy/uvicorn