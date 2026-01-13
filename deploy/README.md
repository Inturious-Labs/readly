# Deployment

Instructions for deploying Readly to a Linux server.

## Setup systemd service

1. Copy the service file:
```bash
sudo cp deploy/readly.service /etc/systemd/system/
```

2. Reload systemd and enable the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable readly
sudo systemctl start readly
```

3. Check status:
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
