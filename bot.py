# Example: reuse your existing OpenAI setup
import os
from openai import OpenAI
import discord
import locale

from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv('OPENAI_TOKEN')
openai_client = OpenAI(
    api_key=openai_api_key
)

TOKEN = os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    print(message.content)
    if message.author == client.user:
        return
    if 'aibot' in message.content.lower() or client.user.mention in message.content.lower():
        completion = openai_client.chat.completions.create(
          model="gpt-4-1106-preview",
          messages=[
              {"role": "user",
               "content": f"""Your name is AIBot or {client.user.mention}.

               Respond to the following statement in at most 2000 characters: {message.content}
               
               If you want to mention the person who referenced you, refer to them as {message.author.mention}
               """
               }
          ]
        )
        await message.channel.send(completion.choices[0].message.content[0:1999])

client.run(TOKEN)