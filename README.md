# Armenian Learning Bot

This repository contains a Telegram bot for learning the Armenian alphabet and basic vocabulary. The bot supports text transliteration, spaced repetition for memorising words and a set of word games.

## Features
- **Transliteration** of Russian text to Armenian letters
- **Spaced repetition** using the SM-2 algorithm
- Simple **word games** such as hangman and word scramble
- Utility functions for **basic expressions**

For more details about the modules and instructions see the [docs](docs/README.md) directory.

## Quick start
1. Install the dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in your tokens
3. Run the bot: `python main.py`
4. Or use the helper script `./run.sh` which pulls updates,
   installs dependencies and starts the application.

## Running as a System Service (Linux)

To run the bot as a systemd service that starts automatically on boot:

1. Run the installation script:
   ```bash
   sudo bash install_service.sh
   ```

2. The service will be installed and enabled to start on boot.

For detailed information about service management, troubleshooting, and configuration, see [docs/SYSTEMD_SERVICE.md](docs/SYSTEMD_SERVICE.md).

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
