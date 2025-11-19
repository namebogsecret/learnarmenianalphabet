# Systemd Service Setup for Learn Armenian Bot

## Overview

This document describes the systemd service setup for running the Learn Armenian Alphabet Telegram bot as a background service that starts automatically on system boot.

## Files

- `learn_armenian.sh` - Main startup script that loads environment variables and starts the bot
- `learnarmenian.service` - Systemd service unit file
- `install_service.sh` - Installation script to set up the service

## Installation

### Automatic Installation (Recommended)

Run the installation script as root:

```bash
sudo bash install_service.sh
```

This script will:
1. Copy all files to `/root/learnarmenianalphabet`
2. Install the systemd service file
3. Enable the service to start on boot
4. Optionally start the service immediately

### Manual Installation

If you prefer to install manually:

1. **Copy files to the installation directory:**
   ```bash
   sudo mkdir -p /root/learnarmenianalphabet
   sudo cp -r * /root/learnarmenianalphabet/
   ```

2. **Make the startup script executable:**
   ```bash
   sudo chmod +x /root/learnarmenianalphabet/learn_armenian.sh
   ```

3. **Create .env file:**
   ```bash
   sudo cp /root/learnarmenianalphabet/.env.example /root/learnarmenianalphabet/.env
   sudo nano /root/learnarmenianalphabet/.env
   ```
   Configure your Telegram bot token and other settings.

4. **Install the systemd service:**
   ```bash
   sudo cp /root/learnarmenianalphabet/learnarmenian.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable learnarmenian.service
   ```

5. **Start the service:**
   ```bash
   sudo systemctl start learnarmenian.service
   ```

## Service Management

### Start the service
```bash
sudo systemctl start learnarmenian.service
```

### Stop the service
```bash
sudo systemctl stop learnarmenian.service
```

### Restart the service
```bash
sudo systemctl restart learnarmenian.service
```

### Check service status
```bash
sudo systemctl status learnarmenian.service
```

### Enable service to start on boot
```bash
sudo systemctl enable learnarmenian.service
```

### Disable service from starting on boot
```bash
sudo systemctl disable learnarmenian.service
```

## Viewing Logs

### View recent logs
```bash
sudo journalctl -u learnarmenian.service -n 50
```

### Follow logs in real-time
```bash
sudo journalctl -u learnarmenian.service -f
```

### View logs from today
```bash
sudo journalctl -u learnarmenian.service --since today
```

## Troubleshooting

### Issue: "source: not found" error

**Cause:** The script was being run with `/bin/sh` instead of `/bin/bash`, and the `source` command is a bash-specific feature.

**Solution:**
- The `learn_armenian.sh` script now uses `#!/bin/bash` shebang
- Uses `. .env` (dot notation) instead of `source .env` for compatibility
- The systemd service file explicitly calls `/bin/bash`

### Issue: Service fails to start

1. **Check the service status:**
   ```bash
   sudo systemctl status learnarmenian.service
   ```

2. **Check the logs:**
   ```bash
   sudo journalctl -u learnarmenian.service -n 100
   ```

3. **Verify .env file exists and is configured:**
   ```bash
   sudo ls -la /root/learnarmenianalphabet/.env
   ```

4. **Test the startup script manually:**
   ```bash
   sudo /root/learnarmenianalphabet/learn_armenian.sh
   ```

### Issue: Environment variables not loaded

Make sure the `.env` file:
- Exists in `/root/learnarmenianalphabet/`
- Has correct permissions (readable by root)
- Contains all required variables (see `.env.example`)

## Security Notes

The service runs as root and includes these security settings:
- `NoNewPrivileges=true` - Prevents privilege escalation
- `PrivateTmp=true` - Uses a private /tmp directory

## Service Configuration

The service is configured with:
- **Automatic restart:** Service restarts automatically if it crashes
- **Restart delay:** 10 seconds between restart attempts
- **Logging:** All output goes to systemd journal
- **Network dependency:** Waits for network to be available before starting

## Updating the Bot

To update the bot code:

1. **Update the code in your development directory**
2. **Re-run the installation script:**
   ```bash
   sudo bash install_service.sh
   ```

   Or manually:
   ```bash
   sudo rsync -av /path/to/your/dev/directory/ /root/learnarmenianalphabet/
   sudo systemctl restart learnarmenian.service
   ```

## Uninstallation

To remove the service:

```bash
sudo systemctl stop learnarmenian.service
sudo systemctl disable learnarmenian.service
sudo rm /etc/systemd/system/learnarmenian.service
sudo systemctl daemon-reload
```

Optionally remove the installation directory:
```bash
sudo rm -rf /root/learnarmenianalphabet
```
