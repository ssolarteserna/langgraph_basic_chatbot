# Use slim Python image
FROM python:3.10-slim

WORKDIR /app

# Install system deps (useful for Python builds)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files (except those in .dockerignore)
COPY . .

# Expose Jupyter
EXPOSE 8888

# Run JupyterLab by default
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser"]
