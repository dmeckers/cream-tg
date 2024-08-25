# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set environment variables to ensure output is sent straight to the console
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create and set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code to the container
COPY . .

# Expose the port that the bot will use (if applicable)
EXPOSE 8080

# Run the bot
CMD ["python", "main.py"]
