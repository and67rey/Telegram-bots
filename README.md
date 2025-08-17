# Telegram-bots
Try different Telegram bots

## Motivational Telegram Bot

This Telegram bot provides inspiring quotes to help users start their day with motivation. Users can get random quotes in both English and Russian, with the option to switch languages.

### Features:

* `/start` - Welcome message and default language set to Russian.
* `/motivate` - Receive a random motivational quote.
* `/help` - Information on how to use the bot.
* `/english` - Switch quotes to English.
* `/russian` - Switch quotes to Russian.

### Setup:

1. Create a `.env` file with your Telegram Bot Token:

   ```
   TOKEN=your-telegram-bot-token
   ```
2. Install the required libraries:

   ```bash
   pip install telebot requests deep-translator python-dotenv
   ```
3. Run the bot:

   ```bash
   python inspire_me_bot.py
   ```
You can try this bot here https://t.me/NiceQuoteBot

Enjoy your daily motivation!

## Weather Telegram Bot

This Telegram bot provides weather updates and forecasts for any city. Simply enter the name of the city, and the bot will give you the current weather. You can also request a 3-day weather forecast by adding the word "прогноз" to the city name.

### Features:
- `/start` - Welcome message and instructions on how to use the bot.
- `/help` - List of commands and how to use the bot.
- Enter a city name - Get the current weather.
- Add the word "прогноз" to the city name - Get the 3-day weather forecast.

### Setup:
1. Create a `.env` file with your API keys:
```

API_TOKEN=your-telegram-bot-token
OPENWEATHER_API_KEY=your-openweather-api-key

````
2. Install the required libraries:
```bash
pip install aiogram aiohttp python-dotenv
````

3. Run the bot:

   ```bash
   python weather_bot.py
   ```
You can try this bot here https://t.me/what_wheather_bot

Enjoy your weather updates!

## Tic-Tac-Toe Telegram Bot

This is a Telegram bot that allows users to play the classic game of Tic-Tac-Toe against the bot. The bot supports three difficulty levels: Easy, Medium, and Hard. Users can start a new game, view the current state of the board, and challenge the bot to a match.

### Features:
- `/start` - Start a new game and choose the difficulty level.
- `/help` - Instructions on how to play the game.
- `/quit` - End the current game.
- `/level` - Change the difficulty level during the game.
- Players can choose between Easy, Medium, or Hard difficulty for the bot's moves.
  
### Gameplay:
- Users play as "❌", and the bot plays as "🟢".
- The bot offers different strategies depending on the selected difficulty level.
- The game ends when there is a winner or a draw, with options to play again.

### Setup:
1. Create a `.env` file with your Telegram Bot Token:
```

TOKEN=your-telegram-bot-token

````
2. Install required dependencies:
```bash
pip install telebot python-dotenv
````

3. Run the bot:

   ```bash
   python tic_tac_toe_bot.py
   ```

You can try this bot here https://t.me/play_T3_bot

Enjoy the game and challenge the bot to see if you can win!

## Reversi Telegram Bot

This Telegram bot allows users to play the classic game of Reversi (also known as Othello) against a bot. The game is played on an 8x8 board, where players take turns placing their pieces to capture their opponent's pieces.

### Features:
- `/start` - Start a new game and play against the bot.
- `/help` - Get instructions on how to play the game.
- Players are represented as ⚫, and the bot plays as 🟡.
- The goal is to capture as many pieces as possible by flipping your opponent's pieces.

### Gameplay:
- The game alternates between the user (⚫) and the bot (🟡).
- Players can make valid moves to flip the opponent’s pieces.
- The game ends when neither player can make a valid move.
- The player with the most pieces at the end wins.

### Setup:
1. Create a `.env` file with your Telegram Bot Token:
```

TOKEN=your-telegram-bot-token

````
2. Install required dependencies:
```bash
pip install telebot python-dotenv
````

3. Run the bot:

   ```bash
   python reversi_bot.py
   ```
You can try this bot here https://t.me/PlayReversiBot

Challenge the bot and see if you can outsmart it at Reversi!


