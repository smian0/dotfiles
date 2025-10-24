#!/usr/bin/env bash
# Wheel Strategy Dashboard Launcher

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎯 Wheel Strategy Dashboard${NC}"
echo -e "${BLUE}==============================${NC}\n"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -q -r requirements.txt

# Launch dashboard
echo -e "\n${GREEN}✓ Starting dashboard...${NC}\n"
echo -e "${BLUE}Dashboard will open at: http://localhost:8501${NC}\n"

streamlit run wheel_app.py

# Deactivate on exit
deactivate
