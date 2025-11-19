# SystemD Service Setup Guide

This guide explains how to set up and troubleshoot the Learn Armenian Alphabet bot as a systemd service.

## Prerequisites

1. Python 3.8+ installed
2. Virtual environment created at `/root/learnarmenianalphabet/venv`
3. All dependencies installed in the virtual environment

## Initial Setup

### 1. Create Environment File

The bot requires a `.env` file with your Telegram bot token. Create it from the example:

```bash
cd /root/learnarmenianalphabet
cp .env.example .env
```

Then edit the `.env` file and add your Telegram bot token:

```bash
nano .env
```

Update the line:
```
TELEGRAM_API=your_actual_telegram_bot_token_here
```

### 2. Create Startup Script

Create the startup script from the template:

```bash
cd /root/learnarmenianalphabet
cp learn_armenian.sh.template learn_armenian.sh
chmod +x learn_armenian.sh
```

If your installation is not in `/root/learnarmenianalphabet`, edit the script and update the `PROJECT_DIR` variable:

```bash
nano learn_armenian.sh
# Change PROJECT_DIR="/root/learnarmenianalphabet" to your actual path
```

### 3. Create SystemD Service

Create the service file:

```bash
sudo nano /etc/systemd/system/learnarmenian.service
```

Add the following content:

```ini
[Unit]
Description=Learn Armenian Alphabet Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/learnarmenianalphabet
ExecStart=/root/learnarmenianalphabet/learn_armenian.sh
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 4. Enable and Start Service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable learnarmenian.service

# Start the service
sudo systemctl start learnarmenian.service

# Check status
sudo systemctl status learnarmenian.service
```

## Troubleshooting

### Check Service Status

```bash
sudo systemctl status learnarmenian.service
```

### View Logs

```bash
# Recent logs
sudo journalctl -u learnarmenian.service -n 50

# Follow logs in real-time
sudo journalctl -u learnarmenian.service -f

# Logs since last boot
sudo journalctl -u learnarmenian.service -b
```

### Common Issues

#### 1. "source: not found" Error

**Problem**: The script uses `#!/bin/sh` but tries to use bash-specific `source` command.

**Solution**: The updated `learn_armenian.sh` script uses `#!/bin/bash` which supports the `source` command.

#### 2. "Telegram token is missing"

**Problem**: The `.env` file is missing or doesn't contain the `TELEGRAM_API` variable.

**Solution**:
```bash
cd /root/learnarmenianalphabet
cp .env.example .env
nano .env  # Add your actual Telegram bot token
```

#### 3. Virtual Environment Not Found

**Problem**: The virtual environment doesn't exist or is in a different location.

**Solution**:
```bash
cd /root/learnarmenianalphabet
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Permission Issues

**Problem**: The script doesn't have execute permissions.

**Solution**:
```bash
chmod +x /root/learnarmenianalphabet/learn_armenian.sh
```

### Restart Service After Changes

After making any changes to the script or configuration:

```bash
sudo systemctl daemon-reload
sudo systemctl restart learnarmenian.service
sudo systemctl status learnarmenian.service
```

## Service Management Commands

```bash
# Start service
sudo systemctl start learnarmenian.service

# Stop service
sudo systemctl stop learnarmenian.service

# Restart service
sudo systemctl restart learnarmenian.service

# Check status
sudo systemctl status learnarmenian.service

# Enable on boot
sudo systemctl enable learnarmenian.service

# Disable on boot
sudo systemctl disable learnarmenian.service

# View logs
sudo journalctl -u learnarmenian.service
```

## File Locations

- **Service file**: `/etc/systemd/system/learnarmenian.service`
- **Startup script**: `/root/learnarmenianalphabet/learn_armenian.sh`
- **Environment file**: `/root/learnarmenianalphabet/.env`
- **Application**: `/root/learnarmenianalphabet/main.py`
- **Virtual environment**: `/root/learnarmenianalphabet/venv`
- **Logs**: `/root/learnarmenianalphabet/logs/bot.log`

## Environment Variables

The following environment variables can be set in the `.env` file:

- `TELEGRAM_API` - **Required**: Your Telegram bot token
- `OPENAI_API_KEY` - Optional: OpenAI API key for AI features
- `TTS_API_KEY` - Optional: Text-to-speech API key
- `DB_PATH` - Database file path (default: `translations.db`)
- `LOG_LEVEL` - Logging level (default: `INFO`)
- `LOG_FILE` - Log file name (default: `bot.log`)
