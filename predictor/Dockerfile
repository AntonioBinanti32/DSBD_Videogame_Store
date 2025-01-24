FROM python:3.11-slim

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

WORKDIR /usr/src/app/src

EXPOSE 3000
CMD ["python", "main.py"]
