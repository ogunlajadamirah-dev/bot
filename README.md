# 🤖 Pride Bot — Discord Welcome & Goodbye Bot

A Discord bot for your friend's server with automatic welcome & goodbye messages, a custom PRIDE banner, and useful slash commands. Hosted on Railway.

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

## ✅ Features

| Feature | Details |
|---|---|
| 🎉 Welcome embed | Sent automatically when someone joins |
| 👋 Goodbye embed | Sent automatically when someone leaves |
| 🔍 Auto channel | Bot finds the first available channel automatically — no setup needed |
| 🎲 Random messages | Fun unique messages every time |
| 💡 Random tips | Each welcome shows a random tip for new members |
| 📊 Stats | Shows account age and member count |
| `/setchannel` | Admin can pick any channel for welcome/goodbye messages |
| `/embed` | Post custom embeds with title, text, color and image |

---

## 🔧 Step 1 — Create your Discord Bot

1. Go to https://discord.com/developers/applications
2. Click **New Application** → give it a name
3. Go to the **Bot** tab → click **Add Bot**
4. Under **Privileged Gateway Intents**, enable:
   - ✅ **Server Members Intent**
   - ✅ **Message Content Intent**
5. Click **Reset Token** → copy your token (keep it secret!)
6. Go to **OAuth2 → URL Generator**:
   - Scopes: ✅ `bot` + ✅ `applications.commands`
   - Bot Permissions: ✅ `Send Messages` ✅ `Embed Links` ✅ `Manage Messages`
7. Copy the generated URL → open it → invite the bot to your server

---

## 🚂 Step 2 — Deploy on Railway

1. Push these files to a **GitHub repo**
2. Go to https://railway.app → sign in with GitHub
3. Click **New Project → Deploy from GitHub repo** → select your repo
4. Go to **Variables** tab → add these:

| Variable | Value |
|---|---|
| `DISCORD_TOKEN` | Your bot token from Step 1 |
| `PRIDE_BANNER_URL` | CDN link of your pride video/image (optional) |

5. Railway deploys automatically 🎉

---

## 📢 How to get PRIDE_BANNER_URL

1. Upload `pride.webp` to any Discord channel
2. Right-click the file → **Copy Link**
3. Paste it as the value of `PRIDE_BANNER_URL` in Railway

---

## 🎮 Commands

### `/setchannel` — Admin only
Pick which channel gets welcome and goodbye messages.
No setup needed — bot works automatically without this.
But if your friend wants to change the channel:
```
/setchannel #any-channel-name
```
- Works with **any channel name**
- Can be changed **anytime**
- Requires **Administrator** permission

---

### `/embed` — Manage Messages permission
Send a custom embed message in any channel.
```
/embed title: Hello! description: Welcome everyone! color: red
```

| Option | Description |
|---|---|
| `title` | The big bold heading |
| `description` | The main text |
| `color` | red, green, blue, gold, purple |
| `image` | Upload a file directly |
| `image_url` | Paste an image/video link |

---

## 🔄 How to update the bot

1. Edit `bot.py` on GitHub
2. Click **Commit changes**
3. Railway auto-redeploys in ~30 seconds ✅

---

## 💡 Tips

- The bot works on **multiple servers** at the same time
- Each server can set its **own channel** using `/setchannel`
- If no channel is set, bot automatically uses the **first available channel**
- The PRIDE banner shows on **every** welcome, goodbye and `/embed` message
