# Discord AIBot with Claude Integration

A Discord bot that uses Claude AI to respond to messages while maintaining conversation context.

## Features
- Responds when mentioned or when "aibot" is typed
- Maintains conversation context by tracking recent message history
- Uses Claude 3 Sonnet model for AI responses
- Supports Discord mentions and formatting

## Prerequisites
- Python 3.8+
- Discord Bot Token
- Anthropic API Key

## Required Packages
```bash
pip install discord.py anthropic python-dotenv
```

## Setup
1. Create a `.env` file in the project root with:
```
DISCORD_TOKEN=your_discord_token
CLAUDE_API_KEY=your_claude_api_key
```

2. Set up a Discord bot and get its token:
   - Go to Discord Developer Portal
   - Create New Application
   - Add Bot
   - Enable Message Content Intent
   - Copy Token to .env file

3. Get Claude API key from Anthropic and add to .env file

## Usage
1. Run the script:
```bash
python bot.py
```

2. In Discord:
   - Mention the bot (@AIBot) or type "aibot" in any message
   - Bot will respond using message history for context
   - Responses limited to 2000 characters (Discord limit)

## Features Explained
- Tracks last 10 messages for context
- Formats chat history for Claude's understanding
- Maintains consistent bot personality
- Supports user mentions
- Handles message content safely

## Limitations
- 2000 character response limit
- 10 message history limit
- Requires appropriate Discord bot permissions

## Note
Remember to keep your API keys secure and never share them publicly.