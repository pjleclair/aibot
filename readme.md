# Discord AI Chatbot

This is a Discord chatbot that integrates with OpenAI and Claude AI models to generate responses based on user messages. It allows switching between AI models dynamically and responds to direct messages and mentions.

## Features
- Supports both OpenAI and Claude AI models.
- Responds to messages in Discord channels and direct messages.
- Allows switching between AI models using `-o3` or `-claude` commands.
- Uses a system prompt template for consistent AI responses.
- Retrieves recent message history to provide context-aware replies.

## Installation & Setup
### Prerequisites
- Python 3.8+
- `pip` installed
- A Discord bot token
- API keys for OpenAI and Claude
- `.env` file with required environment variables

### Environment Variables
Create a `.env` file in the root directory with the following contents:
```
TOKEN=your_discord_bot_token
OPENAI_API_KEY=your_openai_api_key
CLAUDE_API_KEY=your_claude_api_key
SYSTEM_PROMPT=your_system_prompt_template
DICTIONARY=your_custom_dictionary (optional)
```

### Installation Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo.git
   cd your-repo
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```sh
   python bot.py
   ```

## Usage
- Mention the bot (`@botname`) or send a direct message to trigger a response.
- Use `-o3` to switch to OpenAI's model.
- Use `-claude` to switch to Claude AI's model.
- The bot automatically retrieves recent messages for context-aware responses.

## Troubleshooting
- Ensure all environment variables are correctly set.
- Verify that the bot has permissions to read messages and send messages in the desired Discord channels.
- Check the API keys and ensure they are valid.
- Look at the console output for any error messages.