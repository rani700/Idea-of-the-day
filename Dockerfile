# Start with the official Playwright image which includes Node.js, Python, and browsers
FROM mcr.microsoft.com/playwright:v1.44.0-jammy

# Set the working directory
WORKDIR /app

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*


# Install the single-file-cli tool
RUN npm install -g single-file-cli

# Copy your Python script and requirements file
COPY . .
COPY requirements.txt .

# Install Python packages
RUN pip install -r requirements.txt

# Default command to keep the container running
# CMD ["tail", "-f", "/dev/null"]
CMD ["python3", "daily_scraper.py"]