import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Базовая директория проекта
basedir = os.path.abspath(os.path.dirname(__file__))

# Конфигурация приложения


class Config:
    # Секретный ключ приложения
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Строка подключения к базе данных
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    SQLALCHEMY_BINDS = {
        'hotels_db': os.getenv('HOTELS_DATABASE_URL')
        # Добавьте здесь другие базы данных по мере необходимости
    }

    # Отключение отслеживания изменений в базе данных
    SQLALCHEMY_TRACK_MODIFICATIONS = False
