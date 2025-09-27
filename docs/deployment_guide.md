# Deployment Guide

This guide provides detailed instructions for deploying the Intelligent Chatbot application to a production environment.

## Prerequisites

Before you begin, ensure you have the following installed on your server:
-   Git
-   Python 3.9+
-   Docker and Docker Compose (for Docker-based deployment)

---

## Option 1: Deployment with Docker (Recommended)

Using Docker is the recommended method for deployment as it encapsulates the application and its dependencies in a self-contained environment.

### Step 1: Clone the Repository

Clone the project repository to your server.
```bash
git clone https://github.com/your-username/Project-FY25.git
cd Project-FY25
```

### Step 2: Configure Environment Variables

Create a `.env` file in the root of the project directory. This file will be used by Docker Compose to configure the application container.

```env
# .env file

# --- General Settings ---
LOG_LEVEL=INFO

# --- Model Configuration ---
# Choose the model to use: 'svm' or 'bert'
MODEL_TYPE=bert
# You can override the pre-trained BERT model path if needed
# BERT_MODEL_PATH=bert-base-uncased

# --- API Server Configuration ---
API_HOST=0.0.0.0
API_PORT=8080

# --- Feature Toggles ---
ENABLE_GOOGLE_FALLBACK=True
# You may need to set your Google API key if the web_search utility requires it
# GOOGLE_API_KEY=your_google_api_key
```

### Step 3: Build and Run the Docker Container

Use the provided `Dockerfile` to build and run the application.

```bash
docker build -t intelligent-chatbot .
docker run -d --name chatbot-app -p 8080:8080 --env-file .env intelligent-chatbot
```
-   `-d`: Runs the container in detached mode.
-   `--name chatbot-app`: Assigns a name to the container for easy management.
-   `-p 8080:8080`: Maps port 8080 on the host to port 8080 in the container.
-   `--env-file .env`: Loads the environment variables from your `.env` file.

### Step 4: Verify the Deployment

Check if the container is running:
```bash
docker ps
```

You can view the application logs using:
```bash
docker logs -f chatbot-app
```

---

## Option 2: Manual Deployment (Without Docker)

If you prefer to run the application directly on the host machine, follow these steps.

### Step 1: Clone the Repository and Install Dependencies

```bash
git clone https://github.com/your-username/Project-FY25.git
cd Project-FY25

# Set up a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Download NLTK Data

Run the provided script to download the necessary NLTK models.
```bash
python download_nltk_data.py
```

### Step 3: Configure Environment Variables

Export the configuration variables directly into your shell environment.
```bash
export MODEL_TYPE=bert
export LOG_LEVEL=INFO
export API_HOST=0.0.0.0
export API_PORT=8080
```
For a persistent setup, add these `export` commands to your shell's profile script (e.g., `~/.bashrc` or `~/.profile`).

### Step 4: Run the Application

Start the application using a process manager like `systemd` or `supervisor` to ensure it runs continuously.

**Example using `systemd`:**

1.  Create a service file at `/etc/systemd/system/chatbot.service`:
    ```ini
    [Unit]
    Description=Intelligent Chatbot Service
    After=network.target

    [Service]
    User=your_user
    Group=your_group
    WorkingDirectory=/path/to/Project-FY25
    EnvironmentFile=/path/to/your/environment/file.conf
    ExecStart=/path/to/Project-FY25/venv/bin/python main.py

    [Install]
    WantedBy=multi-user.target
    ```
    *Note: The `EnvironmentFile` should contain your exported variables in the `KEY=VALUE` format.*

2.  Reload `systemd` and start the service:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl start chatbot
    sudo systemctl enable chatbot  # To start on boot
    ```

**Simple method using `nohup` (not recommended for production):**
```bash
nohup python main.py > chatbot.log 2>&1 &
```

---

## Post-Deployment Checklist

1.  **Verify API Health**:
    -   From the server, run `curl http://localhost:8080/chat`. You should receive a `401 Unauthorized` error (`{"detail":"Not authenticated"}`), which indicates the API is running and secured.

2.  **Generate an Initial API Key**:
    -   The easiest way to generate your first API key is to temporarily run the application with the GUI enabled on a local machine that has access to the production `data/chatbot.db` file, and use the **API Key Management** tab.

3.  **Set Up a Reverse Proxy (Highly Recommended)**:
    -   Use a web server like **Nginx** or **Caddy** as a reverse proxy in front of the application.
    -   **Benefits**:
        -   **SSL/TLS Termination**: Easily add HTTPS to secure your API.
        -   **Load Balancing**: If you scale to multiple instances.
        -   **Caching**: Can cache static responses if needed.

    **Example Nginx Configuration:**
    ```nginx
    server {
        listen 80;
        server_name your_domain.com;

        location / {
            proxy_pass http://localhost:8080;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
    ```
    *Remember to configure SSL with a tool like Certbot.*

4.  **Check Logs**:
    -   Monitor the application logs for any startup errors or warnings.
    -   If using Docker: `docker logs chatbot-app`
    -   If using `systemd`: `journalctl -u chatbot`

5.  **Backup Data**:
    -   Regularly back up the `data/` directory, which contains the SQLite database (`chatbot.db`), intent files, and saved sessions.