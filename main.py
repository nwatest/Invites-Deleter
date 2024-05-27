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

whitelisted = [1239966321387769866,
               1238325036604067934]

intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.guilds = True
intents.invites = True  # Enable invites intent

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="Managing Invites"))

@bot.command()
async def delete(ctx, max_uses: int, hours: int):
    if ctx.author.id in whitelisted:  # Check if author's ID is in the whitelisted IDs
        if max_uses >= 0 and hours >= 1:
            now = datetime.utcnow().replace(tzinfo=pytz.UTC)
            threshold = now - timedelta(hours=hours)
            invites = await ctx.guild.invites()
            deleted_invites = 0

            for invite in invites:
                invite_created_at = invite.created_at.replace(tzinfo=pytz.UTC)
                if invite.max_uses is not None and invite.max_uses <= max_uses and invite_created_at < threshold:
                    invite_age_hours = (now - invite_created_at).total_seconds() / 3600
                    log_message = f"Deleted invite {invite.code} (uses: {invite.uses}) created {invite_age_hours:.2f} hours ago."
                    requests.post(WEBHOOK_URL, json={"content": log_message})
                    await invite.delete()
                    deleted_invites += 1

            await ctx.reply(f"Deleted {deleted_invites} invites with {max_uses} uses or less that were more than {hours} hours old.")
        else:
            await ctx.reply("Invalid parameters. Max uses must be a non-negative integer and hours must be at least 1.")
    else:
        await ctx.reply("❌")

@bot.command()
async def count(ctx):
    invites = await ctx.guild.invites()
    active_invites = [invite for invite in invites if invite.uses < invite.max_uses or invite.max_uses == 0]
    await ctx.reply(f"There are {len(active_invites)} active invites in this server.")

keep_alive()
bot.run(TOKEN)
