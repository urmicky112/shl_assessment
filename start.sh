#!/bin/bash
export TOKENIZERS_PARALLELISM=false
export CHROMA_SERVER_HOST=0.0.0.0
uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-8000}