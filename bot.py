import os
import json
import discord
import locale
import anthropic
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
xai_key = os.getenv("XAI_KEY")
xai_client = OpenAI(base_url="https://api.x.ai/v1", api_key=xai_key)
openai_client = OpenAI(api_key=openai_api_key)
claude_api_key = os.getenv("CLAUDE_API_KEY")
claude_client = anthropic.Anthropic(api_key=claude_api_key)

TOKEN = os.getenv("TOKEN")
agent = "claude"
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
locale.setlocale(locale.LC_ALL, "")

dictionary_str = os.getenv("DICTIONARY")
if dictionary_str is None:
    raise ValueError("No dictionary found!")
dictionary = json.loads(dictionary_str)


def getSystemPrompt(message):
    prompt_template = os.getenv("SYSTEM_PROMPT")
    if not prompt_template:
        raise ValueError("SYSTEM_PROMPT not found in environment variables")
    return prompt_template.format(
        user_mention=client.user.mention,
        author_mention=message.author.mention,
        agent=agent,
        dictionary=dictionary,
    )


async def sendMsgs(text, message):
    numMsgs = len(text) // 2000
    for i in range(numMsgs):
        await message.channel.send(text[i * 2000 : (i + 1) * 2000])
    await message.channel.send(text[numMsgs * 2000 :])


async def sendMessage(message):
    global agent

    isClaude = agent == "claude"
    isOpenAI = agent == "o3"

    completion = await makeCompletion(message, isClaude, isOpenAI)

    if isClaude:
        text = completion.content[0].text
        await sendMsgs(text, message)
    else:
        text = completion.choices[0].message.content
        await sendMsgs(text, message)


def makeClaudeCompletion(AGENT_PROMPT_TEXT, SYSTEM_PROMPT_TEXT, formatted_history):
    CLAUDE_MODEL = "claude-sonnet-4-20250514"
    CLAUDE_SYSTEM_PROMPT = [
        {"type": "text", "text": SYSTEM_PROMPT_TEXT},
        {
            "type": "text",
            "text": f"History: {formatted_history}",
            "cache_control": {"type": "ephemeral"},
        },
    ]
    claude_completion = claude_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1000,
        system=CLAUDE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": AGENT_PROMPT_TEXT}],
    )
    return claude_completion


def makeOpenAICompletion(AGENT_PROMPT_TEXT, SYSTEM_PROMPT_TEXT, formatted_history):
    openai_completion = openai_client.chat.completions.create(
        model="o3-mini",
        max_completion_tokens=1000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_TEXT},
            {"role": "system", "content": f"History: {formatted_history}"},
            {"role": "user", "content": AGENT_PROMPT_TEXT},
        ],
    )
    return openai_completion


def makeXAICompletion(AGENT_PROMPT_TEXT, SYSTEM_PROMPT_TEXT, formatted_history):
    xai_completion = xai_client.chat.completions.create(
        model="grok-4-latest",  # or "grok-3-mini-fast"
        reasoning_effort="high",
        max_tokens=1000,
        messages=[
            {"role": "user", "content": AGENT_PROMPT_TEXT},
            {"role": "system", "content": SYSTEM_PROMPT_TEXT},
            {"role": "system", "content": f"History: {formatted_history}"},
        ],
        temperature=0.7,
    )
    return xai_completion


async def makeCompletion(message, isClaude, isOpenAI):
    message_history = [msg async for msg in message.channel.history(limit=20)]
    # Format history as a string to include in the system prompt
    formatted_history = "\n".join(
        [
            f"{msg.created_at} {msg.author.name}: {msg.content}"
            for msg in message_history[::-1]
        ]
    )
    AGENT_PROMPT_TEXT = f"Latest message: {message.created_at} {message.author.name}: {message.content}\n"
    SYSTEM_PROMPT_TEXT = getSystemPrompt(message)

    if isClaude:
        return makeClaudeCompletion(
            AGENT_PROMPT_TEXT, SYSTEM_PROMPT_TEXT, formatted_history
        )
    elif isOpenAI:
        return makeOpenAICompletion(
            AGENT_PROMPT_TEXT, SYSTEM_PROMPT_TEXT, formatted_history
        )
    else:
        return makeXAICompletion(
            AGENT_PROMPT_TEXT, SYSTEM_PROMPT_TEXT, formatted_history
        )


def updateAgent(msg_text):
    global agent

    claude_request = "-claude" in msg_text
    o3_request = "-o3" in msg_text

    if claude_request:
        agent = "claude"
    elif o3_request:
        agent = "o3"
    else:
        agent = "grok"


@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")


@client.event
async def on_message(message):
    try:
        print(message.content)
        if message.author == client.user:
            return
        is_dm = isinstance(message.channel, discord.DMChannel)
        msg_text = message.content.lower()
        is_bot_mention = "aibot" in msg_text or client.user.mention in msg_text
        is_agent_update_request = (
            "-grok" in msg_text or "-claude" in msg_text or "-o3" in msg_text
        )
        if is_agent_update_request:
            updateAgent(msg_text)
        if is_dm or is_bot_mention:
            await sendMessage(message)
    except Exception as e:
        print(f"Error: {e}")


client.run(TOKEN)
