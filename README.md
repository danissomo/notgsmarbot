# notgsmarbot

`notgsmarbot` is a Telegram bot that fetches phone specifications from [Kimovil](https://www.kimovil.com), renders a characteristics card, and sends it to the chat.

## Requirements

- Python 3.9 or higher

## Installation

1. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
2. Install the package:
   ```sh
   pip install .
   ```

## Usage

After installation, `notgsmarbot` provides a console script `notgsmarbot` that accepts arguments for configuration.

Run the bot with:
```sh
notgsmarbot [-t TOKEN]  # or --token TOKEN
```
where `TOKEN` is your Telegram bot token. This argument is optional and updates the value in `config.yaml`.

### First-time Setup
The first execution is required to configure all parameters properly.

## License
MIT

