from operator import truediv
from unicodedata import name
import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timezone, timedelta
import os

print(os.environ.get("AlarmBotToken"))

# Your bot's token
TOKEN = os.environ.get("AlarmBotToken")

intents = discord.Intents.all()
intents.members = True

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Function to update voice connect permissions for all voice channels
async def update_voice_permissions():
    await bot.wait_until_ready()

    guild = discord.utils.get(bot.guilds, name="<server name>")
    general_chat = discord.utils.get(guild.text_channels, name="general")
    smilegun = discord.utils.get(guild.emojis, name="smilegun")

    night_message_sent = False
    day_message_sent = False
    
    while not bot.is_closed():
        current_time_utc = datetime.now(timezone.utc)
        current_time_pacific = current_time_utc - timedelta(hours=7)  # Adjust for Pacific Time (UTC -7)

        # good night message
        if current_time_pacific.hour == 3 and not night_message_sent:
            night_message_sent = True
            day_message_sent = False
            await general_chat.send(f"Good night, degens! Voice Chat disabled until 8am PST {smilegun}")

        # good morning message
        if current_time_pacific.hour == 9 and not day_message_sent:
            night_message_sent = False
            day_message_sent = True
            await general_chat.send("Good morning! Voice chat has been enabled again!")

        await asyncio.sleep(60)  # Check every minute

# Event listener to remove members from voice channels during restricted time
@bot.event
async def on_voice_state_update(member, before, after):
    current_time_utc = datetime.now(timezone.utc)
    current_time_pacific = current_time_utc - timedelta(hours=7)  # Adjust for Pacific Time (UTC -7)
    
    # Check if the current time is between 3 AM and 8 AM Pacific Time
    if 3 <= current_time_pacific.hour < 8:
        if after.channel:  # Member joined a voice channel
            await member.move_to(None)  # Remove the member from the voice channel


# Start the background task
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    bot.loop.create_task(update_voice_permissions())

# Run the bot
bot.run(TOKEN)
