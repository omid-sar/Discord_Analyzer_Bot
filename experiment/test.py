# Quick test script to verify IDs
import discord
import os
from dotenv import load_dotenv

# Load .env from parent directory
print("🔍 Loading environment variables...")
load_dotenv("../.env") 

# Debug: Print what we loaded
print("\n📋 Environment Variables:")
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DISCORD_GUILD_ID_STR = os.environ.get("DISCORD_GUILD_ID")
TEST_CHANNEL_ID_STR = os.environ.get("TEST_CHANNEL_ID")

print(f"DISCORD_BOT_TOKEN: {'✅ Found' if DISCORD_BOT_TOKEN else '❌ Missing'}")
print(f"DISCORD_GUILD_ID: {DISCORD_GUILD_ID_STR}")
print(f"TEST_CHANNEL_ID: {TEST_CHANNEL_ID_STR}")

# Convert to integers with error handling
try:
    DISCORD_GUILD_ID = int(DISCORD_GUILD_ID_STR) if DISCORD_GUILD_ID_STR else None
    CHANNEL_ID = int(TEST_CHANNEL_ID_STR) if TEST_CHANNEL_ID_STR else None
    print(f"✅ Converted Guild ID: {DISCORD_GUILD_ID}")
    print(f"✅ Converted Channel ID: {CHANNEL_ID}")
except ValueError as e:
    print(f"❌ Error converting IDs to integers: {e}")
    exit(1)

if not DISCORD_BOT_TOKEN:
    print("❌ Discord bot token is missing!")
    exit(1)

if not DISCORD_GUILD_ID:
    print("❌ Discord guild ID is missing!")
    exit(1)

if not CHANNEL_ID:
    print("❌ Test channel ID is missing!")
    exit(1)

# Set up intents properly
intents = discord.Intents.default()
intents.message_content = True

# Create client only once
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"\n🤖 Bot logged in as {client.user}")
    
    # Show all servers the bot can see first
    print(f"\n🔍 Bot is in {len(client.guilds)} server(s):")
    for guild in client.guilds:
        print(f"  - {guild.name} (ID: {guild.id})")
    
    # Test your specific guild and channel
    guild = client.get_guild(DISCORD_GUILD_ID)
    channel = client.get_channel(CHANNEL_ID)
    
    print(f"\n🎯 Target Results:")
    print(f"Guild: {guild.name if guild else 'Not found'}")
    print(f"Channel: {channel.name if channel else 'Not found'}")
    
    # Test fetching a few messages
    if channel:
        try:
            messages = [message async for message in channel.history(limit=3)]
            print(f"✅ Found {len(messages)} recent messages in #{channel.name}")
            for msg in messages:
                print(f"  - {msg.author}: {msg.content[:50]}...")
        except discord.Forbidden:
            print("❌ Bot doesn't have permission to read messages in this channel")
        except Exception as e:
            print(f"❌ Error reading messages: {e}")
    
    await client.close()

if __name__ == "__main__":
    try:
        print("\n🚀 Starting Discord connection...")
        client.run(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
