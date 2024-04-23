# OmsuNewsBot

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
```shell
.venv\Scripts\activate
```

## Install lib:

### Unix/macOS

```shell
python3 -m pip install -r requirements.txt
```

### Windows

```shell
py -m pip install -r requirements.txt
```