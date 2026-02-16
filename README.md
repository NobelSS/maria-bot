# Maria-Bot

A private Discord bot for tracking League of Legends games among friends.

## Features
- Tracks specified players via their Riot ID.
- Sends live notifications when a tracked player starts a match.
- Posts a summary (Win/Loss, KDA, Champion) when a match ends.

## Setup

1.  **Prerequisites**:
    -   Python 3.8+
    -   A Discord Bot Token (from [Discord Developer Portal](https://discord.com/developers/applications))
    -   A Riot Games API Key (from [Riot Developer Portal](https://developer.riotgames.com/))

2.  **Installation**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration**:
    -   Create a `.env` file in the root directory (already present in template):
        ```env
        DISCORD_TOKEN=your_discord_bot_token
        RIOT_API_KEY=your_riot_api_key
        ```
    -   Ensure the bot has permissions to read messages and send messages in the channel named `league-feed`.
    -   Create a text channel named `league-feed` in your Discord server.
    
4.  **Running the Bot**:
    ```bash
    python -m src.bot
    ```

## Usage

-   `!track GameName#Tag` - Start tracking a player (e.g., `!track Feyr#NA1`).
-   `!untrack GameName#Tag` - Stop tracking a player.

## Notes
-   The bot checks for active games every minute.
-   Active game notifications will appear in the `#league-feed` channel.
-   Ensure your Riot API key is valid (development keys expire every 24 hours).
