#!/bin/bash

case "$1" in
  run)
    cd backend && uvicorn app.main:app --reload --port 8000
    ;;
  start)
    cd backend && uvicorn app.main:app --port 8000
    ;;
  frontend)
    cd frontend && npm run dev
    ;;
  *)
    echo "Run script for fastAPI"
    echo "  1. run (with reload)"
    echo "  2. start"
    echo "  3. frontend"
    ;;
esac
