ssh ec2-user@ec2-3-141-106-24.us-east-2.compute.amazonaws.com  << EOF
cd AI-Secretary
git pull origin main
cd backend
# Kill any instance of the server
pkill -f uvicorn
source .venv/bin/activate
pip install -r requirements.txt
./run.sh
EOF
