import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timezone
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from config.settings import settings
from models.database import get_db, Guild, Channel, Message

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomerAnalyzerBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(command_prefix='!', intents=intents)
        
    async def setup_hook(self):
        """Initialize bot extensions and sync commands"""
        await self.load_extension('bot.commands')
        logger.info("Bot extensions loaded")
        
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        
        # Update guild information in database
        for db in get_db():
            for guild in self.guilds:
                await self.update_guild_info(db, guild)
            db.commit()
    
    async def update_guild_info(self, db: Session, guild: discord.Guild):
        """Update guild information in database"""
        db_guild = db.query(Guild).filter_by(discord_id=str(guild.id)).first()
        
        if not db_guild:
            db_guild = Guild(
                discord_id=str(guild.id),
                name=guild.name
            )
            db.add(db_guild)
            db.flush()
        else:
            db_guild.name = guild.name
            db_guild.updated_at = datetime.utcnow()
        
        # Update channels
        for channel in guild.text_channels:
            db_channel = db.query(Channel).filter_by(discord_id=str(channel.id)).first()
            
            if not db_channel:
                db_channel = Channel(
                    discord_id=str(channel.id),
                    guild_id=db_guild.id,
                    name=channel.name,
                    type='text'
                )
                db.add(db_channel)
            else:
                db_channel.name = channel.name
                db_channel.updated_at = datetime.utcnow()
    
    async def fetch_channel_messages(
        self, 
        channel: discord.TextChannel, 
        limit: int = 1000,
        after: Optional[datetime] = None
    ) -> List[discord.Message]:
        """Fetch messages from a channel with rate limiting"""
        messages = []
        
        try:
            async for message in channel.history(limit=limit, after=after, oldest_first=True):
                messages.append(message)
                
                # Rate limiting
                if len(messages) % 100 == 0:
                    await asyncio.sleep(settings.DISCORD_RATE_LIMIT_DELAY)
                    
        except discord.Forbidden:
            logger.warning(f"No permission to read messages in {channel.name}")
        except Exception as e:
            logger.error(f"Error fetching messages from {channel.name}: {e}")
            
        return messages
    
    async def save_messages_to_db(self, db: Session, channel_id: int, messages: List[discord.Message]):
        """Save messages to database"""
        db_channel = db.query(Channel).filter_by(discord_id=str(channel_id)).first()
        
        if not db_channel:
            logger.error(f"Channel {channel_id} not found in database")
            return
        
        saved_count = 0
        for msg in messages:
            # Skip bot messages
            if msg.author.bot:
                continue
                
            # Check if message already exists
            existing = db.query(Message).filter_by(discord_id=str(msg.id)).first()
            if existing:
                continue
            
            db_message = Message(
                discord_id=str(msg.id),
                channel_id=db_channel.id,
                author_id=str(msg.author.id),
                author_name=msg.author.name,
                content=msg.content,
                created_at=msg.created_at.replace(tzinfo=timezone.utc)
            )
            db.add(db_message)
            saved_count += 1
            
            # Commit in batches
            if saved_count % 100 == 0:
                db.commit()
        
        db.commit()
        logger.info(f"Saved {saved_count} new messages from channel {db_channel.name}")
        
        # Update last analyzed timestamp
        db_channel.last_analyzed = datetime.utcnow()
        db.commit()

    async def on_message(self, message: discord.Message):
        """Handle new messages"""
        # Don't process bot messages
        if message.author.bot:
            return
            
        # Process commands
        await self.process_commands(message)
        
        # Save message to database for real-time analysis (optional)
        if message.guild and isinstance(message.channel, discord.TextChannel):
            for db in get_db():
                await self.save_single_message(db, message)

    async def save_single_message(self, db: Session, message: discord.Message):
        """Save a single message to database"""
        db_channel = db.query(Channel).filter_by(discord_id=str(message.channel.id)).first()
        
        if db_channel:
            db_message = Message(
                discord_id=str(message.id),
                channel_id=db_channel.id,
                author_id=str(message.author.id),
                author_name=message.author.name,
                content=message.content,
                created_at=message.created_at.replace(tzinfo=timezone.utc)
            )
            db.add(db_message)
            db.commit()

# Create bot instance
bot = CustomerAnalyzerBot() 