FROM python:3.10

WORKDIR /workspace

COPY . /workspace/

RUN apt-get update && apt-get install -y build-essential

RUN pip install -r /workspace/requirements.txt

RUN chmod +x run.sh

EXPOSE 8501

CMD ["bash", "-c", "./run.sh"]