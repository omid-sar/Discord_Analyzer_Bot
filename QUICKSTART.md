# Quick Start Guide 🚀

Get your Discord Customer Analyzer Bot running in 5 minutes!

## 1. Clone and Setup (1 minute)

```bash
# Clone the repository
git clone <your-repo-url>
cd letta_discord

# Create virtual environment and install dependencies
python -m venv discord_bot
source discord_bot/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt


# 6. Test run the bot
python main.py
```

## 2. Create Discord Bot (2 minutes)

1. Visit [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" → Name it → Create
3. Go to "Bot" section → Click "Add Bot"
4. Copy the **Bot Token** (you'll need this!)
5. Enable these Privileged Intents:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT

## 3. Get OpenAI API Key (1 minute)

1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create new secret key
3. Copy the key (starts with `sk-`)

## 4. Configure Bot (30 seconds)

```bash
# Copy example environment file
cp example.env .env

# Edit .env file with your favorite editor
# Add your Discord Bot Token and OpenAI API Key
```

## 5. Invite Bot to Server (30 seconds)

1. In Discord Developer Portal, go to OAuth2 → URL Generator
2. Select scopes: `bot`, `applications.commands`
3. Select permissions:
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
   - Embed Links
4. Copy generated URL and open in browser
5. Select your server and authorize

## 6. Run the Bot! 🎉

```bash
python main.py
```

## 7. Test It Out

In your Discord server, type:
```
!analyze
```

The bot will analyze the current channel for potential customers!

## Common Issues

**Bot not responding?**
- Check bot has permissions in the channel
- Ensure MESSAGE CONTENT INTENT is enabled
- Verify bot is online (green dot)

**OpenAI errors?**
- Check your API key is valid
- Ensure you have credits in your OpenAI account
- Try using `gpt-3.5-turbo` model if rate limited

## Next Steps

- Customize `CUSTOMER_KEYWORDS` in `.env` for your startup
- Try `!analyze #channel-name 30 500` for specific analysis
- Run `!customer_report` to see all identified leads
- Check the README.md for advanced features

Happy customer hunting! 🎯 