# 🗣️ Tlk-io Telegram Bot

A Telegram bot + terminal client to chat in [tlk.io](https://tlk.io) rooms.

> Built by [Taz](https://t.me/modsbytaz)

---

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create a `.env` File

```env
BOT_TOKEN=your_telegram_bot_token
OWNER_ID=your_telegram_user_id
DEFAULT_ROOM=lovezone
DEFAULT_NICKNAME=Tom
```
---

## ▶️ Run the Bot

### Telegram Bot
```bash
python bot.py
```

### Terminal Chat Client
```bash
python tlkio.py
```

---

## 💬 Telegram Commands

| Command              | Description                      |
|----------------------|----------------------------------|
| /join [room] [nick]  | Join a room                      |
| /stop                | Leave the room                   |
| .b/.i/.c/.st/.l/.q   | Markdown formatting              |
| .s query             | Search image on Google           |

---

## 🖥️ Terminal Commands

- `.stop` — Exit  
- `.leave` — Change room  
- `.help` — Show formatting commands

---

## ⚙️ Features

- Join any `tlk.io` room
- Real-time Telegram ↔ Tlk.io bridge
- Markdown support & image search
- Works via Telegram or terminal

---

## 🧑‍💻 Author

**Taz** — [@modsbytaz](https://t.me/modsbytaz)  
Bot: [@TazChatBot](https://t.me/TazChatBot)
