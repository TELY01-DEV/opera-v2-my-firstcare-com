#!/usr/bin/env python3
import base64
import json
from datetime import datetime

# JWT token from the logs
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJvcGVyYXBhbmVsIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzUyMDM1MzY5fQ.XMmIWumSwM17TS0FKyIkhMZ6W44dWX7BJ275c4ywwJg'

# Split the token
parts = token.split('.')
if len(parts) != 3:
    print("Invalid JWT token format")
    exit(1)

# Decode the payload (second part)
payload_base64 = parts[1]

# Add padding if needed
padding = '=' * (4 - len(payload_base64) % 4)
payload_base64 += padding

# Decode base64
payload_bytes = base64.b64decode(payload_base64)
payload = json.loads(payload_bytes.decode('utf-8'))

print('Token payload:', json.dumps(payload, indent=2))

# Check expiration time
exp_timestamp = payload['exp']
exp_datetime = datetime.fromtimestamp(exp_timestamp)
current_time = datetime.now()

print(f'Token expires at: {exp_datetime}')
print(f'Current time: {current_time}')
print(f'Time until expiry: {exp_datetime - current_time}')
print(f'Token expired: {current_time > exp_datetime}')

# Check if token has short expiry
duration = exp_datetime - datetime.fromtimestamp(exp_timestamp - 3600)  # Assume 1 hour token
print(f'Token appears to have {duration} duration')
