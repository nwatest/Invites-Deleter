import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import pytz
import requests
from keep_alive import keep_alive

load_dotenv()
TOKEN = os.getenv('TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

whitelisted = 1239966321387769866

intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="Deleting Invites!"))

@bot.command()
async def delete(ctx, uses: int, hours: int):
    if ctx.author.id == whitelisted:
        if uses == 0 and hours >= 1:
            now = datetime.utcnow().replace(tzinfo=pytz.UTC)
            threshold = now - timedelta(hours=hours)
            invites = await ctx.guild.invites()
            deleted_invites = 0

            for invite in invites:
                if invite.uses == 0 and invite.created_at < threshold:
                    invite_age_hours = (now - invite.created_at).total_seconds() / 3600
                    log_message = f"Deleted invite {invite.code} created {invite_age_hours:.2f} hours ago."
                    requests.post(WEBHOOK_URL, json={"content": log_message})
                    await invite.delete()
                    deleted_invites += 1

            await ctx.reply(f"Deleted {deleted_invites} invites with 0 uses that were more than {hours} hours old.")
        else:
            await ctx.reply("Invalid parameters. Uses must be 0 and hours must be at least 1.")
    else:
        await ctx.reply("❌")

keep_alive()
bot.run(TOKEN)
