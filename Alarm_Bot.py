"""
Alarm Bot is a bot that acts as an alarm
but rather than as an alarm for when to wake up
it acts as an alarm for when to go to sleep.
"""

import asyncio
from datetime import datetime, timezone, timedelta
import json
import os

import discord
from discord.ext import commands

TOKEN = os.environ.get("AlarmBotToken")

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

"""
Example Overrides.txt format:
Don't let member with id "1234567890" join voice chat
on Monday between 9am and 5pm Pacific Time
(because they should be working :upsidedown-smile:)
{
    "1234567890":
    {
        "weekday": 1,
        "hour_start": 9,
        "hour_end": 17
    }
}
"""
async def load_overrides():
    """
    Loads an overrides file, which contains rules
    that will work in addition to the default of "no voice from 3am to 8am"
    """
    with open("Overrides.txt", "r", encoding="UTF-8") as overrides_file:
        return json.load(overrides_file)

async def maybe_kick_member_from_voice(member: discord.Member):
    """
    Common function for usage in both 'run_loop()' and 'on_voice_state_update'
    so that both functions respect the overrides file
    """
    current_time_utc = datetime.now(timezone.utc)
    current_time_pacific = current_time_utc - timedelta(hours=7)
    current_weekday = current_time_pacific.weekday()
    current_hour = current_time_pacific.hour
    overrides = await load_overrides()

    member_id = str(member.id)
    # No overrides present, follow the default rule
    member_override = overrides[member_id]
    if member_override is None or len(member_override) == 0:
        if 3 <= current_hour <= 8:
            await member.move_to(None)
    else:
        weekday_override = member_override.get("weekday")
        hour_start_override = member_override.get("hour_start")
        hour_end_override = member_override.get("hour_end")
        if weekday_override is not None and hour_start_override is not None:
            if current_weekday == weekday_override and current_hour == hour_start_override:
                await member.move_to(None)
        elif weekday_override is not None and hour_start_override is None:
            if current_weekday == weekday_override:
                await member.move_to(None)
        elif weekday_override is None and hour_start_override is not None:
            if hour_start_override <= current_hour < hour_end_override:
                await member.move_to(None)

async def run_loop():
    """ Main run loop of the bot """
    await bot.wait_until_ready()
    guild = discord.utils.get(bot.guilds, name=os.environ.get("ServerName"))

    while not bot.is_closed():
        for channel in guild.voice_channels:
            for member in channel.members:
                await maybe_kick_member_from_voice(member)
                await asyncio.sleep(60)

@bot.event
async def on_voice_state_update(member: discord.Member,
                                _: discord.VoiceState,
                                after: discord.VoiceState):
    """
    Function that runs each time a user joins a voice channel
    Auto-kicks the user if the current time is between 3am and 8am Pacific Time
    """

    if after.channel is None:
        return

    await maybe_kick_member_from_voice(member)

@bot.event
async def on_ready():
    """ Function that's called when the bot is ready """
    print(f'Logged in as {bot.user.name}')
    bot.loop.create_task(run_loop())

bot.run(TOKEN)
