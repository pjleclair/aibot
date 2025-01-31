import os
import json
import discord
import locale
import anthropic
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(
    api_key=openai_api_key
)
claude_api_key = os.getenv("CLAUDE_API_KEY")
claude_client = anthropic.Anthropic(
    api_key=claude_api_key
)

TOKEN = os.getenv('TOKEN')
agent = 'claude'
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
locale.setlocale(locale.LC_ALL, '')

dictionary_str = os.getenv('DICTIONARY')
dictionary = json.loads(dictionary_str)

def getSystemPrompt(message):
    prompt_template = os.getenv('SYSTEM_PROMPT')
    if not prompt_template:
        raise ValueError("SYSTEM_PROMPT not found in environment variables")
    return prompt_template.format(
        user_mention=client.user.mention,
        author_mention=message.author.mention,
        agent=agent,
        dictionary=dictionary
    )

async def makeCompletion(message, isClaude):
    message_history = [
        msg async for msg in message.channel.history(limit=20)
    ]
    # Format history as a string to include in the system prompt
    formatted_history = "\n".join(
        [f"{msg.created_at} {msg.author.name}: {msg.content}" for msg in message_history[::-1]]
    )
    SYSTEM_PROMPT_TEXT = getSystemPrompt(message)
    AGENT_PROMPT_TEXT = f"Latest message: {message.created_at} {message.author.name}: {message.content}\n"
    
    if isClaude:
        CLAUDE_SYSTEM_PROMPT = [
            {
                "type": "text",
                "text": SYSTEM_PROMPT_TEXT
            },
            {
                "type": "text",
                "text": f"History: {formatted_history}",
                "cache_control": { "type": "ephemeral" }
            }
        ]
        claude_completion = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            system=CLAUDE_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": AGENT_PROMPT_TEXT
                }
            ]
        )
        return claude_completion
    else:
        openai_completion = openai_client.chat.completions.create(
            model="o3-mini",
            max_completion_tokens=2048,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT_TEXT
                },
                {
                    "role": "user",
                    "content": AGENT_PROMPT_TEXT
                }
            ],
        )
        return openai_completion

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    global agent
    try:
        print(message.content)
        if message.author == client.user:
            return
        is_dm = isinstance(message.channel, discord.DMChannel)
        is_bot_mention = 'aibot' in message.content.lower() or client.user.mention in message.content.lower()
        is_agent_update_request = '-o3' in message.content.lower() or '-claude' in message.content.lower()
        if is_agent_update_request:
            claude_request = '-claude' in message.content.lower()
            if claude_request:
                agent = 'claude'
            else:
                agent = 'o3'
        if is_dm or is_bot_mention:
            isClaude = agent == 'claude'
            completion = await makeCompletion(message, isClaude)
            if isClaude:
                claudeMsg = completion.content[0].text[0:1999]
                await message.channel.send(claudeMsg)
            else:
                openaiMsg = completion.choices[0].message.content[0:1999]
                await message.channel.send(openaiMsg)
    except Exception as e:
        print(f'Error: {e}')

client.run(TOKEN)