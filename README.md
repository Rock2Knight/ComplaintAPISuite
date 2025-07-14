# Описание установки и настройки API

## Настройка .env файла
Файл .env настравивается следующим образом:
```
DATABASE_URL=sqlite+aiosqlite:///./app/app.db  # эту строку не менять
PROMPT_SENTIMENT_API_KEY=<ваш api-key для сервиса анализа эмоциональной окраски текста>
OPEN_AI_API_KEY=<ваш api-key OpenAI API>
```

Подробное описание:<br>
**DATABASE_URL** - строка подключения к базе данных. В данном случае используется SQLite. В ней всегда указывается "sqlite+aiosqlite:///./app/app.db"<br>
**PROMPT_SENTIMENT_API_KEY** - api-key для сервиса анализа эмоциональной окраски текста. Берется из https://apilayer.com/marketplace/sentiment-api<br>
**OPEN_AI_API_KEY** - api-key для от OpenAI API. Берется из https://platform.openai.com. Возможно потребуется подписка на OpenAI API, так как бесплатная версия имеет ограничения на количество запросов.<br>

## Требования приложения:
- Python 3.12+
- Docker
- SQLite3


## Создание файла БД
1. После настройки .env файла создайте виртуальную оболчку python командой `python3 -m venv venv`.
2. Активируйте виртуальную оболочку:
- macOS/Linux: `source ./venv/bin/activate`
- Windows: `.\venv\Scripts\activate`
3. Установите зависимости в виртуальную среду командой `pip3 install -r requirements.txt` **(при включенном vpn)**.
4. Запустите миграцию базы данных командой `alembic upgrade head`.

Проверка БД:
Если вы все сделали успешно, должен появиться файл app.db в директории app. Введите команду:
```bash
sqlite3 ./app/app.db ".table"
```
Если таблицы появились, значит миграция прошла успешно.

## Настройка контейнеров Docker
1. Откройте файл docker-compose.yml
2. В сервисе *n8n* вы найдете такие строки:
```yaml
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=pirojok
      - N8N_BASIC_AUTH_PASSWORD=&as12*45sa
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - N8N_RUNNERS_ENABLED=true
      - TZ=Europe/Moscow
```

3. Вам нужно поменять поля пользователя, пароля и часовой зоны на нужные вам. Часовую зону можно посмотреть:
- macOS/Linux: в папке /usr/share/zoneinfo
- Windows: ввести в PowerShell команду: `Get-TimeZone -ListAvailable`<br>
Важно: поле TZ (часовую зону) нужно настроить как для сервиса `n8n`, так и для `complaints-api` (все эти параметр находятся в docker-compose.yml).

## Настройка раздельного туннелирования
Вам нужно настроить раздельное туннелирование **исключающего типа** для API и n8n в своем VPN-клиенте (я настраивал на windscribe, но openvpn тоже подойдет). Вот какие ip-адреса и подсети необходимо исключить:
- 127.0.0.1, 0.0.0.0, 127.0.0.1/32 (localhost)
- 178.248.238.120, 104.21.13.165, 140.82.121.3, 172.67.156.204, 213.180.204.183
- 74.125.0.0/16, 192.168.100.0/24 (сеть docker-compose)
- 172.17.0.0/16, 172.18.0.0/16, 172.19.0.0/16 (подсети docker)

Это необходимо для корректного туннелирования, так-как запросы к openai api и установка пакетов pip3 должны идти через vpn, а другие запросы не должны идти через vpn.

## Сборка docker-compose
1. Убедитесь, что у вас **установлен и запущен docker** и что **vpn запущен**.
2. Создайте сеть docker с помощью следующей команды:<br>
`docker network create --subnet=192.168.100.0/24 --driver=bridge temp_complaints_network`
3. Проверьте, что сеть создана с помощью команды: `docker network ls`. Там должна быть сеть с именем `*temp_complaints_network*`
4. Соберите образы docker с помощью `docker compose build --no-cache`
5. Запустите контейнеры с помощью `docker compose up`
6. Сервисы готовы к работе!
