#!/bin/bash

# Check if NVM is installed
if ! [ -x "$(command -v nvm)" ]; then
  echo "NVM is not installed. Installing NVM..."

  # Install NVM
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash

  # Load NVM into the current shell session
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
else
  echo "NVM is already installed."
fi

# Install Node.js using NVM
echo "Installing Node.js using NVM..."
nvm install node

# Use the latest installed Node.js version
nvm use node

# Install project dependencies
echo "Installing project dependencies..."
npm install

echo "Node.js and project dependencies installed."
