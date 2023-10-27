"""
Alarm Bot is a bot that acts as an alarm
but rather than as an alarm for when to wake up
it acts as an alarm for when to go to sleep.
"""

import asyncio
from datetime import datetime, timezone, timedelta
import os

import discord
from discord.ext import commands

print(os.environ.get("AlarmBotToken"))

# Your bot's token
TOKEN = os.environ.get("AlarmBotToken")

intents = discord.Intents.all()
intents.members = True

# Create a bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Function to update voice connect permissions for all voice channels
async def run_loop():
    """ Main run loop of the bot """
    await bot.wait_until_ready()

    guild = discord.utils.get(bot.guilds, name=os.environ.get("ServerName"))

    while not bot.is_closed():
        current_time_utc = datetime.now(timezone.utc)
        current_time_pacific = current_time_utc - timedelta(hours=7)

        if current_time_pacific.hour < 3 or current_time_pacific.hour > 8:
            await asyncio.sleep(60)  # Check every minute
            continue

        for channel in guild.voice_channels:
            for member in channel.members:
                await member.move_to(None)

        await asyncio.sleep(60)  # Check every minute

# Event listener to remove members from voice channels during restricted time
@bot.event
async def on_voice_state_update(member: discord.Member,
                                _: discord.VoiceState,
                                after: discord.VoiceState):
    """
    Function that runs each time a user joins a voice channel
    Auto-kicks the user if the current time is between 3am and 8am Pacific Time
    """

    if not after.channel:
        return

    current_time_utc = datetime.now(timezone.utc)
    current_time_pacific = current_time_utc - timedelta(hours=7)

    # Check if the current time is between 3 AM and 8 AM Pacific Time
    if 3 <= current_time_pacific.hour < 8:
        await member.move_to(None)  # Remove the member from the voice channel

# Start the background task
@bot.event
async def on_ready():
    """ Function that's called when the bot is ready """
    print(f'Logged in as {bot.user.name}')
    bot.loop.create_task(run_loop())

# Run the bot
bot.run(TOKEN)