FROM python:3.7
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV AWS_DEFAULT_REGION=us-east-1
WORKDIR /usr/app/
RUN \
    apt update && \
        apt-get install awscli --yes
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD [ "python", "main.py"]
