#!/bin/sh
# run_fly_io.sh
# 2023-02-01 | CR
#
APP_DIR='chalicelib'

if [ -f "./.env" ]; then
    ENV_FILESPEC="./.env"
else
    ENV_FILESPEC="../.env"
fi
set -o allexport; source ${ENV_FILESPEC}; set +o allexport ;

if [ "$PORT" = "" ]; then
    PORT="5001"
fi
if [ "$PYTHON_VERSION" = "" ]; then
    echo "Error: PYTHON_VERSION is not set" && exit 1
fi

PYTHON3_EXEC="/usr/local/bin/python${PYTHON_VERSION}"

if [ "$1" = "deactivate" ]; then
    cd ${APP_DIR} ;
    deactivate ;
fi
if [[ "$1" != "deactivate" && "$1" != "pipfile" && "$1" != "clean" && "$1" != "set_webhook" ]]; then
    ${PYTHON3_EXEC} -m venv ${APP_DIR} ;
    . ${APP_DIR}/bin/activate ;
    cd ${APP_DIR} ;
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    else
        pip install \
            requests \
            fastapi \
            a2wsgi \
            openai \
            pymongo \
            werkzeug \
            "python-jose[cryptography]" \
            "passlib[bcrypt]" \
            wheel \
            python-multipart \
            python-dotenv
        pip install gunicorn
        pip freeze > requirements.txt
    fi
fi
if [ "$1" = "pipfile" ]; then
    deactivate ;
    pipenv lock
fi
if [ "$1" = "clean" ]; then
    echo "Cleaning..."
    deactivate ;
    rm -rf __pycache__ ;
    rm -rf bin ;
    rm -rf include ;
    rm -rf lib ;
    rm -rf pyvenv.cfg ;
    rm -rf ../.vercel/cache ;
    rm -rf .vercel/cache ;
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

if [ "$1" = "create_app" ]; then
    flyctl auth login
    flyctl apps create ${FLYIO_APP_NAME}
fi

if [[ "$1" = "create_app" || "$1" = "set_vars" ]]; then
    flyctl secrets set TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    flyctl secrets set TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
    flyctl secrets set OPENAI_API_KEY=${OPENAI_API_KEY}
    flyctl secrets set APP_NAME=${APP_NAME}
    flyctl secrets set SERVER_NAME=${SERVER_NAME}
    flyctl secrets set DB_URI=${DB_URI}
    flyctl secrets set DB_NAME=${DB_NAME}
    flyctl secrets set SECRET_KEY=${SECRET_KEY}
    flyctl secrets set ALGORITHM=${ALGORITHM}
    flyctl secrets set ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}
fi

if [ "$1" = "restart" ]; then
    flyctl apps restart ${FLYIO_APP_NAME} ;
fi

if [ "$1" = "deploy" ]; then
    flyctl deploy ;
fi
if [ "$1" = "deploy_prod" ]; then
    flyctl deploy ;
fi

if [ "$1" = "run_docker" ]; then
    docker-compose up -d
fi

if [ "$1" = "run_ngrok" ]; then
    ../node_modules/ngrok/bin/ngrok http $PORT
fi

if [[ "$1" = "run" || "$1" = "" ]]; then
    cd ..
    # python -m ${APP_DIR}.index
    gunicorn -b 0.0.0.0:${PORT} --log-level debug -w 4 'chalicelib.index:app'
fi
