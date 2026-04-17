# Base image - pulls the latest official Python image from Docker Hub
FROM python:latest

# Sets the working directory inside the container (creates if not exists)
WORKDIR /myapp

# Copies everything from current local directory to /myapp in container
COPY . .

# Runs pip install inside container to install all dependencies from requirements.txt
RUN pip install -r requirements.txt

# Exposes port 5000 to allow external access to the container (documentation purpose)
EXPOSE 5000

# Default command to run when container starts - launches the Python application
CMD ["python", "app.py"]