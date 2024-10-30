FROM python:3.10

WORKDIR /workspace

COPY . /workspace/

RUN apt-get update && apt-get install -y build-essential

RUN pip install -r /workspace/requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "TIMEGEN_Demo.py", "--server.port=8501", "--server.address=0.0.0.0","--server.enableCORS=false", "--server.enableXsrfProtection=false"]