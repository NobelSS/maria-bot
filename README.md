# Maria-Bot

A private Discord bot for tracking League of Legends games among friends.

## Features
- Tracks specified players via their Riot ID.
- Sends live notifications of started matches (with opponent ranks and win rates).
- Posts a post-game summary (Win/Loss, KDA, Champion).
- **DM Subscriptions**: Users can subscribe to get notifications directly in their DMs.

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
    -   Create a `.env` file in the root directory:
        ```env
        DISCORD_TOKEN=your_discord_bot_token
        RIOT_API_KEY=your_riot_api_key
        ```
    -   (Optional) Create a text channel named `league-feed` in your Discord server for public alerts.
    
4.  **Running the Bot**:
    ```bash
    python main.py
    ```

## Usage

-   `!track GameName#Tag` - Start tracking a player.
-   `!untrack GameName#Tag` - Stop tracking a player.
-   `!subscribe` - Receive game notifications via DM.
-   `!unsubscribe` - Stop receiving DM notifications.

## Notes
-   The bot uses a local SQLite database (`maria.db`) to store tracked users and subscribers.
-   The bot checks for active games every minute.
-   Ensure your Riot API key is valid (development keys expire every 24 hours).
