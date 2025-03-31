FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ /app/app/
COPY run.py /app/

EXPOSE 5000

CMD ["python3", "run.py"]