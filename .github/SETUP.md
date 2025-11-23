# Настройка CI/CD для hub-service

## Шаг 1: Настройка GitHub Secrets

Перейдите в **Settings → Secrets and variables → Actions** и добавьте:

| Секрет | Описание | Где найти |
|--------|----------|-----------|
| `REDEPLOY_TOKEN` | API токен Coolify | Coolify → Settings → API Tokens → Create New Token |
| `APP_UPDATE_HOST` | URL для обновления env переменных | Например: `https://coolify.yourdomain.com/api/v1/applications` |
| `HOOK_HOST` | URL для webhook деплоя | Например: `https://coolify.yourdomain.com/api/v1/deploy` |
| `COOLIFY_APP_ID` | UUID приложения | В URL приложения: `/application/{uuid}` |
| `TELEGRAM_WEATHER_BOT_TOKEN` | Токен Telegram бота | @BotFather в Telegram |

## Шаг 2: Создание API токена в Coolify

1. Откройте Coolify
2. Перейдите в **Settings → API Tokens**
3. Нажмите **Create New Token**
4. Скопируйте токен и добавьте в GitHub Secrets

## Шаг 3: Найти ID приложения

1. Откройте ваше приложение в Coolify
2. Посмотрите на URL: `https://coolify.yourdomain.com/project/xxx/application/YOUR-APP-ID`
3. Скопируйте `YOUR-APP-ID` и добавьте в GitHub Secrets

## Шаг 4: Настройка Coolify приложения

1. **Source:** Подключите GitHub репозиторий
2. **Branch:** Укажите `main` или `master`
3. **Build Pack:** Docker Compose
4. **Domain:** `hub.pavbox.com`
5. **Network:** Убедитесь что есть внешняя сеть `traefik`

## Как это работает

1. При пуше в `main`/`master` GitHub Actions:
   - Определяет какие проекты изменились
   - Собирает Docker образы для измененных проектов
   - Пушит образы в GitHub Container Registry
   - Обновляет переменные окружения в Coolify через API
   - Триггерит перезапуск приложения

2. Coolify подтягивает новые образы и перезапускает сервисы

## Добавление нового бота или API

### Шаг 1: Добавьте токен в GitHub Secrets

Перейдите в **Settings → Secrets and variables → Actions** и добавьте новый секрет (например, `TELEGRAM_NEW_BOT_TOKEN`)

### Шаг 2: Добавьте маппинг в `.github/env-mapping.json`

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

### Шаг 3: Добавьте case в workflow

В файле `.github/workflows/build-and-deploy.yml` в шаге "Build environment variables JSON" добавьте:

```bash
"TELEGRAM_NEW_BOT_TOKEN")
  ENV_JSON=$(echo "$ENV_JSON" | jq --arg key "$var_name" --arg val "${{ secrets.TELEGRAM_NEW_BOT_TOKEN }}" '. + {($key): $val}')
  ;;
```

### Шаг 4: Добавьте сервис в `docker-compose.yml`

```yaml
new-bot:
  build:
    context: ./telegram-bots/new-bot
  environment:
    TELEGRAM_NEW_BOT_TOKEN: ${TELEGRAM_NEW_BOT_TOKEN}
  restart: unless-stopped
  networks:
    - internal
```

### Как это работает

Workflow автоматически:
1. Определяет какие проекты изменились
2. Ищет их в `env-mapping.json`
3. Собирает только нужные переменные для этих проектов
4. Отправляет в Coolify только релевантные переменные

## Troubleshooting

**Ошибка: "Invalid API token"**
- Проверьте что токен правильно скопирован в GitHub Secrets
- Создайте новый токен в Coolify если текущий истек

**Ошибка: "Application not found"**
- Проверьте правильность `COOLIFY_APP_ID`
- Убедитесь что используется полный UUID

**Переменные не обновляются**
- Проверьте логи GitHub Actions
- Убедитесь что API endpoint правильный для вашей версии Coolify

