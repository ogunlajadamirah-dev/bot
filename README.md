# 🤖 Friend Server Bot

A Discord bot for your friend's server with welcome & goodbye in **one shared channel**, fun random messages, and a `/embed` command. Hosted free on Railway.

---

## 📁 Files

```
friendbot/
├── bot.py            ← Main bot code
├── requirements.txt  ← Python dependencies
├── Procfile          ← Tells Railway how to start the bot
├── railway.toml      ← Railway config
└── README.md         ← This file
```

---

## 🔧 Step 1 — Create your Discord Bot

1. Go to https://discord.com/developers/applications
2. Click **New Application** → give it a name
3. Go to the **Bot** tab → click **Add Bot**
4. Under **Privileged Gateway Intents**, enable:
   - ✅ **Server Members Intent**
5. Click **Reset Token** → copy your token (keep it secret!)
6. Go to **OAuth2 → URL Generator**:
   - Scopes: `bot` + `applications.commands`
   - Bot Permissions: `Send Messages`, `Embed Links`, `Manage Messages`
7. Copy the generated URL → open it → invite the bot to your friend's server

---

## 📢 Step 2 — Get your channel ID

1. In Discord, go to **Settings → Advanced → Enable Developer Mode**
2. Right-click the channel you want (the ONE channel for welcome + goodbye)
3. Click **Copy Channel ID**

---

## 🚂 Step 3 — Deploy on Railway (free)

1. Push these files to a **GitHub repo** (can be private)
2. Go to https://railway.app → sign in with GitHub
3. Click **New Project → Deploy from GitHub repo** → select your repo
4. Go to your project → **Variables** tab → add these:

| Variable name      | Value                        |
|--------------------|------------------------------|
| `DISCORD_TOKEN`    | Your bot token from Step 1   |
| `MEMBER_CHANNEL_ID`| Your channel ID from Step 2  |

5. Railway will automatically deploy and start the bot 🎉

---

## ✅ Features

| Feature | Details |
|---|---|
| 🎉 Welcome embed | Sent to your member channel when someone joins |
| 👋 Goodbye embed | Sent to the **same** channel when someone leaves |
| 🎲 Random messages | Fun unique messages every time — never repetitive |
| 💡 Random tips | Each welcome shows a random tip for new members |
| 📊 Member count | Shows account age and server member count |
| `/embed` command | Post custom embeds (requires Manage Messages) |

---

## 🎨 Customizing messages

Open `bot.py` and edit the lists at the top:

```python
WELCOME_MESSAGES = [
    "just dropped in like a shooting star 🌟",
    # add your own lines here!
]

GOODBYE_MESSAGES = [
    "We'll keep the lights on for you 🕯️",
    # add your own lines here!
]
```

---

## 🔄 Updating the bot

1. Edit your files
2. Push to GitHub
3. Railway auto-redeploys in ~30 seconds
