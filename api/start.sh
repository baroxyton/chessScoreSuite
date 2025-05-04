#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"

uvicorn main:app --host 0.0.0.0 --port 5554 # 55,54 = e4,e5
