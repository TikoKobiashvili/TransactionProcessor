# Use an official Python runtime as a parent image
FROM python:3.10-slim
# Set the PYTHONPATH
ENV PYTHONPATH=./app
# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the necessary Python packages
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "main.py"]
