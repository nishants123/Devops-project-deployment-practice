FROM python:latest

WORKDIR /myapp

COPY . .

RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]