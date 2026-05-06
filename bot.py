import discord
from discord.ext import commands
from discord import app_commands
import os
import random

# ─── Config from environment variables (Railway) ──────────────────
TOKEN = os.environ["DISCORD_TOKEN"]

# Validate PRIDE_BANNER_URL — only use if it starts with https://
_raw_url = os.environ.get("PRIDE_BANNER_URL", "").strip()
PRIDE_BANNER_URL = _raw_url if _raw_url.startswith("https://") else ""
# ──────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Stores chosen channel per server in memory
guild_channels = {}

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


def get_channel(guild: discord.Guild):
    if guild.id in guild_channels:
        ch = guild.get_channel(guild_channels[guild.id])
        if ch:
            return ch
    for ch in guild.text_channels:
        if ch.permissions_for(guild.me).send_messages:
            return ch
    return None


# ─── Bot Ready ────────────────────────────────────────────────────
@bot.event
async def on_ready():
    await tree.sync()
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name="over the server 👀")
    )
    print(f"✅ Bot is online as {bot.user}")
    print(f"🖼️ Banner URL: {PRIDE_BANNER_URL if PRIDE_BANNER_URL else 'Not set — skipping banner'}")


# ─── /setchannel ─────────────────────────────────────────────────
@tree.command(name="setchannel", description="Choose which channel gets welcome and goodbye messages")
@app_commands.describe(channel="Pick any channel you want")
@app_commands.checks.has_permissions(administrator=True)
async def setchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_channels[interaction.guild.id] = channel.id
    embed = discord.Embed(
        title="✅ Channel Updated!",
        description=(
            f"Welcome and goodbye messages will now be sent in {channel.mention}!\n\n"
            f"You can change this anytime by running `/setchannel` again."
        ),
        color=discord.Color.green(),
    )
    await interaction.response.send_message(embed=embed)


@setchannel.error
async def setchannel_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You need **Administrator** permission.", ephemeral=True
        )


# ─── Welcome ─────────────────────────────────────────────────────
@bot.event
async def on_member_join(member: discord.Member):
    channel = get_channel(member.guild)
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
    channel = get_channel(member.guild)
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


# ─── /embed ──────────────────────────────────────────────────────
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
    elif image_url and image_url.startswith("https://"):
        embed.set_image(url=image_url)
    elif PRIDE_BANNER_URL:
        embed.set_image(url=PRIDE_BANNER_URL)
    await interaction.response.send_message(embed=embed)


@embed_command.error
async def embed_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You need **Manage Messages** permission.", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)


# ─── Run ──────────────────────────────────────────────────────────
bot.run(TOKEN)
