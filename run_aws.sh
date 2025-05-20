#!/bin/sh
# run_aws.sh
# 2023-02-02 | CR
#
APP_DIR='chalicelib'
AWS_STACK_NAME='mediabros-apis-stack'

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

ENV_FILESPEC=""
if [ -f "./.env" ]; then
    ENV_FILESPEC="./.env"
fi
if [ -f "../.env" ]; then
    ENV_FILESPEC="../.env"
fi
if [ "$ENV_FILESPEC" != "" ]; then
    echo ""
    echo "Loading environment variables from $ENV_FILESPEC..."
    echo "" 
    set -o allexport; source ${ENV_FILESPEC}; set +o allexport ;
fi

if [ "$PORT" = "" ]; then
    PORT="5001"
fi

if [ "$PYTHON_VERSION" = "" ]; then
    echo "Error: PYTHON_VERSION is not set" && exit 1
fi
PYTHON3_EXEC='/usr/local/bin/python${PYTHON_VERSION}'

# ..........

create_chalice_config_json_file() {
    echo ""
    echo "Creating chalice config file..."
    echo ""
    CHALICE_DIR="${BASE_DIR}/.chalice"
    cp ${CHALICE_DIR}/config-example.json ${CHALICE_DIR}/config.json
    # For each variable defined in .env file, replace the placeholder in config.json
    for var in $(cat .env | cut -d'=' -f1); do
        # Filter the comments
        if [ "$(echo $var | cut -d'=' -f2 | cut -c1)" = "#" ]; then
            # echo "Skipping comment: $var"
            continue
        fi
        # Fix the "@" in the ${var} value
        var_value="${!var}"
        var_value=${var_value//"@"/"\\@"}
        # echo "${var}: ${var_value}"
        # Replace the placeholder in config.json
        perl -i -pe "s|${var}_placeholder|${var_value}|g" ${CHALICE_DIR}/config.json
    done
}

run_clean() {
    echo ""
    echo "Cleaning..."
    echo ""
    cd ${APP_DIR} ;
    # deactivate ;
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
    cd ..
    echo ""
    echo "Removing pipenv virtual environment..."
    echo ""
    pipenv --rm
    echo ""
    echo "Re-creating the virtual environment and installing dependencies..."
    echo ""
    pipenv install
    echo ""
    echo "Done cleaning..."
    echo ""
}

replace_github_pat() {
    echo ""
    echo "Replacing Github PAT in $1 by the string \${GITHUB_API_KEY}..."
    echo ""
    perl -i -pe "s|github_pat_[^@]*|\\$\{GITHUB_API_KEY}|g" $1
}

restore_github_pat() {
    echo ""
    echo "Restoring Github PAT in $1..."
    echo ""
    perl -i -pe "s|\\$\{GITHUB_API_KEY}[^@]*|${GITHUB_API_KEY}|g" $1
}

run_requirements_txt() {
    echo ""
    echo "Generating requirements.txt..."
    echo ""
    pipenv requirements > ${BASE_DIR}/requirements.txt
}

run_pipfile() {
    echo ""
    echo "Installing dependencies..."
    echo ""
    pwd

    if [ ! -f ".python-version" ]; then
        echo ""
        echo "Error: '.python-version' not found in: ${BASE_DIR}"
        echo ""
        echo "Please run:"
        echo "  pyenv install ${PYTHON_VERSION}"
        echo "  pyenv local ${PYTHON_VERSION}"
        echo ""
        exit 1
    fi

    # echo ""
    # echo "Setting Python version..."
    # echo ""
    # # https://realpython.com/intro-to-pyenv/
    # pipenv --python $(cat ${BASE_DIR}/.python-version)

    if [ "${BCV_EXCHANGE_RATES_BRANCH}" != "" ]; then
        BCV_EXCHANGE_RATES_BRANCH="@${BCV_EXCHANGE_RATES_BRANCH}"
    fi
    if [ "${COP_EXCHANGE_RATES_BRANCH}" != "" ]; then
        COP_EXCHANGE_RATES_BRANCH="@${COP_EXCHANGE_RATES_BRANCH}"
    fi
    if [ "${MONITOR_EXCHANGE_RATES_BRANCH}" != "" ]; then
        MONITOR_EXCHANGE_RATES_BRANCH="@${MONITOR_EXCHANGE_RATES_BRANCH}"
    fi

    echo ""
    echo "Restoring Github PAT in Pipfile..."
    echo ""
    restore_github_pat ${BASE_DIR}/Pipfile

    echo ""
    echo "Installing monitor-exchange-rates from git branch: ${MONITOR_EXCHANGE_RATES_BRANCH}"
    echo "Installing bcv-exchange-rates from git branch: ${BCV_EXCHANGE_RATES_BRANCH}"
    echo "Installing cop-exchange-rates from git branch: ${COP_EXCHANGE_RATES_BRANCH}"

    # echo ""
    # echo "Installing dependencies..."
    # echo ""
    # pipenv install \
    #     requests \
    #     openai \
    #     "python-jose[cryptography]" \
    #     "passlib[bcrypt]" \
    #     wheel \
    #     python-multipart \
    #     python-dotenv

    # # FasAPI
    # echo ""
    # echo "Installing FastAPI..."
    # echo ""
    # pipenv install fastapi
    # # pipenv install a2wsgi
    
    # # Mongo
    # echo ""
    # echo "Installing MongoDB dependencies..."
    # echo ""
    # pipenv install \
    #     pymongo \
    #     werkzeug

    # # AWS
    # echo ""
    # echo "Installing AWS dependencies..."
    # echo ""
    # pipenv install \
    #     boto3 \
    #     chalice

    echo ""
    echo "Installing dependencies..."
    echo ""
    pipenv install \
        git+https://${GITHUB_API_KEY}@github.com/tomkat-cr/monitor-exchange-rates.git${MONITOR_EXCHANGE_RATES_BRANCH} \
        git+https://github.com/tomkat-cr/bcv-exchange-rates${BCV_EXCHANGE_RATES_BRANCH} \
        git+https://github.com/tomkat-cr/cop-exchange-rates${COP_EXCHANGE_RATES_BRANCH} \
        requests \
        openai \
        "python-jose[cryptography]" \
        "passlib[bcrypt]" \
        wheel \
        python-multipart \
        python-dotenv \
        fastapi \
        pymongo \
        werkzeug \
        boto3 \
        chalice

    run_requirements_txt

    echo ""
    echo "Replacing Github PAT in requirements.txt with perl by the string \${GITHUB_API_KEY}..."
    echo ""
    replace_github_pat ${BASE_DIR}/requirements.txt

    echo ""
    echo "Replacing Github PAT in Pipfile with perl by the string \${GITHUB_API_KEY}..."
    echo ""
    replace_github_pat ${BASE_DIR}/Pipfile

    echo ""
    echo "Done..."
}

# ..........

if [ "$1" = "pipfile" ]; then
    run_pipfile
    exit
fi

if [ "$1" = "clean" ]; then
    run_clean
    exit
fi

if [ "$1" = "update" ]; then
    run_clean
    rm -rf ${BASE_DIR}/requirements.txt
    run_pipfile
    exit
fi

if [[ "$1" = "test" ]]; then
    # echo "Error: no test specified" && exit 1
    echo "Run test..."
    python -m pytest
    echo "Done..."
    exit
fi

if [[ "$1" = "run" || "$1" = "" ]]; then
    create_chalice_config_json_file
    pipenv run chalice local --port ${PORT}
    exit
fi

if [ "$1" = "deploy" ]; then
    create_chalice_config_json_file
    pipenv requirements > ${BASE_DIR}/requirements.txt
    pipenv run chalice deploy --stage dev
    exit
fi
if [ "$1" = "deploy_prod" ]; then
    create_chalice_config_json_file
    pipenv requirements > ${BASE_DIR}/requirements.txt
    pipenv run chalice deploy --stage prod
    exit
fi

if [ "$1" = "create_stack" ]; then
    create_chalice_config_json_file
    aws cloudformation deploy --template-file "${APP_DIR}/.chalice/dynamodb_cf_template.yaml" --stack-name "${AWS_STACK_NAME}"
    # aws cloudformation describe-stack-events --stack-name "${AWS_STACK_NAME}"
    exit
fi

if [ "$1" = "delete_app" ]; then
    create_chalice_config_json_file
    # Delete application
    pipenv run chalice delete
    exit
fi

if [ "$1" = "delete_stack" ]; then
    # Delete DynamoDb table
    create_chalice_config_json_file
    aws cloudformation delete-stack --stack-name "${AWS_STACK_NAME}"
    exit
fi

if [ "$1" = "install" ]; then
    # Install dependencies
    pipenv install
    exit
fi

if [ "$1" = "requirements" ]; then
    # Install dependencies from requirements.txt
    run_requirements_txt
    exit
fi

echo ""
echo "Error: no command specified"
exit 1
