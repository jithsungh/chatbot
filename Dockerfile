    
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir reduces image size, --upgrade pip is good practice
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's source code into the container
COPY . .

# Expose the port the app runs on (for the API)
EXPOSE 8000

# The default command to run when the container starts.
# We will run the API by default. We can override this for ingestion.
# Use 0.0.0.0 to make it accessible from outside the container.
CMD ["uvicorn", "src.app.index:app", "--host", "0.0.0.0", "--port", "8080"]