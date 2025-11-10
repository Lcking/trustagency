#!/bin/bash
cd /Users/ck/Desktop/Project/trustagency/backend
/Users/ck/Desktop/Project/trustagency/backend/venv/bin/python -m uvicorn app.main:app --port 8001 --reload
