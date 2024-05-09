# OmsuNewsBot
## About

Бот для отправки учебного расписания в Telegram, учитывающий академические недели. Он составляет расписание как для студентов, так и для преподавателей. В качестве базы данных используется PostgreSQL, но можно использовать и другие бд.

## Установка бота

1. Клонируйте репозиторий.
2. В `config.yml` заполните все пропуски.
3. Следуйте дальнейшим инструкциям подготовки виртуального окружения.
4. Бот готов к запуску.

## Создать venv

### Unix/macOS

```shell
python3 -m venv .venv
```
```shell
source .venv/bin/activate
```

### Windows

```shell
py -m venv .venv
```

## Установка библиотек:

### Unix/macOS

```shell
python3 -m pip install -r requirements.txt
```

### Windows

```shell
py -m pip install -r requirements.txt
```