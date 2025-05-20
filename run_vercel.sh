#!/bin/sh
# run_vercel.sh
# 2023-01-21 | CR
#
APP_DIR='chalicelib'
RUN_AS_MODULE=1
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
if [ "$PYTHON_VERSION" = "" ]; then
    echo "Error: PYTHON_VERSION is not set" && exit 1
fi

PYTHON3_EXEC='/usr/local/bin/python${PYTHON_VERSION}'

if [ "$1" = "deactivate" ]; then
    cd ${APP_DIR} ;
    deactivate ;
fi
if [[ "$1" != "deactivate" && "$1" != "pipfile" && "$1" != "clean" ]]; then
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
        pip freeze > requirements.txt
    fi
fi
if [ "$1" = "pipfile" ]; then
    deactivate ;
    pipenv lock
fi
if [ "$1" = "clean" ]; then
    echo "Cleaning..."
    cd ${APP_DIR} ;
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

if [ "$1" = "run_ngrok" ]; then
    ../node_modules/ngrok/bin/ngrok http $PORT
fi

if [[ "$1" = "run_module" ]]; then
    # npm run run:cli .env /cop /debug otros strings
    echo "Run module only as CLI..."
    if [ "$RUN_AS_MODULE" = "1" ]; then
        cd ..
        python -m ${APP_DIR}.index cli $2 $3 $4 $5 $6 $7 $8 $9
    else
        python -m index cli $2 $3 $4 $5 $6 $7 $8 $9
    fi
    echo "Done..."
fi

if [[ "$1" = "run" || "$1" = "" ]]; then
    if [ "$RUN_AS_MODULE" = "1" ]; then
        cd ..
    fi
    vercel dev --listen 0.0.0.0:$PORT ;
fi
if [ "$1" = "deploy_prod" ]; then
    if [ "$RUN_AS_MODULE" = "1" ]; then
        cd ..
    fi
    vercel --prod ;
fi
if [ "$1" = "rename_staging" ]; then
    if [ "$RUN_AS_MODULE" = "1" ]; then
        cd ..
    fi
    vercel alias $2 ${APP_NAME}-staging-tomkat-cr.vercel.app
fi
