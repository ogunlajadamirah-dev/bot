import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import json

# ─── Config from environment variables (Railway) ──────────────────
TOKEN = os.environ["DISCORD_TOKEN"]
PRIDE_BANNER_URL = os.environ.get("PRIDE_BANNER_URL", "")
# ──────────────────────────────────────────────────────────────────

# Saves each server's chosen channel to a file
SETTINGS_FILE = "settings.json"

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)

def get_channel_id(guild_id: int):
    settings = load_settings()
    return settings.get(str(guild_id))

def set_channel_id(guild_id: int, channel_id: int):
    settings = load_settings()
    settings[str(guild_id)] = channel_id
    save_settings(settings)


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ─── Fun message pools ────────────────────────────────────────────
WELCOME_MESSAGES = [
    "just dropped in like a shooting star 🌟",
    "has entered the chat — and honestly? We're better for it 🎉",
    "arrived and the vibe instantly improved ✨",
    "showed up and the server said: *finally* 🥳",
    "joined and we hit a new record of awesomeness 🔥",
    "pulled up — welcome to the family! 🫂",
    "just unlocked: **being part of something cool** 🏆",
]

GOODBYE_MESSAGES = [
    "We'll keep the lights on for you 🕯️",
    "The server won't be the same without you 💙",
    "Left but never forgotten. Legends don't really leave 👑",
    "Gone but the memories remain ✨",
    "The door is always open if you come back 🚪",
    "We'll miss you more than we'll admit 🥹",
    "Fly safe, legend 🕊️",
]

WELCOME_TIPS = [
    "📌 Check out **#rules** before anything else!",
    "🎯 Introduce yourself — we love new faces!",
    "🎮 Hop into a voice channel, don't be shy!",
    "🔔 Set your notifications so you don't miss the good stuff.",
    "💬 Best way to fit in? Just start chatting!",
]


# ─── Bot Ready ────────────────────────────────────────────────────
@bot.event
async def on_ready():
    await tree.sync()
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name="over the server 👀")
    )
    print(f"✅ Bot is online as {bot.user}")


# ─── Bot joins a new server ───────────────────────────────────────
@bot.event
async def on_guild_join(guild: discord.Guild):
    # Find first channel it can talk in and tell admin to set the channel
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(
                title="👋 Hey! I just joined!",
                description=(
                    "Thanks for adding me! 🎉\n\n"
                    "To set up welcome & goodbye messages, an admin needs to run:\n\n"
                    "**`/setchannel #your-channel-name`**\n\n"
                    "Just pick any channel you want and I'll send all messages there!"
                ),
                color=discord.Color.from_rgb(180, 40, 20),
            )
            await channel.send(embed=embed)
            break


# ─── /setchannel command ──────────────────────────────────────────
@tree.command(name="setchannel", description="Set the channel for welcome and goodbye messages")
@app_commands.describe(channel="Pick the channel you want welcome/goodbye messages in")
@app_commands.checks.has_permissions(administrator=True)
async def setchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    set_channel_id(interaction.guild.id, channel.id)
    embed = discord.Embed(
        title="✅ Channel Set!",
        description=f"Welcome and goodbye messages will now be sent in {channel.mention}!",
        color=discord.Color.green(),
    )
    await interaction.response.send_message(embed=embed)


@setchannel.error
async def setchannel_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You need **Administrator** permission to use this.", ephemeral=True
        )


# ─── Welcome ─────────────────────────────────────────────────────
@bot.event
async def on_member_join(member: discord.Member):
    channel_id = get_channel_id(member.guild.id)
    if not channel_id:
        return
    channel = bot.get_channel(channel_id)
    if not channel:
        return

    embed = discord.Embed(
        title=f"🎉 Welcome to {member.guild.name}!",
        description=(
            f"Hey {member.mention}, you {random.choice(WELCOME_MESSAGES)}\n\n"
            f"**Tip:** {random.choice(WELCOME_TIPS)}"
        ),
        color=discord.Color.from_rgb(180, 40, 20),
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    if PRIDE_BANNER_URL:
        embed.set_image(url=PRIDE_BANNER_URL)
    embed.add_field(name="👤 Account Age", value=discord.utils.format_dt(member.created_at, "R"), inline=True)
    embed.add_field(name="🧑‍🤝‍🧑 Member #", value=str(member.guild.member_count), inline=True)
    embed.set_footer(text=f"ID: {member.id} • Glad you're here!", icon_url=member.display_avatar.url)
    await channel.send(embed=embed)


# ─── Goodbye ─────────────────────────────────────────────────────
@bot.event
async def on_member_remove(member: discord.Member):
    channel_id = get_channel_id(member.guild.id)
    if not channel_id:
        return
    channel = bot.get_channel(channel_id)
    if not channel:
        return

    embed = discord.Embed(
        title=f"👋 {member.display_name} has left",
        description=(
            f"{member.mention} just left **{member.guild.name}**.\n"
            f"{random.choice(GOODBYE_MESSAGES)}"
        ),
        color=discord.Color.from_rgb(30, 30, 30),
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    if PRIDE_BANNER_URL:
        embed.set_image(url=PRIDE_BANNER_URL)
    embed.add_field(name="📅 Was here since", value=discord.utils.format_dt(member.joined_at, "R") if member.joined_at else "Unknown", inline=True)
    embed.add_field(name="🧑‍🤝‍🧑 Members remaining", value=str(member.guild.member_count), inline=True)
    embed.set_footer(text=f"ID: {member.id} • We'll miss you!", icon_url=member.display_avatar.url)
    await channel.send(embed=embed)


# ─── /embed slash command ─────────────────────────────────────────
@tree.command(name="embed", description="Send a custom embed message")
@app_commands.describe(
    title="Title of the embed",
    description="Body text of the embed",
    color="Color: red, green, blue, gold, purple (default: blue)",
    image="Upload an image file directly (optional)",
    image_url="Or paste an image URL instead (optional)",
)
@app_commands.checks.has_permissions(manage_messages=True)
async def embed_command(
    interaction: discord.Interaction,
    title: str,
    description: str,
    color: str = "blue",
    image: discord.Attachment = None,
    image_url: str = None,
):
    color_map = {
        "red":    discord.Color.red(),
        "green":  discord.Color.green(),
        "blue":   discord.Color.blue(),
        "gold":   discord.Color.gold(),
        "purple": discord.Color.purple(),
    }
    embed = discord.Embed(
        title=title,
        description=description,
        color=color_map.get(color.lower(), discord.Color.blue()),
    )
    embed.set_footer(text=f"Sent by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    if image:
        embed.set_image(url=image.url)
    elif image_url:
        embed.set_image(url=image_url)
    elif PRIDE_BANNER_URL:
        embed.set_image(url=PRIDE_BANNER_URL)

    await interaction.response.send_message(embed=embed)


@embed_command.error
async def embed_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You need **Manage Messages** permission to use this.", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)


# ─── Run ──────────────────────────────────────────────────────────
bot.run(TOKEN)
