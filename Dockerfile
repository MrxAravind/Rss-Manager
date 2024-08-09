# Use the official Python base image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port 6969
EXPOSE 6969

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6969", "--reload"]
