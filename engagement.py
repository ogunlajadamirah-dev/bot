import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import json
import asyncio
from datetime import datetime, timedelta

# ─── Config ───────────────────────────────────────────────────────
TOKEN = os.environ["DISCORD_TOKEN"]

# ─── XP & Levels ─────────────────────────────────────────────────
xp_data = {}          # { guild_id: { user_id: { xp, level, messages } } }
cooldowns = {}        # { user_id: datetime } — prevent XP spam

XP_PER_MESSAGE = 10
XP_COOLDOWN_SECONDS = 60
LEVEL_UP_XP = lambda level: 100 * (level ** 2)  # XP needed per level

# ─── Active giveaways ─────────────────────────────────────────────
active_giveaways = {}  # { message_id: { prize, end_time, channel_id, host } }

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# ─── XP Helpers ───────────────────────────────────────────────────
def get_user_data(guild_id, user_id):
    guild_id, user_id = str(guild_id), str(user_id)
    if guild_id not in xp_data:
        xp_data[guild_id] = {}
    if user_id not in xp_data[guild_id]:
        xp_data[guild_id][user_id] = {"xp": 0, "level": 1, "messages": 0}
    return xp_data[guild_id][user_id]

def get_rank(guild_id, user_id):
    guild_id, user_id = str(guild_id), str(user_id)
    if guild_id not in xp_data:
        return 1
    sorted_users = sorted(
        xp_data[guild_id].items(),
        key=lambda x: (x[1]["level"], x[1]["xp"]),
        reverse=True
    )
    for i, (uid, _) in enumerate(sorted_users):
        if uid == user_id:
            return i + 1
    return len(sorted_users) + 1


# ─── Bot Ready ────────────────────────────────────────────────────
@bot.event
async def on_ready():
    await tree.sync()
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name="the server 👀")
    )
    print(f"✅ Engagement Bot is online as {bot.user}")
    bot.loop.create_task(giveaway_checker())


# ─── XP on message ────────────────────────────────────────────────
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return

    user_id = str(message.author.id)
    now = datetime.utcnow()

    # Cooldown check
    if user_id in cooldowns and (now - cooldowns[user_id]).seconds < XP_COOLDOWN_SECONDS:
        await bot.process_commands(message)
        return

    cooldowns[user_id] = now
    data = get_user_data(message.guild.id, message.author.id)
    data["xp"] += XP_PER_MESSAGE
    data["messages"] += 1

    # Level up check
    needed = LEVEL_UP_XP(data["level"])
    if data["xp"] >= needed:
        data["level"] += 1
        data["xp"] = 0

        embed = discord.Embed(
            title="⬆️ Level Up!",
            description=f"🎉 {message.author.mention} just reached **Level {data['level']}**! Keep it up!",
            color=discord.Color.gold(),
        )
        embed.set_thumbnail(url=message.author.display_avatar.url)
        await message.channel.send(embed=embed)

    await bot.process_commands(message)


# ─── /rank ────────────────────────────────────────────────────────
@tree.command(name="rank", description="Check your level and XP rank")
@app_commands.describe(member="Check another member's rank (optional)")
async def rank(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    data = get_user_data(interaction.guild.id, target.id)
    rank_pos = get_rank(interaction.guild.id, target.id)
    needed = LEVEL_UP_XP(data["level"])
    progress = int((data["xp"] / needed) * 20)
    bar = "█" * progress + "░" * (20 - progress)

    embed = discord.Embed(
        title=f"📊 {target.display_name}'s Rank",
        color=discord.Color.from_rgb(180, 40, 20),
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="🏆 Rank", value=f"#{rank_pos}", inline=True)
    embed.add_field(name="⭐ Level", value=str(data["level"]), inline=True)
    embed.add_field(name="💬 Messages", value=str(data["messages"]), inline=True)
    embed.add_field(name=f"XP Progress {data['xp']}/{needed}", value=f"`{bar}`", inline=False)
    await interaction.response.send_message(embed=embed)


# ─── /leaderboard ─────────────────────────────────────────────────
@tree.command(name="leaderboard", description="See the top 10 most active members")
async def leaderboard(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    if guild_id not in xp_data or not xp_data[guild_id]:
        await interaction.response.send_message("No data yet! Start chatting to earn XP! 💬", ephemeral=True)
        return

    sorted_users = sorted(
        xp_data[guild_id].items(),
        key=lambda x: (x[1]["level"], x[1]["xp"]),
        reverse=True
    )[:10]

    medals = ["🥇", "🥈", "🥉"]
    embed = discord.Embed(
        title="🏆 Server Leaderboard",
        description="Top 10 most active members!",
        color=discord.Color.gold(),
    )

    for i, (user_id, data) in enumerate(sorted_users):
        member = interaction.guild.get_member(int(user_id))
        name = member.display_name if member else f"User {user_id}"
        medal = medals[i] if i < 3 else f"`#{i+1}`"
        embed.add_field(
            name=f"{medal} {name}",
            value=f"Level **{data['level']}** • {data['xp']} XP • {data['messages']} messages",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


# ─── /poll ────────────────────────────────────────────────────────
@tree.command(name="poll", description="Create a poll for members to vote on")
@app_commands.describe(
    question="The poll question",
    option1="First option",
    option2="Second option",
    option3="Third option (optional)",
    option4="Fourth option (optional)",
)
@app_commands.checks.has_permissions(manage_messages=True)
async def poll(
    interaction: discord.Interaction,
    question: str,
    option1: str,
    option2: str,
    option3: str = None,
    option4: str = None,
):
    options = [option1, option2]
    if option3:
        options.append(option3)
    if option4:
        options.append(option4)

    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
    description = "\n\n".join([f"{emojis[i]} {opt}" for i, opt in enumerate(options)])

    embed = discord.Embed(
        title=f"📊 {question}",
        description=description,
        color=discord.Color.blue(),
    )
    embed.set_footer(text=f"Poll by {interaction.user.display_name} • React to vote!")

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    for i in range(len(options)):
        await msg.add_reaction(emojis[i])


# ─── /giveaway ────────────────────────────────────────────────────
@tree.command(name="giveaway", description="Start a giveaway!")
@app_commands.describe(
    prize="What are you giving away?",
    minutes="How many minutes should the giveaway last?",
)
@app_commands.checks.has_permissions(manage_messages=True)
async def giveaway(interaction: discord.Interaction, prize: str, minutes: int):
    end_time = datetime.utcnow() + timedelta(minutes=minutes)

    embed = discord.Embed(
        title="🎉 GIVEAWAY!",
        description=(
            f"**Prize:** {prize}\n\n"
            f"React with 🎉 to enter!\n\n"
            f"⏰ Ends in **{minutes} minute(s)**"
        ),
        color=discord.Color.gold(),
    )
    embed.set_footer(text=f"Hosted by {interaction.user.display_name} • Ends at {end_time.strftime('%H:%M UTC')}")

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()
    await msg.add_reaction("🎉")

    active_giveaways[msg.id] = {
        "prize": prize,
        "end_time": end_time,
        "channel_id": interaction.channel.id,
        "host": interaction.user.display_name,
        "message_id": msg.id,
    }


# ─── Giveaway checker loop ─────────────────────────────────────────
async def giveaway_checker():
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.utcnow()
        ended = [mid for mid, g in active_giveaways.items() if now >= g["end_time"]]

        for msg_id in ended:
            g = active_giveaways.pop(msg_id)
            channel = bot.get_channel(g["channel_id"])
            if not channel:
                continue
            try:
                msg = await channel.fetch_message(msg_id)
                reaction = discord.utils.get(msg.reactions, emoji="🎉")
                users = [u async for u in reaction.users() if not u.bot] if reaction else []

                if not users:
                    embed = discord.Embed(
                        title="🎉 Giveaway Ended",
                        description=f"No one entered the giveaway for **{g['prize']}**!",
                        color=discord.Color.red(),
                    )
                else:
                    winner = random.choice(users)
                    embed = discord.Embed(
                        title="🎉 Giveaway Ended!",
                        description=(
                            f"**Prize:** {g['prize']}\n\n"
                            f"🏆 Winner: {winner.mention}\n\n"
                            f"Congratulations! 🎊"
                        ),
                        color=discord.Color.gold(),
                    )
                await channel.send(embed=embed)
            except Exception as e:
                print(f"Giveaway error: {e}")

        await asyncio.sleep(15)


# ─── /trivia ──────────────────────────────────────────────────────
TRIVIA = [
    {"q": "What anime is Levi Ackerman from?", "a": "attack on titan", "opts": ["Naruto", "Attack on Titan", "Bleach", "One Piece"]},
    {"q": "What is the best-selling video game of all time?", "a": "minecraft", "opts": ["Minecraft", "GTA V", "Tetris", "Fortnite"]},
    {"q": "Which artist released 'Thriller'?", "a": "michael jackson", "opts": ["Michael Jackson", "Prince", "Madonna", "David Bowie"]},
    {"q": "What novel features a whale named Moby Dick?", "a": "moby-dick", "opts": ["Moby-Dick", "The Old Man and the Sea", "20,000 Leagues", "Jaws"]},
    {"q": "In what game do you build with blocks and fight creepers?", "a": "minecraft", "opts": ["Roblox", "Terraria", "Minecraft", "Fortnite"]},
    {"q": "Who wrote the manga Naruto?", "a": "masashi kishimoto", "opts": ["Masashi Kishimoto", "Eiichiro Oda", "Akira Toriyama", "Hajime Isayama"]},
    {"q": "What is the name of the One Piece main character?", "a": "monkey d. luffy", "opts": ["Zoro", "Nami", "Monkey D. Luffy", "Sanji"]},
    {"q": "What genre is the game 'Dark Souls'?", "a": "action rpg", "opts": ["FPS", "Action RPG", "Strategy", "Simulation"]},
]

active_trivia = {}  # channel_id: { question, answer, asker }

@tree.command(name="trivia", description="Start a trivia question for the server!")
async def trivia(interaction: discord.Interaction):
    if interaction.channel.id in active_trivia:
        await interaction.response.send_message("⚠️ A trivia is already active in this channel!", ephemeral=True)
        return

    q = random.choice(TRIVIA)
    active_trivia[interaction.channel.id] = {"answer": q["a"], "asker": interaction.user.display_name}

    random.shuffle(q["opts"])
    emojis = ["🅰️", "🅱️", "🆑", "🆘"]
    opts_text = "\n".join([f"{emojis[i]} {opt}" for i, opt in enumerate(q["opts"])])

    embed = discord.Embed(
        title="🧠 Trivia Time!",
        description=f"**{q['q']}**\n\n{opts_text}\n\nType your answer in chat!",
        color=discord.Color.purple(),
    )
    embed.set_footer(text=f"Started by {interaction.user.display_name} • First correct answer wins!")
    await interaction.response.send_message(embed=embed)

    # Auto end trivia after 30 seconds
    await asyncio.sleep(30)
    if interaction.channel.id in active_trivia:
        active_trivia.pop(interaction.channel.id)
        await interaction.channel.send(f"⏰ Time's up! The answer was **{q['a'].title()}**!")


@bot.event
async def on_message_trivia(message: discord.Message):
    if message.author.bot or not message.guild:
        return
    if message.channel.id in active_trivia:
        ans = active_trivia[message.channel.id]["answer"]
        if ans.lower() in message.content.lower():
            active_trivia.pop(message.channel.id)
            embed = discord.Embed(
                title="✅ Correct!",
                description=f"🎉 {message.author.mention} got it right! The answer was **{ans.title()}**!\n\n+50 Bonus XP!",
                color=discord.Color.green(),
            )
            # Bonus XP for trivia
            data = get_user_data(message.guild.id, message.author.id)
            data["xp"] += 50
            await message.channel.send(embed=embed)


# Override on_message to also check trivia
original_on_message = bot.on_message

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return

    # Trivia check
    if message.channel.id in active_trivia:
        ans = active_trivia[message.channel.id]["answer"]
        if ans.lower() in message.content.lower():
            active_trivia.pop(message.channel.id)
            embed = discord.Embed(
                title="✅ Correct!",
                description=f"🎉 {message.author.mention} got it right! The answer was **{ans.title()}**!\n\n+50 Bonus XP! 🌟",
                color=discord.Color.green(),
            )
            data = get_user_data(message.guild.id, message.author.id)
            data["xp"] += 50
            await message.channel.send(embed=embed)

    # XP system
    user_id = str(message.author.id)
    now = datetime.utcnow()
    if not (user_id in cooldowns and (now - cooldowns[user_id]).seconds < XP_COOLDOWN_SECONDS):
        cooldowns[user_id] = now
        data = get_user_data(message.guild.id, message.author.id)
        data["xp"] += XP_PER_MESSAGE
        data["messages"] += 1
        needed = LEVEL_UP_XP(data["level"])
        if data["xp"] >= needed:
            data["level"] += 1
            data["xp"] = 0
            embed = discord.Embed(
                title="⬆️ Level Up!",
                description=f"🎉 {message.author.mention} just reached **Level {data['level']}**!",
                color=discord.Color.gold(),
            )
            embed.set_thumbnail(url=message.author.display_avatar.url)
            await message.channel.send(embed=embed)

    await bot.process_commands(message)


# ─── /coinflip ────────────────────────────────────────────────────
@tree.command(name="coinflip", description="Flip a coin!")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["Heads 🪙", "Tails 🪙"])
    embed = discord.Embed(
        title="🪙 Coin Flip!",
        description=f"{interaction.user.mention} flipped a coin and got... **{result}**!",
        color=discord.Color.gold(),
    )
    await interaction.response.send_message(embed=embed)


# ─── /roll ────────────────────────────────────────────────────────
@tree.command(name="roll", description="Roll a dice!")
@app_commands.describe(sides="Number of sides (default: 6)")
async def roll(interaction: discord.Interaction, sides: int = 6):
    result = random.randint(1, sides)
    embed = discord.Embed(
        title="🎲 Dice Roll!",
        description=f"{interaction.user.mention} rolled a **{sides}-sided dice** and got... **{result}**!",
        color=discord.Color.blue(),
    )
    await interaction.response.send_message(embed=embed)


# ─── /8ball ───────────────────────────────────────────────────────
EIGHTBALL_RESPONSES = [
    "✅ It is certain.", "✅ Without a doubt.", "✅ Yes, definitely!",
    "✅ You may rely on it.", "🤔 Ask again later.", "🤔 Cannot predict now.",
    "❌ Don't count on it.", "❌ My sources say no.", "❌ Very doubtful.",
]

@tree.command(name="8ball", description="Ask the magic 8ball a question")
@app_commands.describe(question="Your question")
async def eightball(interaction: discord.Interaction, question: str):
    embed = discord.Embed(
        title="🎱 Magic 8Ball",
        color=discord.Color.dark_purple(),
    )
    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name="Answer", value=random.choice(EIGHTBALL_RESPONSES), inline=False)
    embed.set_footer(text=f"Asked by {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)


# ─── /serverinfo ──────────────────────────────────────────────────
@tree.command(name="serverinfo", description="See info about this server")
async def serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    embed = discord.Embed(title=f"📊 {g.name}", color=discord.Color.from_rgb(180, 40, 20))
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
    embed.add_field(name="👑 Owner", value=g.owner.mention if g.owner else "Unknown", inline=True)
    embed.add_field(name="👥 Members", value=str(g.member_count), inline=True)
    embed.add_field(name="💬 Channels", value=str(len(g.text_channels)), inline=True)
    embed.add_field(name="🎭 Roles", value=str(len(g.roles)), inline=True)
    embed.add_field(name="📅 Created", value=discord.utils.format_dt(g.created_at, "R"), inline=True)
    await interaction.response.send_message(embed=embed)


# ─── /userinfo ────────────────────────────────────────────────────
@tree.command(name="userinfo", description="See info about a member")
@app_commands.describe(member="The member to look up (optional)")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    embed = discord.Embed(title=f"👤 {target.display_name}", color=discord.Color.blue())
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="🏷️ Username", value=str(target), inline=True)
    embed.add_field(name="🆔 ID", value=str(target.id), inline=True)
    embed.add_field(name="📅 Joined Server", value=discord.utils.format_dt(target.joined_at, "R") if target.joined_at else "Unknown", inline=True)
    embed.add_field(name="🎂 Account Created", value=discord.utils.format_dt(target.created_at, "R"), inline=True)
    embed.add_field(name="🎭 Top Role", value=target.top_role.mention, inline=True)
    await interaction.response.send_message(embed=embed)


# ─── Run ──────────────────────────────────────────────────────────
bot.run(TOKEN)
