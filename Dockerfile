# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create .streamlit directory and copy config
RUN mkdir -p .streamlit

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]
