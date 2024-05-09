# OmsuNewsBot
## About

<<<<<<< HEAD
Бот для отправки учебного расписания в Telegram, учитывающий академические недели. Он составляет расписание как для студентов, так и для преподавателей. В качестве базы данных используется PostgreSQL, но можно использовать и другие бд.

## Установка бота

1. Клонируйте репозиторий.
2. В `config.yml` заполните все пропуски.
3. Следуйте дальнейшим инструкциям подготовки виртуального окружения.
4. Бот готов к запуску.

## Создать venv
=======
[Навигация]

## About

[Описание]

## Setup bot

1. Клонируйте этот репозиторий
2. Измените имя файла `config.yml.dist` на `config.yml`
3. В качестве драйвера используйте `postgresql+psycopg2`
4. Введите данные `PostgreSQL` в файл `config.yml`
5. Запустите базу данных  `PosgreSQL`
6. Бот готов к запуску 

## Create venv
>>>>>>> b3cbe8f121d82c6ca395df027451653658db9799

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
<<<<<<< HEAD

## Установка библиотек:
=======
```shell
.venv\Scripts\activate
```

## Install lib:
>>>>>>> b3cbe8f121d82c6ca395df027451653658db9799

### Unix/macOS

```shell
python3 -m pip install -r requirements.txt
```

### Windows

```shell
py -m pip install -r requirements.txt
```