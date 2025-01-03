# Example: reuse your existing OpenAI setup
import os
import discord
import locale
import anthropic
from dotenv import load_dotenv

load_dotenv()

claude_api_key = os.getenv("CLAUDE_API_KEY")
claude_client = anthropic.Anthropic(
    api_key=claude_api_key
)

TOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
locale.setlocale(locale.LC_ALL, '')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    print(message.content)
    if message.author == client.user:
        return
    if 'aibot' in message.content.lower() or client.user.mention in message.content.lower():
        message_history = [
            msg async for msg in message.channel.history(limit=10)
        ]
        # Format history as a string to include in the system prompt
        formatted_history = "\n".join(
            [f"{msg.author.name}: {msg.content}" for msg in message_history[::-1]]
        )
        completion = claude_client.messages.create(
          model="claude-3-5-sonnet-20241022",
          max_tokens=1024,
          system=f"""Pretend your name is AIBot or {client.user.mention}.
               If you want to mention the person who referenced you, refer to them as {message.author.mention}.
               Here is the formatted message history for context: {formatted_history}
               """,
          messages=[
               {
                   "role": "user",
                   "content": f"""Respond to the following statement in at most 2000 characters: {message.content}"""
               }
          ]
        )
        await message.channel.send(completion.content[0].text[0:1999])

client.run(TOKEN)