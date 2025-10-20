#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"

uvicorn main:app --host 127.0.0.1  --port 5554 # 55,54 = e4,e5
