# notgsmarbot

`notgsmarbot` is a Telegram bot that fetches phone specifications from [Kimovil](https://www.kimovil.com), renders a characteristics card, and sends it to the chat.

<img src="doc\botlink.png" alt="botlink" width="237" height="248">

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
usage: notgsmarbot [-h] [-t TOKEN] [--width WIDTH] [--height HEIGHT] [--scale SCALE] [-d]

Telegram bot for render specs from kimovil.com

options:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        Your telegram token
  --width WIDTH         width of viewport
  --height HEIGHT       height of viewpor
  --scale SCALE         scale of viewpor
  -d, --dryrun          Do not update config
```
where `TOKEN` is your Telegram bot token. This argument is optional and updates the value in `config.yaml`.

### First-time Setup
The first execution is required to configure all parameters properly.

### Running as a Daemon

After the initial setup, you can install the bot as a daemon using the script `setup_service.bash`.
The first execution is required to configure all parameters properly.

## License
MIT

