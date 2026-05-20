#!/bin/bash

cd ./files
python -m venv .venv
.venv/bin/pip install -r requirements.txt
screen -S files bash -c ".venv/bin/uvicorn app:app --host 127.0.0.1 --port 8001"

sudo systemctl restart nginx

