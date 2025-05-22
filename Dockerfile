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

FROM public.ecr.aws/lambda/python:3.11 AS build

RUN yum install -y unzip

RUN curl -Lo "/tmp/chromedriver-linux64.zip" "https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.113/linux64/chromedriver-linux64.zip"
RUN curl -Lo "/tmp/chrome-linux64.zip" "https://storage.googleapis.com/chrome-for-testing-public/136.0.7103.113/linux64/chrome-linux64.zip"

RUN unzip /tmp/chromedriver-linux64.zip -d /opt/
RUN unzip /tmp/chrome-linux64.zip -d /opt/

FROM public.ecr.aws/lambda/python:3.11

RUN yum install -y git atk cups-libs gtk3 libXcomposite alsa-lib \
    libXcursor libXdamage libXext libXi libXrandr libXScrnSaver \
    libXtst pango at-spi2-atk libXt xorg-x11-server-Xvfb \
    xorg-x11-xauth dbus-glib dbus-glib-devel nss mesa-libgbm

COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

COPY --from=build /opt/chrome-linux64 /opt/chrome
COPY --from=build /opt/chromedriver-linux64 /opt/chromedriver

COPY app.py lambda_handler.py ${LAMBDA_TASK_ROOT}/
COPY chalicelib ${LAMBDA_TASK_ROOT}/chalicelib

# Set the CMD to your handler (could also be done in serverless.yml)
CMD [ "lambda_handler.lambda_handler" ]
