# Hub Service

Монорепозиторий для всех проектов с автоматическим деплоем через Coolify.

## Структура проекта

```
hub-service/
├── telegram-bots/          # Telegram боты
│   └── weather-today/      # Бот прогноза погоды
├── api-services/           # API сервисы
│   └── example-api/        # Пример API с публичным доступом
├── web-apps/               # Веб-приложения
└── docker-compose.yml      # Общий compose для всех сервисов
```

## Добавление нового проекта

1. Создайте папку в соответствующей категории:
   - `telegram-bots/` - для Telegram ботов
   - `api-services/` - для API сервисов
   - `web-apps/` - для веб-приложений

2. Добавьте `Dockerfile` в папку проекта

3. Добавьте сервис в `docker-compose.yml`:

### Для Telegram бота (без публичного доступа)

```yaml
bot-name:
  build:
    context: ./telegram-bots/bot-name
  environment:
    TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
  restart: unless-stopped
  networks:
    - internal
```

### Для API/Web приложения (с публичным доступом)

```yaml
service-name:
  build:
    context: ./api-services/service-name
  environment:
    PORT: 8000
  expose:
    - "8000"
  labels:
    - traefik.enable=true
    - traefik.http.routers.service-name.rule=Host(`hub.pavbox.com`) && PathPrefix(`/service-name`)
    - traefik.http.routers.service-name.entrypoints=websecure
    - traefik.http.routers.service-name.tls.certresolver=le
    - traefik.http.services.service-name.loadbalancer.server.port=8000
    # Middleware для удаления префикса пути
    - traefik.http.middlewares.service-name-strip.stripprefix.prefixes=/service-name
    - traefik.http.routers.service-name.middlewares=service-name-strip
  restart: unless-stopped
  networks:
    - traefik
    - internal
```

## CI/CD

GitHub Actions автоматически:
1. Определяет измененные проекты
2. Собирает Docker образы только для измененных проектов
3. Пушит образы в GitHub Container Registry (ghcr.io)
4. Триггерит webhook Coolify для деплоя

### Настройка GitHub Secrets

Добавьте в настройках репозитория (Settings → Secrets and variables → Actions):
- `REDEPLOY_TOKEN` - API токен Coolify (создается в Settings → API Tokens)
- `APP_UPDATE_HOST` - URL для обновления переменных (например, `https://coolify.yourdomain.com/api/v1/applications`)
- `HOOK_HOST` - URL для webhook деплоя (например, `https://coolify.yourdomain.com/api/v1/deploy`)
- `COOLIFY_APP_ID` - UUID приложения в Coolify
- `TELEGRAM_WEATHER_BOT_TOKEN` - токен Telegram бота для WeatherToday

**Как найти COOLIFY_APP_ID:**
1. Откройте ваше приложение в Coolify
2. Скопируйте UUID из URL: `https://coolify.yourdomain.com/project/xxx/application/{uuid}`

## Настройка Coolify

1. Укажите домен: `hub.pavbox.com`
2. Подключите репозиторий и выберите ветку
3. Coolify автоматически использует `docker-compose.yml`
4. Traefik должен быть настроен как внешняя сеть

## Роутинг

Все приложения доступны через единый домен с разными путями:
- `hub.pavbox.com/example-api` - Example API
- Telegram боты работают через polling и не имеют публичных URL

## Переменные окружения

Переменные окружения автоматически передаются из GitHub Secrets в Coolify через CI/CD pipeline на основе файла маппинга `.github/env-mapping.json`.

**Для добавления переменной к новому проекту:**

1. Добавьте секрет в GitHub (Settings → Secrets and variables → Actions)

2. Добавьте маппинг в `.github/env-mapping.json`:

```json
{
  "telegram-bots/weather-today": {
    "TELEGRAM_WEATHER_BOT_TOKEN": "TELEGRAM_WEATHER_BOT_TOKEN"
  },
  "telegram-bots/new-bot": {
    "TELEGRAM_NEW_BOT_TOKEN": "TELEGRAM_NEW_BOT_TOKEN"
  }
}
```

3. Добавьте case в `.github/workflows/build-and-deploy.yml` (шаг "Build environment variables JSON"):

```bash
"TELEGRAM_NEW_BOT_TOKEN")
  ENV_JSON=$(echo "$ENV_JSON" | jq --arg key "$var_name" --arg val "${{ secrets.TELEGRAM_NEW_BOT_TOKEN }}" '. + {($key): $val}')
  ;;
```

4. Используйте переменную в `docker-compose.yml`

**Как это работает:**
- Workflow определяет какие проекты изменились
- Читает `.github/env-mapping.json` для этих проектов
- Автоматически собирает только нужные переменные
- Отправляет их в Coolify перед деплоем
