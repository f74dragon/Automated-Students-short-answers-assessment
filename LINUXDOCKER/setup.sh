#!/bin/bash
set -e  # Exit on error

echo "🚀 Starting setup for Automated Short Answer Assessment system..."

# 1. Create project directory
mkdir -p /project
cd /project

# 2. Clone the repository
echo "📥 Cloning repository..."
git clone https://github.com/f74dragon/Automated-Students-short-answers-assessment.git
cd Automated-Students-short-answers-assessment

# 3. Install system packages
echo "📦 Installing required packages..."
apt update
apt install -y git python3 python3-venv python3-pip nodejs npm \
               postgresql postgresql-contrib curl

# 4. Start PostgreSQL service
echo "🐘 Starting PostgreSQL..."
service postgresql start

# 5. Install Ollama
echo "🧠 Installing Ollama..."
curl https://ollama.ai/install.sh | sh

# 5b. Start Ollama server in background
echo "🧠 Starting Ollama in server mode..."
ollama serve > /var/log/ollama.log 2>&1 &


# 6. Build the frontendd
echo "🛠️ Building frontend..."
cd frontend
npm install
npm run build
cd ..

# 6b. Install and configure Nginx
echo "📦 Installing and configuring Nginx..."
apt install -y nginx

# Create custom nginx.conf
cat <<EOF > /etc/nginx/sites-available/default
server {
    listen 80;
    root /var/www/html;

    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

# Move React build output to Nginx directory
rm -rf /var/www/html/*
cp -r frontend/build/* /var/www/html/

# Start Nginx
echo "🚀 Starting Nginx server..."
service nginx start



# 7. Set up Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 8. Install Python dependencies
echo "📚 Installing backend requirements..."
cd backend
pip install -r requirements.txt
cd ..

# 9. Configure environment variables
echo "⚙️ Creating .env file manually..."
cat <<EOF > .env
# Example environment variables
DOCKERIZED=false
EOF

# 10. Initialize PostgreSQL user and database
echo "🗄️ Creating PostgreSQL user and database..."
su - postgres -c "psql -c \"CREATE ROLE \\\"user\\\" LOGIN PASSWORD 'mypassword';\" || true"
su - postgres -c "psql -c \"CREATE DATABASE mydatabase OWNER \\\"user\\\";\" || true"

# 11. Start FastAPI backend
echo "🧠 Starting FastAPI backend..."
source venv/bin/activate
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
