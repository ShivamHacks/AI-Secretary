#!/bin/bash

read -p "Enter the EC2 instance (e.g., ec2-user@ec2-instance): " EC2_INSTANCE
read -p "Enter your git email: " user_email

# The commands to run on the EC2 instance
commands=$(cat <<'EOL'
# Step 1: Generate SSH key using provided email
ssh-keygen -t ed25519 -C "$user_email"

# Step 2: Start the ssh-agent in the background
eval "$(ssh-agent -s)"

# Step 3: Create SSH config file if it doesn't exist
touch ~/.ssh/config

# Step 4: Add configuration to SSH config file
if ! grep -q "github.com" ~/.ssh/config; then
    cat >> ~/.ssh/config <<EOF
Host github.com
  AddKeysToAgent yes
  IdentityFile ~/.ssh/id_ed25519
EOF
fi

# Step 5: Add the SSH private key to the ssh-agent
ssh-add ~/.ssh/id_ed25519

# Set right permissions
chmod 600 ~/.ssh/config

# Step 6: Copy SSH public key to clipboard (macOS pbcopy)
if [[ "$OSTYPE" == "darwin"* ]]; then
    pbcopy < ~/.ssh/id_ed25519.pub
    echo "Public key copied to clipboard!"
else
    echo "Please manually copy the public key from ~/.ssh/id_ed25519.pub"
    cat ~/.ssh/id_ed25519.pub
fi

# Notify user of completion
echo "SSH key setup complete!"

echo "Installing git"
sudo yum update -y
sudo yum install git -y
git —version
EOL
)

# Execute the commands remotely on the EC2 instance
ssh "$EC2_INSTANCE" "user_email='$user_email'; $commands"
