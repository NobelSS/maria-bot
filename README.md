# Maria-Bot

A private Discord bot for tracking League of Legends games among friends.

## Project Structure

```
maria-bot/
├── src/                   # Core bot source code
│   ├── bot.py             # Commands, task loop, embeds
│   ├── config.py          # Env vars & region config
│   ├── database.py        # SQLite helpers
│   └── riot_client.py     # Riot API wrapper
├── scripts/               # Utility / debug scripts
│   └── solo_kill.py       # Standalone match detail inspector
├── tests/                 # Tests
│   └── test_bot_functions.py
├── main.py                # Entry point
├── Dockerfile
├── requirements.txt
└── Procfile
```

## Features
- Tracks specified players via their Riot ID.
- Sends live notifications of started matches (with opponent ranks and win rates).
- Posts a post-game summary (Win/Loss, KDA, CS, Damage, Vision Score, Gold).
- **DM Subscriptions**: Users can subscribe to get notifications directly in their DMs.

## Setup

1.  **Prerequisites**:
    -   Python 3.11+
    -   A Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
    -   A Riot Games API Key (from [Riot Developer Portal](https://developer.riotgames.com/))
    -   (Optional) A text channel named `league-feed` in your Discord server for public alerts.

2.  **Configuration** — create a `.env` file in the root:
    ```env
    DISCORD_TOKEN=your_discord_bot_token
    RIOT_API_KEY=your_riot_api_key
    ```

3.  **Run locally**:
    ```bash
    pip install -r requirements.txt
    python main.py
    ```

4.  **Run with Docker**:
    ```bash
    docker build -t maria-bot .
    docker run --env-file .env -p 8000:8000 maria-bot
    ```

## Usage

| Command | Description |
|---|---|
| `!track GameName#Tag` | Start tracking a player |
| `!untrack GameName#Tag` | Stop tracking a player |
| `!subscribe` | Receive game notifications via DM |
| `!unsubscribe` | Stop receiving DM notifications |

## Notes
-   The bot uses a local SQLite database (`maria.db`) to store tracked users and subscribers.
-   The bot checks for active games every minute.
-   Ensure your Riot API key is valid (development keys expire every 24 hours).
