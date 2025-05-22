# Dockerfile for AWS Lambda with Selenium
# (alternative for chalice deploy that stopped working because the chrome/chromedriver exceeded the size limit)
# 2025-05-22 | CR
#
# References:
#   GS-204 - Fix Mediabros APIs and currency exchanges
#   https://github.com/umihico/docker-selenium-lambda
#   https://stackoverflow.com/questions/71746654/how-do-i-add-selenium-chromedriver-to-an-aws-lambda-function
#
# Source: https://github.com/umihico/docker-selenium-lambda/blob/main/Dockerfile

# Envvars for build
CHROMEDRIVER_VERSION="136.0.7103.113"
PYTHON_VERSION="3.11"

# FROM public.ecr.aws/lambda/python@sha256:4a4ca5ff3639ba963e218fa66417fbcdfa19a03fd71c5011acf4e4eed542392e as build
FROM public.ecr.aws/lambda/python:${PYTHON_VERSION} as build

RUN dnf install -y unzip && \
    curl -Lo "/tmp/chromedriver-linux64.zip" "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" && \
    curl -Lo "/tmp/chrome-linux64.zip" "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chrome-linux64.zip" && \
    unzip /tmp/chromedriver-linux64.zip -d /opt/ && \
    unzip /tmp/chrome-linux64.zip -d /opt/

FROM public.ecr.aws/lambda/python:${PYTHON_VERSION}

RUN dnf install -y atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel nss mesa-libgbm

# RUN pip install selenium==4.32.0
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY --from=build /opt/chrome-linux64 /opt/chrome
COPY --from=build /opt/chromedriver-linux64 /opt/chromedriver

# Copy app.py and chalicelib to handler function
COPY app.py ${LAMBDA_TASK_ROOT}/
COPY chalicelib ${LAMBDA_TASK_ROOT}/chalicelib

CMD [ "app.app" ]