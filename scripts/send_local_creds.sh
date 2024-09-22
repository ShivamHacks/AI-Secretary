#!/bin/bash

LOCAL_FILE="../backend/openai_key.txt"
REMOTE_DIR="~/AI-Secretary/backend/"
read -p "Enter the EC2 instance (e.g., ec2-user@ec2-instance): " EC2_INSTANCE
scp "$LOCAL_FILE" "$EC2_INSTANCE":"$REMOTE_DIR"
echo "File $LOCAL_FILE copied to $EC2_INSTANCE:$REMOTE_DIR"
