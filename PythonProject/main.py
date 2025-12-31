import discord
from discord.ext import commands
import logging
import asyncio
from dotenv import load_dotenv
import os
from openai import OpenAI

# =========================
# ENV / SETUP
# =========================
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# =========================
# EVENTS
# =========================

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_member_join(member):
    await asyncio.sleep(1)  # wait 1 second
    try:
        embed = discord.Embed(
            title="Welcome!",
            description=f"Welcome to the server, {member.name}!",
            color=discord.Color.green()
        )
        await member.send(embed=embed)
    except Exception:
        pass  # ignore errors if DMs are blocked

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "elijah" in message.content.lower():
        await message.delete()
        embed = discord.Embed(
            description=f"{message.author.mention}, you shouldn't say that name!",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)

    await bot.process_commands(message)

# =========================
# COMMANDS
# =========================

@bot.command()
async def hello(ctx):
    embed = discord.Embed(
        description=f"Hello, {ctx.author.mention}!",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def scale(ctx, *, args):
    """
    Usage: !scale CharacterA vs CharacterB
    Simplified output: just key stats and winner.
    """
    if " vs " not in args.lower():
        embed = discord.Embed(
            description="Usage: `!scale CharacterA vs CharacterB`",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return

    name_a, name_b = map(str.strip, args.split("vs"))
    embed = discord.Embed(
        title="Power Scaling",
        description=f"Scaling **{name_a}** vs **{name_b}**...",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

    # Simplified prompt for clean, short output
    prompt = f"""
You are comparing two fictional characters for a VS-style power scale. 
Keep your answer concise and structured. 

Character A: {name_a}
Character B: {name_b}

Provide ONLY:
- Strength
- Speed
- Durability
- Abilities
- Battle Intelligence
- Winner

Format like this:

Character A (Example - Luffy):
Strength: ...
Speed: ...
Durability: ...
Abilities: ...
Battle Intelligence: ...

Character B (Example - Goku):
Strength: ...
Speed: ...
Durability: ...
Abilities: ...
Battle Intelligence: ...

Winner: Character X (Example - Luffy)
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        result = response.choices[0].message.content

        # Use embed for scaling result
        result_embed = discord.Embed(
            title=f"{name_a} vs {name_b} Result",
            description=f"```{result[:2000]}```",
            color=discord.Color.gold()
        )
        await ctx.send(embed=result_embed)
    except Exception as e:
        error_embed = discord.Embed(
            description=f"An error occurred while scaling: {e}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

# =========================
# RUN BOT
# =========================

bot.run(DISCORD_TOKEN, log_handler=handler, log_level=logging.DEBUG)

