#!/bin/sh
cd api
python -m uvicorn index:app --reload