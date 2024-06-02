@echo off

rem Путь к вашему виртуальному окружению
set VIRTUAL_ENV_PATH=.venv

rem Активация виртуального окружения
call %VIRTUAL_ENV_PATH%\Scripts\activate

rem Запуск Flask-приложения
python run.py

rem Деактивация виртуального окружения после работы
deactivate
