# Deployment

Instructions for deploying Readly to a Linux server.

## Setup systemd service

1. Edit the service file and replace `YOUR_USER` with your Linux username:
```bash
sed -i 's/YOUR_USER/your_actual_username/g' ~/readly/deploy/readly.service
```

2. Copy the service file:
```bash
sudo cp ~/readly/deploy/readly.service /etc/systemd/system/
```

3. Reload systemd and enable the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable readly
sudo systemctl start readly
```

4. Check status:
```bash
sudo systemctl status readly
```

## Common commands

```bash
# View logs
sudo journalctl -u readly -f

# Restart service
sudo systemctl restart readly

# Stop service
sudo systemctl stop readly
```

## After code updates

```bash
cd ~/readly
git pull
sudo systemctl restart readly
```
