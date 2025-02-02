import logging
from colorlog import ColoredFormatter

# Настройка логирования


def setup_logging():
    # Создаем обработчик для вывода логов в консоль
    handler = logging.StreamHandler()

    # Форматирование с цветом для каждого уровня
    formatter = ColoredFormatter(
        # Формат логирования с цветами
        '%(log_color)s[%(levelname)s]: %(message)s',
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG': 'cyan',  # Цвет для уровня DEBUG
            'INFO': 'green',   # Цвет для уровня INFO
            'WARNING': 'yellow',  # Цвет для WARNING
            'ERROR': 'red',    # Цвет для ERROR
            'CRITICAL': 'magenta'  # Цвет для CRITICAL
        }
    )

    # Применяем форматирование к обработчику
    handler.setFormatter(formatter)

    # Получаем логгер
    logger = logging.getLogger('bot')
    logger.setLevel(logging.DEBUG)  # Устанавливаем уровень логирования INFO

    # Добавляем обработчик в логгер
    logger.addHandler(handler)

    return logger


# Пример использования логирования
LOGGER = setup_logging()
