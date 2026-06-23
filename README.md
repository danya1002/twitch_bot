# Twitch & YouTube Monitor Bot

Бот для отслеживания стримов на Twitch и новых видео на YouTube.

## Установка

```bash
pip install -r requirements.txt
```

## Настройка

1. Открой `config.ini` и заполни:
   - **Twitch**: получи `CLIENT_ID` и `CLIENT_SECRET` на https://dev.twitch.tv/console/apps
   - **YouTube**: получи `API_KEY` в https://console.cloud.google.com (YouTube Data API v3)
2. Укажи логины Twitch-каналов и YouTube Channel ID

## Запуск

```bash
python twitch_youtube_bot.py
```

## Как работает

Бот каждые 60 секунд проверяет:
- 🔴 Кто зашёл в онлайн на Twitch
- 🎬 Новые видео на YouTube

Чтобы остановить — нажми `Ctrl+C`.
