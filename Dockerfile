# Use the official Python slim image based on Debian Bullseye (11)
FROM python:3.11-slim-bullseye

# Set environment variables to prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory inside the container
WORKDIR /app

# Copy the application code to the working directory
COPY . /app

# Install system dependencies and Microsoft ODBC Driver for SQL Server
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev \
    gnupg \
    curl \
    apt-transport-https \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Add Microsoft GPG key and repository for Debian 11
RUN curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/trusted.gpg.d/microsoft.gpg] https://packages.microsoft.com/repos/microsoft-debian-bullseye-prod bullseye main" > /etc/apt/sources.list.d/microsoft.list

# Install the Microsoft ODBC Driver 18 for SQL Server
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Fix missing symlinks for libodbc if necessary
RUN ln -sf /usr/lib/x86_64-linux-gnu/libodbc.so.2 /usr/lib/x86_64-linux-gnu/libodbc.so

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Ensure SSL certificates directory exists
RUN mkdir -p /app/ssl

# Copy SSL certificate into the container
COPY server-ca.pem /app/ssl/server-ca.pem

# Set appropriate permissions for SSL certificate
RUN chmod 600 /app/ssl/server-ca.pem

# Ensure ODBC configuration references the SSL certificate
RUN echo "[ODBC Driver 18 for SQL Server]\nDriver=/opt/microsoft/msodbcsql18/lib64/libmsodbcsql-18.0.so.1.1\nTrace=No\nEncrypt=Yes\nTrustServerCertificate=No\nSSLCAFile=/app/ssl/server-ca.pem" > /etc/odbcinst.ini

# Create a non-root user for enhanced security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Change ownership of the working directory
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose the application port
EXPOSE 8080

# Run the application with Waitress
CMD ["waitress-serve", "--listen=0.0.0.0:8080", "app:app"]
