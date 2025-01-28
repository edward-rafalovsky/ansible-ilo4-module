FROM python:3.9-slim

# Install git for collection development
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create directory structure for ansible collections
RUN mkdir -p /root/.ansible/collections/ansible_collections/hpe/ilo_ssh

# Set working directory
WORKDIR /root/.ansible/collections/ansible_collections/hpe/ilo_ssh

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Create directory for test results
RUN mkdir -p /test_results

# Default command to run unit tests
CMD ["python", "-m", "pytest", "tests/unit/", "-v"] 