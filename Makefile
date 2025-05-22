.PHONY: all deactivate pipfile clean update run_module run deploy_prod rename_staging
SHELL := /bin/bash

# default show this file
all:
	@cat Makefile

pipfile:
	${SHELL} ./run_aws.sh pipfile

clean:
	${SHELL} ./run_aws.sh clean

update:
	${SHELL} ./run_aws.sh update

update_pakages_only:
	${SHELL} ./run_aws.sh update_pakages_only

test:
	${SHELL} ./run_aws.sh test

run:
	${SHELL} ./run_aws.sh

deploy:
	${SHELL} ./run_aws.sh deploy

deploy_prod:
	${SHELL} ./run_aws.sh deploy_prod

create_stack:
	${SHELL} ./run_aws.sh create_stack

delete_stack:
	${SHELL} ./run_aws.sh delete_stack

install:
	${SHELL} ./run_aws.sh install

requirements:
	${SHELL} ./run_aws.sh requirements
