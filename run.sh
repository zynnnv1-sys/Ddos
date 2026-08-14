#!/bin/bash
echo "[*] Installing dependencies..."
pip install -r requirements.txt
echo "[*] Running DDoS script..."
python3 ddos.py
