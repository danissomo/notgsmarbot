#!/bin/bash

# Определяем абсолютные пути
SCRIPT_DIR=$(dirname "$(realpath "$0")")
PYTHON_SCRIPT=$(which notgsmarbot)
VENV_PATH="$SCRIPT_DIR/venv"
SERVICE_NAME="notgsmar.service"
SYSTEMD_PATH="/etc/systemd/system/$SERVICE_NAME"

# Проверяем, что файл Python-скрипта существует
if [ ! -f "$PYTHON_SCRIPT" ]; then
  echo "Ошибка: Файл $PYTHON_SCRIPT не найден!"
  exit 1
fi

# Проверяем, что виртуальное окружение существует
if [ ! -d "$VENV_PATH" ]; then
  echo "Ошибка: Виртуальное окружение $VENV_PATH не найдено!"
  exit 1
fi

# Создаём файл службы
echo "Создаём файл службы $SYSTEMD_PATH..."
sudo bash -c "cat > $SYSTEMD_PATH" <<EOL
[Unit]
Description=Telegram Bot Service for notgsmar
After=network.target

[Service]
User=$(whoami)
Group=$(whoami)
WorkingDirectory=$SCRIPT_DIR
ExecStart=$VENV_PATH/bin/python $PYTHON_SCRIPT
Environment="PYTHONUNBUFFERED=1"
KillMode=process
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

# Перезагружаем systemd и активируем службу
echo "Перезагружаем systemd..."
sudo systemctl daemon-reload

echo "Активируем службу..."
sudo systemctl enable "$SERVICE_NAME"

echo "Запускаем службу..."
sudo systemctl start "$SERVICE_NAME"

# Проверяем статус службы
echo "Проверяем статус службы..."
sudo systemctl status "$SERVICE_NAME"

echo "Готово! Служба настроена и запущена."
