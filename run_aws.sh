#!/bin/sh
# run_aws.sh
# 2023-02-02 | CR
#
APP_DIR='chalicelib'
PYTHON3_EXEC='/usr/local/bin/python3.9'
AWS_STACK_NAME='mediabros-apis-stack'
ENV_FILESPEC=""
if [ -f "./.env" ]; then
    ENV_FILESPEC="./.env"
fi
if [ -f "../.env" ]; then
    ENV_FILESPEC="../.env"
fi
if [ "$ENV_FILESPEC" != "" ]; then
    set -o allexport; source ${ENV_FILESPEC}; set +o allexport ;
fi
if [ "$PORT" = "" ]; then
    PORT="5001"
fi

if [ "$1" = "pipfile" ]; then
    deactivate ;
    
    # https://realpython.com/intro-to-pyenv/
    pipenv --python 3.9

    pipenv install requests
    pipenv install openai
    pipenv install "python-jose[cryptography]"
    pipenv install "passlib[bcrypt]"
    pipenv install wheel
    pipenv install python-multipart
    pipenv install python-dotenv
    
    # FasAPI
    pipenv install fastapi
    # pipenv install a2wsgi
    
    # Mongo
    pipenv install pymongo
    pipenv install werkzeug

    # AWS
    pipenv install boto3
    pipenv install chalice

    pipenv lock
    pipenv requirements > requirements.txt
fi

if [ "$1" = "clean" ]; then
    echo "Cleaning..."
    cd ${APP_DIR} ;
    deactivate ;
    rm -rf __pycache__ ;
    rm -rf ../__pycache__ ;
    rm -rf bin ;
    rm -rf include ;
    rm -rf lib ;
    rm -rf src ;
    rm -rf pyvenv.cfg ;
    rm -rf .vercel/cache ;
    rm -rf ../.vercel/cache ;
    rm -rf ../node_modules ;
    rm requirements.txt
    ls -lah
fi

if [[ "$1" = "test" ]]; then
    # echo "Error: no test specified" && exit 1
    echo "Run test..."
    python -m pytest
    echo "Done..."
fi

if [[ "$1" = "run" || "$1" = "" ]]; then
    pipenv run chalice local --port ${PORT}
    exit
fi

if [ "$1" = "deploy" ]; then
    pipenv requirements > requirements.txt
    pipenv run chalice deploy --stage dev
    exit
fi
if [ "$1" = "deploy_prod" ]; then
    pipenv requirements > requirements.txt
    pipenv run chalice deploy --stage prod
    exit
fi

if [ "$1" = "create_stack" ]; then
    aws cloudformation deploy --template-file "${APP_DIR}/.chalice/dynamodb_cf_template.yaml" --stack-name "${AWS_STACK_NAME}"
    # aws cloudformation describe-stack-events --stack-name "${AWS_STACK_NAME}"
fi

if [ "$1" = "delete_app" ]; then
    # Delete application
    pipenv run chalice delete
    exit
fi

if [ "$1" = "delete_stack" ]; then
    # Delete DynamoDb table
    aws cloudformation delete-stack --stack-name "${AWS_STACK_NAME}"
fi
