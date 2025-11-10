#!/bin/bash
# 一键修复脚本
cd /Users/ck/Desktop/Project/trustagency
docker-compose build backend && docker-compose down && docker-compose up -d && sleep 20 && curl http://localhost:8001/admin/ | head -5
