# build stage
FROM python:3.11 as build

RUN apt update && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/code/myeshop

EXPOSE 80

COPY . .

# RUN rm -rf deploy

RUN pip install -e eshop/apps/user_identity && \
    pip install -e eshop/apps/user_identity_cqrs_contract && \
    pip install -e eshop/framework && \
    pip install -e .


# build for run pytest stage
FROM build as build_for_run_pytest

RUN pip install -r requirements/for_run_tests.txt

# build for prod
FROM build as build_for_prod

COPY deploy deploy