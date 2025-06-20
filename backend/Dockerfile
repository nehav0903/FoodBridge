# Use official Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy contents of the backend folder into the container
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port (only needed for web service)
EXPOSE 5000

# Default command (change in Railway UI for the background job)
CMD ["python", "main.py"]
