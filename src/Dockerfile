FROM python:3.10

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . ./src

# ARG GUNICORN_WORKERS
# ENV GUNICORN_WORKERS=4
# ENV GUNICORN_WORKERS=1

# CMD ["gunicorn", "-b", "0.0.0.0", "--log-level", "debug", "-w", $GUNICORN_WORKERS, "src.index:app"]
CMD ["gunicorn", "-b", "0.0.0.0", "--log-level", "debug", "-w", "1", "src.index:app"]
