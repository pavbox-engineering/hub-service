# Руководство по добавлению переменных окружения

## Быстрый старт

При добавлении нового проекта с переменными окружения нужно обновить 3 места:

### 1. GitHub Secrets

```
Settings → Secrets and variables → Actions → New repository secret
```

Добавьте ваш секрет (например, `TELEGRAM_NEW_BOT_TOKEN`)

### 2. .github/env-mapping.json

Добавьте маппинг для вашего проекта:

```json
{
  "telegram-bots/weather-today": {
    "TELEGRAM_WEATHER_BOT_TOKEN": "TELEGRAM_WEATHER_BOT_TOKEN"
  },
  "telegram-bots/new-bot": {
    "TELEGRAM_NEW_BOT_TOKEN": "TELEGRAM_NEW_BOT_TOKEN"
  },
  "api-services/my-api": {
    "API_KEY": "API_KEY",
    "DATABASE_URL": "DATABASE_URL"
  }
}
```

**Формат:**
- **Ключ** (`telegram-bots/new-bot`): путь к проекту
- **Значение**: объект, где:
  - **Ключ** (`TELEGRAM_NEW_BOT_TOKEN`): имя переменной в docker-compose.yml
  - **Значение** (`"TELEGRAM_NEW_BOT_TOKEN"`): имя секрета в GitHub

### 3. .github/workflows/build-and-deploy.yml

В шаге "Build environment variables JSON" добавьте case для вашей переменной:

```bash
case $secret_name in
  "TELEGRAM_WEATHER_BOT_TOKEN")
    ENV_JSON=$(echo "$ENV_JSON" | jq --arg key "$var_name" --arg val "${{ secrets.TELEGRAM_WEATHER_BOT_TOKEN }}" '. + {($key): $val}')
    ;;
  "TELEGRAM_NEW_BOT_TOKEN")
    ENV_JSON=$(echo "$ENV_JSON" | jq --arg key "$var_name" --arg val "${{ secrets.TELEGRAM_NEW_BOT_TOKEN }}" '. + {($key): $val}')
    ;;
  "API_KEY")
    ENV_JSON=$(echo "$ENV_JSON" | jq --arg key "$var_name" --arg val "${{ secrets.API_KEY }}" '. + {($key): $val}')
    ;;
esac
```

## Пример: Добавление нового Telegram бота

**Проект:** `telegram-bots/crypto-bot`  
**Переменная:** Токен бота

### Шаг 1: Добавьте GitHub Secret

Имя: `TELEGRAM_CRYPTO_BOT_TOKEN`  
Значение: `7123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw`

### Шаг 2: Обновите env-mapping.json

```json
{
  "telegram-bots/weather-today": {
    "TELEGRAM_WEATHER_BOT_TOKEN": "TELEGRAM_WEATHER_BOT_TOKEN"
  },
  "telegram-bots/crypto-bot": {
    "TELEGRAM_CRYPTO_BOT_TOKEN": "TELEGRAM_CRYPTO_BOT_TOKEN"
  }
}
```

### Шаг 3: Добавьте case в workflow

```bash
"TELEGRAM_CRYPTO_BOT_TOKEN")
  ENV_JSON=$(echo "$ENV_JSON" | jq --arg key "$var_name" --arg val "${{ secrets.TELEGRAM_CRYPTO_BOT_TOKEN }}" '. + {($key): $val}')
  ;;
```

### Шаг 4: Используйте в docker-compose.yml

```yaml
crypto-bot:
  build:
    context: ./telegram-bots/crypto-bot
  environment:
    TELEGRAM_CRYPTO_BOT_TOKEN: ${TELEGRAM_CRYPTO_BOT_TOKEN}
  restart: unless-stopped
  networks:
    - internal
```

Готово! ✅ Теперь при изменении `telegram-bots/crypto-bot/` workflow автоматически:
1. Соберет Docker образ
2. Отправит переменную `TELEGRAM_CRYPTO_BOT_TOKEN` в Coolify
3. Триггерит редеплой

## Проект с несколькими переменными

Пример API сервиса с базой данных:

### env-mapping.json

```json
{
  "api-services/payment-service": {
    "PAYMENT_API_KEY": "PAYMENT_API_KEY",
    "STRIPE_SECRET": "STRIPE_SECRET",
    "DATABASE_URL": "DATABASE_URL",
    "REDIS_URL": "REDIS_URL"
  }
}
```

### workflow case

```bash
"PAYMENT_API_KEY")
  ENV_JSON=$(echo "$ENV_JSON" | jq --arg key "$var_name" --arg val "${{ secrets.PAYMENT_API_KEY }}" '. + {($key): $val}')
  ;;
"STRIPE_SECRET")
  ENV_JSON=$(echo "$ENV_JSON" | jq --arg key "$var_name" --arg val "${{ secrets.STRIPE_SECRET }}" '. + {($key): $val}')
  ;;
"DATABASE_URL")
  ENV_JSON=$(echo "$ENV_JSON" | jq --arg key "$var_name" --arg val "${{ secrets.DATABASE_URL }}" '. + {($key): $val}')
  ;;
"REDIS_URL")
  ENV_JSON=$(echo "$ENV_JSON" | jq --arg key "$var_name" --arg val "${{ secrets.REDIS_URL }}" '. + {($key): $val}')
  ;;
```

## Как это работает

1. **Git push** → GitHub Actions запускается
2. **Detect changes** → определяет `telegram-bots/crypto-bot` изменился
3. **Build environment variables** → читает `env-mapping.json`, находит:
   ```json
   "telegram-bots/crypto-bot": {
     "TELEGRAM_CRYPTO_BOT_TOKEN": "TELEGRAM_CRYPTO_BOT_TOKEN"
   }
   ```
4. **Case statement** → подставляет значение из GitHub Secrets
5. **Update Coolify** → отправляет:
   ```json
   {
     "TELEGRAM_CRYPTO_BOT_TOKEN": "7123456789:AAH..."
   }
   ```
6. **Redeploy** → Coolify перезапускает приложение с новыми переменными

## Важные моменты

✅ **DO:**
- Используйте описательные имена для секретов
- Группируйте переменные по проектам в env-mapping.json
- Добавляйте case для каждой новой переменной

❌ **DON'T:**
- Не храните секреты в коде или .env файлах в репозитории
- Не используйте одинаковые имена для разных проектов
- Не забывайте обновлять все 3 места

## Troubleshooting

**Переменная не передается в Coolify:**
- Проверьте что секрет добавлен в GitHub
- Проверьте точное совпадение имен в env-mapping.json
- Проверьте что case добавлен в workflow

**Ошибка в логах workflow:**
- Проверьте валидность JSON в env-mapping.json
- Проверьте синтаксис case statement
- Проверьте что проект существует в репозитории



