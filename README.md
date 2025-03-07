# DiscordBot-Gdsc 

A powerful, modular **Discord Bot** built using **Python** and **Discord.py** for the GDSC Python subdomain.

## Features 🎉

- 🤖 AI Chatbot (using Gemini 2.0 Flash API)
- ⏰ Reminders
- 📊 Polls
- 🎶 Music (via Wavelink)
- 👋 Welcome Messages
- 📝 AI-powered Summaries
- 🗄️ SQLite database with `aiosqlite`

## Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/ryanfer123/DiscordBot-Gdsc.git
cd DiscordBot-Gdsc
```

### 2️⃣ Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3️⃣ Install Requirements
```bash
pip install -r requirements.txt
```

### 4️⃣ Create `.env` file
In the project root, add a `.env` file with your TOKENS:
```env
DISCORD_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## Disclaimer ⚠️
I couldn't upload the .env file due to the tokens present in it (discord, gemini)
So you will have to generate your own tokens by creating your own .env file.

### 5️⃣ Run the Bot
```bash
python bot.py
```

## How I Built It 🔨

- Followed **modular architecture** using **Cogs** for clean and scalable code.
- Integrated **async database handling** with `aiosqlite`.
- Used **Gemini API** for smart AI responses.
- Used **Discord Token** for bot integration.
- Used **Wavelink** for music.(Found this out on the web) 

## Project Structure 🗂️
```
discord-bot/
│
├── cogs/
│   ├── ai.py
│   ├── music.py
│   ├── polls.py
│   ├── reminders.py
│   └── welcome.py
│
├── bot.py
├── bot_database.db
├── requirements.txt
├── .env (not included in submission)
|── .gitignore
```


## 📝 License
[MIT](LICENSE)

## Created By Ryan Fernandes
- First Year CSE Core Student @ VIT Vellore
---
