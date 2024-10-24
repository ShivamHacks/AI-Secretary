# Run on the server to install HTTPS
# Actually does more - makes sure http (80) and https (443) redirect to port 8000

# Download caddy
curl -o caddy "https://caddyserver.com/api/download?os=linux&arch=amd64"

# Set it up
chmod +x caddy
sudo mv caddy /usr/bin/
sudo groupadd --system caddy
sudo useradd --system \
    --gid caddy \
    --create-home \
    --home-dir /var/lib/caddy \
    --shell /usr/sbin/nologin \
    --comment "Caddy web server" \
    caddy
sudo curl -o /etc/systemd/system/caddy.service https://raw.githubusercontent.com/caddyserver/dist/refs/heads/master/init/caddy.service

# Set up the Caddyfile
sudo mkdir -p /etc/caddy
# Replace with correct URL - directs all traffic to server
echo "managemytimeai.com {
    reverse_proxy localhost:8000
}" | sudo tee /etc/caddy/Caddyfile

# Start caddy
sudo systemctl daemon-reload
sudo systemctl enable --now caddy


# Troubleshooting
# Reload after file change
# sudo systemctl reload caddy
