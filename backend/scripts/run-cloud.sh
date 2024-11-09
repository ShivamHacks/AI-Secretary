source .venv/bin/activate

# Make sure to run on 0.0.0.0 so accessible from outside, not just localhost
nohup uvicorn server:app --host 0.0.0.0 --port 8000 --reload > uvicorn.log 2>&1 &
