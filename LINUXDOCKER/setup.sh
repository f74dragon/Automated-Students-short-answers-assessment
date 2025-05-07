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

# 6. Build and serve the frontend
echo "🛠️ Setting up frontend..."
cd frontend
npm install
npm run build
cd ..

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

# 10. PostgreSQL initialization instructions
echo "📘 Database setup manual step (run inside psql):"
echo
echo "  1. Run: 'su - postgres'"
echo "  2. Then: 'psql'"
echo "  3. Inside psql, run:"
echo "     CREATE ROLE \"user\" LOGIN PASSWORD 'mypassword';"
echo "     CREATE DATABASE mydatabase OWNER \"user\";"
echo "     \q to exit"
echo
echo "🔥 Once that's done, you can start the backend with:"
echo "  source venv/bin/activate"
echo "  uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001"
echo
echo "✅ Frontend is already built and can be served via npm start in ./frontend"

echo "✅ Setup complete."
