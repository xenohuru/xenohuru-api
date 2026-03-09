#!/bin/bash
# One-time setup script for PythonAnywhere
# Run this in the PythonAnywhere bash console ONCE to set up the project.
#
# Usage: bash /home/xenohuru/pa_setup.sh

set -e
PA_USERNAME="xenohuru"
PROJECT_DIR="/home/${PA_USERNAME}/xenohuru-api"
VENV_DIR="/home/${PA_USERNAME}/.virtualenvs/xenohuru-venv"
REPO_URL="https://github.com/xenohuru/xenohuru-api.git"

echo "=== Step 1: Clone repository ==="
if [ -d "$PROJECT_DIR" ]; then
  echo "Directory already exists, pulling latest..."
  cd "$PROJECT_DIR" && git pull origin main
else
  git clone "$REPO_URL" "$PROJECT_DIR"
fi

echo "=== Step 2: Create virtual environment ==="
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

echo "=== Step 3: Install dependencies ==="
pip install -r "$PROJECT_DIR/requirements.txt" --quiet

echo "=== Step 4: Check .env file ==="
if [ ! -f "$PROJECT_DIR/src/.env" ]; then
  echo ""
  echo "⚠️  .env file missing! Upload it to: $PROJECT_DIR/src/.env"
  echo "    Use the PA Files tab or: nano $PROJECT_DIR/src/.env"
  echo "    Reference: $PROJECT_DIR/src/.env.example"
  echo ""
else
  echo ".env found ✓"
fi

echo "=== Step 5: Run migrations ==="
cd "$PROJECT_DIR"
python src/manage.py migrate --no-input

echo "=== Step 6: Collect static files ==="
python src/manage.py collectstatic --no-input --clear

echo ""
echo "✅ Setup complete!"
echo ""
echo "=== Next steps in PythonAnywhere dashboard ==="
echo "1. Go to Web tab → your web app"
echo "2. Set Source code: $PROJECT_DIR"
echo "3. Set Virtualenv: $VENV_DIR"
echo "4. Edit WSGI file — replace contents with the wsgi_config.py snippet:"
echo "   cat $PROJECT_DIR/wsgi_config.py"
echo "5. Reload the web app"
