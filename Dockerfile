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

RUN pip install -e eshop/apps/user_identity && \
    pip install -e eshop/apps/user_identity_cqrs_contract && \
    pip install -e eshop/apps/basket && \
    pip install -e eshop/apps/basket_cqrs_contract && \
    pip install -e eshop/apps/test_app && \
    pip install -e eshop/apps/catalog && \
    pip install -e eshop/apps/catalog_cqrs_contract && \
    pip install -e eshop/apps/api_mediator && \
    pip install -e eshop/framework && \
    pip install -e .

COPY alembic.ini alembic.ini

# build for running import-linter
FROM build as build_for_running_import_linter

COPY setup.cfg setup.cfg
COPY deploy/ci/linter/import_linter.txt deploy/ci/linter/import_linter.txt

RUN pip install -r deploy/ci/linter/import_linter.txt


# build for run pytest stage
FROM build as build_for_run_pytest

COPY pytest.ini pytest.ini

ENV POSTGRES__NAME=blabla
ENV POSTGRES__HOST=blabla
ENV POSTGRES__PORT=12345
ENV POSTGRES__LOGIN=blabla
ENV POSTGRES__PASSWORD=blabla
ENV USER_IDENTITY_SERVICE__SECRET=blabla
ENV USER_IDENTITY_SERVICE__INITIAL_ADMIN_USER_CREDENTIALS__NAME=blabla
ENV USER_IDENTITY_SERVICE__INITIAL_ADMIN_USER_CREDENTIALS__PASSWORD=blabla

RUN pip install -r requirements/for_run_tests.txt

# build for prod
FROM build as build_for_prod

COPY deploy/uvicorn deploy/uvicorn