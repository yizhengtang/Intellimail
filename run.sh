#!/bin/bash

case "$1" in
  run)
    cd backend && uvicorn app.main:app --reload --port 8000
    ;;
  start)
    cd backend && uvicorn app.main:app --port 8000
    ;;
  *)
    echo "Run script for fastAPI"
    echo "  1. run (with reload)"
    echo "  2. start"
    ;;
esac
