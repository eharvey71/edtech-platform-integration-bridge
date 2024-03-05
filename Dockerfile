# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Dev - Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir -r requirements-prod.txt

# Generate a random secret key and store it in an environment variable
RUN echo "FLASK_SECRET_KEY=$(openssl rand -base64 32)" > .env

# Dev - Make port 80 available to the world outside this container
EXPOSE 80

# Dev - Use Uvicorn to run the application, replace `app:app` with your application and variable
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]

# Production uses gunicorn
#CMD exec gunicorn --bind :$PORT --workers 1 --worker-class uvicorn.workers.UvicornWorker  --threads 8 app:app