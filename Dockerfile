FROM node:22-slim

# Install Python 3 and pip
RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \    
python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Install Node.js dependencies from the api subfolder
COPY api/package*.json ./
RUN npm install --production

# 2. Install Python dependencies from root
WORKDIR /app
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages || pip3 install --no-cache-dir -r requirements.txt

# 3. Copy Node.js server files from the api subfolder into /app
COPY api/ .

# 4. Copy ALL Python files from root into /app
COPY *.py ./

EXPOSE 3000
# 6. Start the server from inside the api directory where node_modules lives
CMD ["node", "server.js"]
