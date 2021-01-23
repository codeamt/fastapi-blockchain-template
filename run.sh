export BLOCKCHAIN_URL=http://127.0.0.1:5000
export INITIAL_DIFFICULTY=2

uvicorn --port 5000 --host 127.0.0.1 main:blockchain ---reload