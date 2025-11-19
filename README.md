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

## Production Deployment

For production deployment with systemd service:
- See [SERVICE_SETUP.md](SERVICE_SETUP.md) for detailed instructions on setting up the bot as a systemd service
- The `learn_armenian.sh` script is provided for use with systemd

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
