
FROM python:3.9-slim


ENV PYTHONDONTWRITEBYTECODE 1  # Prevents Python from writing pyc files
ENV PYTHONUNBUFFERED 1  # Ensures output is not buffered


WORKDIR /app


COPY requirements.txt requirements.txt


RUN pip install --no-cache-dir -r requirements.txt



COPY . /app/



EXPOSE 8000


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
