# Use official Python base image with conda
FROM continuumio/miniconda3:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CONDA_ENV_NAME=credit_rating_transition

# Install system dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy conda environment file
COPY environment.yml .

# Create conda environment
RUN conda env create -f environment.yml

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "credit_rating_transition", "/bin/bash", "-c"]

# Copy requirements and install additional pip packages
COPY config/requirements_pipeline.txt .
RUN pip install -r requirements_pipeline.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/raw data/processed rag_cache

# Set permissions
RUN chmod +x examples/*.py

# Expose port for Streamlit
EXPOSE 8501

# Set the default command
CMD ["conda", "run", "-n", "credit_rating_transition", "streamlit", "run", "src/dashboard/credit_rating_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"] 