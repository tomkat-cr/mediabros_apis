#!/bin/sh
# run_aws.sh
# 2023-02-02 | CR
#
APP_DIR='chalicelib'
AWS_STACK_NAME='mediabros-apis-stack'

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo ""
echo "BASE_DIR: ${BASE_DIR}"
echo ""

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

deploy_with_sls() {
    local stage="$1"
    local remove_previous="$2"
    echo ""
    echo "Deploying with SLS | Stage: ${stage} | Remove previous: ${remove_previous}"
    echo ""

    echo ""
    echo "Checking if 3rd party packages are installed..."
    echo ""
    if ! grep -q "monitor-exchange-rates" Pipfile
    then
        install_3rd_party_pakages
    fi

    run_requirements_txt

    cd ${BASE_DIR}
    pwd

    if ! sls --version
    then
        echo ""
        echo "Installing serverless..."
        echo ""
        # if ! npm install -g serverless@^3
        if ! npm install -g serverless
        then
            echo "Error installing serverless" && exit 1
        fi
    fi

    echo ""
    echo "Creating mediabros_apis..."
    echo ""

    if [ "${AWS_REGION}" = "" ]; then
        AWS_REGION="us-east-1"
    fi
    export AWS_REGION

    if [ "${BUILD_PATH}" = "" ]; then
        BUILD_PATH="/tmp/mediabros_apis_build"
    fi

    if [ "${MEDIABROS_APIS_REPO}" = "" ]; then
        MEDIABROS_APIS_REPO="https://github.com/tomkat-cr/mediabros_apis"
    fi
    if [ "${MEDIABROS_APIS_BRANCH}" = "" ]; then
        MEDIABROS_APIS_BRANCH="main"
    fi

    # If MEDIABROS_APIS_REPO is a remote path, add /tree
    if [[ "${MEDIABROS_APIS_REPO}" == *"https://"* ]]; then
        MEDIABROS_APIS_REPO="${MEDIABROS_APIS_REPO}/tree/${MEDIABROS_APIS_BRANCH}"
        SLS_PARAMETERS="--template-url ${MEDIABROS_APIS_REPO} --path ${BUILD_PATH}"
    else
        SLS_PARAMETERS="--template-path ${MEDIABROS_APIS_REPO} --path ${BUILD_PATH}"
    fi

    echo ""
    echo "MEDIABROS_APIS_REPO: ${MEDIABROS_APIS_REPO}"
    echo "MEDIABROS_APIS_BRANCH: ${MEDIABROS_APIS_BRANCH}"
    echo "SLS_PARAMETERS: ${SLS_PARAMETERS}"
    echo "AWS_REGION: ${AWS_REGION}"
    echo ""

    if [[ "${MEDIABROS_APIS_REPO}" == *"https://"* ]]; then
        echo "Did you committed all changes to the remote repository?"
        echo "Press [Enter] key to continue, [Ctrl+C] or [a] to abort..."
        echo ""
        read any_key

        if [ "${any_key}" = "a" ]; then
            echo "Aborting..."
            run_remove_pat_from_files
            exit
        fi
    fi

    echo ""
    echo "Removing vendor and build directories..."
    echo ""
    rm -rf vendor
    rm -rf build
    rm -rf ${BUILD_PATH}


    if [ "${AWS_ACCOUNT_ID}" = "" ]; then
        echo ""
        echo "Getting AWS Account ID..."
        echo ""
        AWS_ACCOUNT_ID=$(aws sts get-caller-identity --output json --no-paginate | jq -r '.Account')
    fi

    echo ""
    echo "Login to ECR. AWS Account ID: ${AWS_ACCOUNT_ID}"
    echo ""

    if ! AWS_PROFILE=${AWS_PROFILE:-default} aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
    then
        echo "Error: Failed to authenticate to AWS ECR. Check your AWS credentials and permissions." && exit 1
    fi

    echo ""
    echo "Creating mediabros_apis..."
    echo ""

    # if ! sls create ${SLS_PARAMETERS}
    if ! sls --app mediabros-apis ${SLS_PARAMETERS}
    then
        echo "Error creating mediabros_apis" && exit 1
    fi

    echo ""
    echo "Deploying mediabros_apis..."
    echo ""

    if [ "${remove_previous}" = "1" ]; then
        echo ""
        echo "Removing previous mediabros_apis..."
        echo ""
        sls remove --app mediabros-apis --stage ${stage}
    fi

    # cd ${BUILD_PATH}
    if ! sls deploy --app mediabros-apis --stage ${stage}
    then
        echo "Error deploying mediabros_apis" && exit 1
    fi

    run_remove_pat_from_files

    echo ""
    echo "Invoking mediabros_apis lambda function..."
    echo ""
    if ! sls invoke --app mediabros-apis --function api --stage ${stage}
    then
        echo "Error invoking mediabros_apis" && exit 1
    fi

    echo ""
    echo "Waiting for the API Gateway to be ready..."
    echo ""
    sleep 10

    echo ""
    echo "Getting the API Gateway URL..."
    echo "" 
    sls info --app mediabros-apis --stage ${stage} 2>/tmp/sls.txt
    API_URL=$(perl -ne 'print "$1\n" if /ANY - (https[^\s]+)\s/' /tmp/sls.txt | sed 's|{proxy+}||g' | head -n 1)

    if [ "${API_URL}" = "" ]; then
        API_URL=$(perl -ne 'print "$1\n" if /GET - (https[^\s]+)\s/' /tmp/sls.txt | sed 's|{proxy+}||g' | head -n 1)
    else
        API_URL="${API_URL%?}/usdvef/1"
    fi

    if [ "${API_URL}" = "" ]; then
        echo "Error getting API Gateway URL" && exit 1
    fi
    
    echo "API URL: ${API_URL}"

    echo ""
    echo "Testing the API Gateway: ${API_URL}"
    echo ""
    
    # Simple GET request without any special headers
    if ! curl -v "${API_URL}"
    then
        echo "Error testing the API Gateway"
        exit 1
    fi
    
    echo ""
    echo "API Gateway test completed"
    echo ""

    cd ${BASE_DIR}
}

deploy_with_chalice() {
    local stage="$1"
    set_aws_chromedriver_path
    create_chalice_config_json_file
    run_add_pat_to_files
    # restore_github_pat ${BASE_DIR}/Pipfile
    # restore_github_pat ${BASE_DIR}/Pipfile.lock
    # pipenv install
    run_requirements_txt
    pipenv run chalice deploy --stage ${stage}
    run_remove_pat_from_files
    # mask_github_pat ${BASE_DIR}/requirements.txt
    # mask_github_pat ${BASE_DIR}/Pipfile
    # mask_github_pat ${BASE_DIR}/Pipfile.lock
}

run_deploy() {
    local stage="$1"
    if [ "${CHALICE_DEPLOYMENT}" = "1" ]; then
        deploy_with_chalice ${stage}
    else
        deploy_with_sls ${stage} ${REMOVE_PREVIOUS}
    fi
}

set_local_chromedriver_path() {
    export CHROMEDRIVER_PATH="./vendor/chromedriver-linux64"
}

set_aws_chromedriver_path() {
    export CHROMEDRIVER_PATH="/opt/python/lib/python%s.%s/site-packages/chromedriver-linux64"
}

download_chromedriver() {
    echo ""
    echo "Downloading chromedriver..."
    echo "Please check the following URL to get the latest version:"
    echo "https://googlechromelabs.github.io/chrome-for-testing/"
    echo ""
    if [ "${CHROMEDRIVER_INCLUDE}" = "" ]; then
        echo "CHROMEDRIVER_INCLUDE is not set, skipping chromedriver download"
        return
    fi
    if [ "${CHROMEDRIVER_VERSION}" = "" ]; then
        CHROMEDRIVER_VERSION="136.0.7103.94"
    fi
    cd ${BASE_DIR}
    mkdir -p ./vendor
    cd ./vendor
    if ! wget "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"
    then
        echo "Error downloading chromedriver" && exit 1
    fi
    if ! wget "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chrome-linux64.zip"
    then
        echo "Error downloading chrome" && exit 1
    fi
    unzip chromedriver-linux64.zip
    unzip chrome-linux64.zip
    rm chromedriver-linux64.zip
    rm chrome-linux64.zip
    cd ${BASE_DIR}
}

run_git_clone() {
    echo ""
    echo "Cloning ${1}/${2}, branch: ${3}, github api key: ${4}..."
    echo ""
    git clone https://${4}@github.com/${1}/${2}.git
    if [ "$3" != "" ]; then
        cd ${2}
        git checkout $3
        cd ..
    fi
    if [ "$5" != "" ]; then
        mv ${2}/${5} .
        rm -rf ${2}
    fi
}

load_3rd_party_pakages() {
    echo ""
    echo "Creating vendor directory..."
    echo ""

    cd ${BASE_DIR}
    rm -rf ./vendor
    mkdir -p ./vendor
    cd ./vendor

    touch __init__.py

    echo ""
    echo "Loading 3rd party packages..."
    echo ""

    run_git_clone tomkat-cr monitor-exchange-rates ${MONITOR_EXCHANGE_RATES_BRANCH} ${GITHUB_API_KEY} monitor_exchange_rates
    run_git_clone tomkat-cr bcv-exchange-rates ${BCV_EXCHANGE_RATES_BRANCH} ${GITHUB_API_KEY} bcv_exchange_rates
    run_git_clone tomkat-cr cop-exchange-rates ${COP_EXCHANGE_RATES_BRANCH} ${GITHUB_API_KEY} cop_exchange_rates

    echo ""
    echo "Checking if 3rd party packages are installed..."
    echo ""
    if grep -q "monitor-exchange-rates" Pipfile
    then
        uninstall_3rd_party_pakages
    fi

    cd ${BASE_DIR}
}

uninstall_3rd_party_pakages() {
    echo ""
    echo "Uninstalling 3rd party packages..."
    echo ""
    cd ${BASE_DIR}
    pipenv uninstall \
        monitor-exchange-rates \
        bcv-exchange-rates \
        cop-exchange-rates
}

install_3rd_party_pakages() {
    echo ""
    echo "Installing 3rd party packages..."
    echo ""
    cd ${BASE_DIR}

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
    echo "Installing monitor-exchange-rates from git branch: ${MONITOR_EXCHANGE_RATES_BRANCH}"
    echo "Installing bcv-exchange-rates from git branch: ${BCV_EXCHANGE_RATES_BRANCH}"
    echo "Installing cop-exchange-rates from git branch: ${COP_EXCHANGE_RATES_BRANCH}"

    pipenv install \
        git+https://${GITHUB_API_KEY}@github.com/tomkat-cr/monitor-exchange-rates.git${MONITOR_EXCHANGE_RATES_BRANCH} \
        git+https://github.com/tomkat-cr/bcv-exchange-rates${BCV_EXCHANGE_RATES_BRANCH} \
        git+https://github.com/tomkat-cr/cop-exchange-rates${COP_EXCHANGE_RATES_BRANCH}
}

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

    # Replace the placeholder in config.json
    if [ "${CHROMEDRIVER_INCLUDE}" != "" ]; then
        if [ "$CHROMEDRIVER_PATH" != "" ]; then
            echo ""
            echo "Setting CHROMEDRIVER_PATH in config.json..."
            echo ""
            perl -i -pe "s|CHROMEDRIVER_PATH_placeholder|${CHROMEDRIVER_PATH}|g" ${CHALICE_DIR}/config.json
        else
            echo ""
            echo "Leaving CHROMEDRIVER_PATH placeholder empty in config.json [1]..."
            echo ""
            perl -i -pe "s|CHROMEDRIVER_PATH_placeholder||g" ${CHALICE_DIR}/config.json
        fi
    else
        echo ""
        echo "Leaving CHROMEDRIVER_PATH placeholder empty in config.json [2]..."
        echo ""
        perl -i -pe "s|CHROMEDRIVER_PATH_placeholder||g" ${CHALICE_DIR}/config.json
    fi
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

mask_github_pat() {
    local file="$1"
    local string_to_replace="$2"
    if [ "${string_to_replace}" = "" ]; then
        string_to_replace="github_pat_"
    fi
    local envvar_name="$3"
    if [ "${envvar_name}" = "" ]; then
        envvar_name="GITHUB_API_KEY"
    fi
    local envvar_value="${!envvar_name}"
    echo ""
    echo "Masking Github PAT in '$file' (${envvar_name}: ${envvar_value})..."
    echo ""
    # perl -i -pe "s|github_pat_[^@]*|\\$\{GITHUB_API_KEY}|g" $1
    perl -i -pe "s|${string_to_replace}[^@]*|\\$\{${envvar_name}}|g" $file
}

restore_github_pat() {
    local file="$1"
    local envvar_name="$2"
    if [ "${envvar_name}" = "" ]; then
        envvar_name="GITHUB_API_KEY"
    fi
    local envvar_value="${!envvar_name}"
    echo ""
    echo "Restoring Github PAT in '$file' (${envvar_name}: ${envvar_value})..."
    echo ""
    # perl -i -pe "s|\\$\{GITHUB_API_KEY}[^@]*|${GITHUB_API_KEY}|g" $1
    perl -i -pe "s|\\$\{${envvar_name}}[^@]*|${envvar_value}|g" $file
}

run_requirements_txt() {
    echo ""
    echo "Generating requirements.txt..."
    echo ""
    rm -f ${BASE_DIR}/requirements.txt
    pipenv requirements > ${BASE_DIR}/requirements.txt
    restore_github_pat ${BASE_DIR}/requirements.txt
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

    echo ""
    echo "Restoring Github PAT in Pipfile..."
    echo ""
    restore_github_pat ${BASE_DIR}/Pipfile

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

    if [ "${CHALICE_DEPLOYMENT}" = "1" ]; then
        load_3rd_party_pakages
        download_chromedriver
    else
        install_3rd_party_pakages
    fi

    echo ""
    echo "Installing dependencies..."
    echo ""

    pipenv install \
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
        chalice \
        beautifulsoup4 \
        cloudscraper \
        selenium

    run_requirements_txt

    run_remove_pat_from_files

    echo ""
    echo "Done..."
}

run_add_pat_to_files() {
    echo ""
    echo "Adding Github PAT to requirements.txt..."
    echo ""
    restore_github_pat ${BASE_DIR}/requirements.txt

    echo ""
    echo "Adding Github PAT to Pipfile..."
    echo ""
    restore_github_pat ${BASE_DIR}/Pipfile
}

run_remove_pat_from_files() {
    echo ""
    echo "Removing Github PAT from requirements.txt..."
    echo ""
    mask_github_pat ${BASE_DIR}/requirements.txt

    echo ""
    echo "Removing Github PAT from Pipfile..."
    echo ""
    mask_github_pat ${BASE_DIR}/Pipfile
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
    # run_clean
    pipenv --rm
    run_pipfile
    exit
fi

if [ "$1" = "update_pakages_only" ]; then
    if [ "${CHALICE_DEPLOYMENT}" = "1" ]; then
        load_3rd_party_pakages
        download_chromedriver
    else
        install_3rd_party_pakages
    fi
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
    set_local_chromedriver_path
    create_chalice_config_json_file
    pipenv run chalice local --port ${PORT}
    exit
fi

if [ "$1" = "deploy" ]; then
    run_deploy dev
    exit
fi
if [ "$1" = "deploy_prod" ]; then
    run_deploy prod
    exit
fi

if [ "$1" = "create_stack" ]; then
    set_aws_chromedriver_path
    create_chalice_config_json_file
    aws cloudformation deploy --template-file "${APP_DIR}/.chalice/dynamodb_cf_template.yaml" --stack-name "${AWS_STACK_NAME}"
    # aws cloudformation describe-stack-events --stack-name "${AWS_STACK_NAME}"
    exit
fi

if [ "$1" = "delete_app" ]; then
    set_aws_chromedriver_path
    create_chalice_config_json_file
    # Delete application
    pipenv run chalice delete
    exit
fi

if [ "$1" = "delete_stack" ]; then
    # Delete DynamoDb table
    set_aws_chromedriver_path
    create_chalice_config_json_file
    aws cloudformation delete-stack --stack-name "${AWS_STACK_NAME}"
    exit
fi

if [ "$1" = "install" ]; then
    # Install dependencies
    run_add_pat_to_files
    pipenv install
    run_remove_pat_from_files
    exit
fi

if [ "$1" = "requirements" ]; then
    # Install dependencies from requirements.txt
    run_requirements_txt
    mask_github_pat ${BASE_DIR}/requirements.txt
    exit
fi

echo ""
echo "Error: no command specified"
exit 1
