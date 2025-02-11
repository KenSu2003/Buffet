#!/bin/bash

# Log file to store ngrok output
NGROK_LOG_FILE="/home/admin/Buffet/ngrok_ssh.log"

# Start ngrok for SSH and log output
echo "Starting ngrok for SSH tunneling..."
nohup ngrok tcp 22 > "$NGROK_LOG_FILE" 2>&1 &

# Give ngrok some time to initialize
sleep 3

# Extract the ngrok SSH address from the log file
NGROK_ADDRESS=$(grep -o 'tcp://[0-9a-zA-Z.-]*:[0-9]*' "$NGROK_LOG_FILE" | head -n 1)

# Check if the ngrok address was found
if [ -n "$NGROK_ADDRESS" ]; then
    echo "Ngrok tunnel established."
    echo "SSH address: $NGROK_ADDRESS"
    echo "You can connect using: ssh pi@$NGROK_ADDRESS"
else
    echo "Failed to retrieve ngrok address. Check $NGROK_LOG_FILE for details."
fi
