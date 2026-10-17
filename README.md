# GeniusTelegramBot 🎵

Telegram-бот для быстрого поиска текстов песен через API Genius в inline-режиме.

## Возможности

- 🔍 **Inline-поиск**: введите `@имя_бота <название песни или строчка>` в любом чате, чтобы найти трек.
- 📜 **Парсинг текста**: быстрое извлечение и очистка текста песни с сайта Genius.
- ⚡ **Асинхронность**: построен на базе `aiogram 3` и `aiohttp`.

## Установка и запуск

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/FLARMIX/GeniusTelegramBot.git
   cd GeniusTelegramBot
   ```

2. **Создайте и активируйте виртуальное окружение**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте переменные окружения**:
   Создайте файл `.env` на основе `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Укажите ваши токены:
   - `BOT_TOKEN` — токен вашего Telegram-бота (получить в [@BotFather](https://t.me/BotFather))
   - `GENIUS_TOKEN` — Client Access Token от Genius API (получить на [Genius API Clients](https://genius.com/api-clients))

5. **Запустите бота**:
   ```bash
   python main.py
   ```

> ⚠️ **Важно**: для работы поиска в любом чате убедитесь, что в [@BotFather](https://t.me/BotFather) для вашего бота включен **Inline Mode** (`/setinline`).
