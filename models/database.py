from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from config.settings import settings

Base = declarative_base()

class Guild(Base):
    __tablename__ = 'guilds'
    
    id = Column(Integer, primary_key=True)
    discord_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    channels = relationship("Channel", back_populates="guild", cascade="all, delete-orphan")

class Channel(Base):
    __tablename__ = 'channels'
    
    id = Column(Integer, primary_key=True)
    discord_id = Column(String(50), unique=True, nullable=False)
    guild_id = Column(Integer, ForeignKey('guilds.id'), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50))  # text, voice, etc.
    last_analyzed = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    guild = relationship("Guild", back_populates="channels")
    messages = relationship("Message", back_populates="channel", cascade="all, delete-orphan")
    analyses = relationship("ChannelAnalysis", back_populates="channel", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    discord_id = Column(String(50), unique=True, nullable=False)
    channel_id = Column(Integer, ForeignKey('channels.id'), nullable=False)
    author_id = Column(String(50), nullable=False)
    author_name = Column(String(255))
    content = Column(Text)
    created_at = Column(DateTime, nullable=False)
    
    channel = relationship("Channel", back_populates="messages")
    analyses = relationship("MessageAnalysis", back_populates="message", cascade="all, delete-orphan")

class ChannelAnalysis(Base):
    __tablename__ = 'channel_analyses'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('channels.id'), nullable=False)
    analysis_type = Column(String(50))  # 'customer_intent', 'sentiment', etc.
    summary = Column(Text)
    insights = Column(JSON)  # Store structured insights
    created_at = Column(DateTime, default=datetime.utcnow)
    
    channel = relationship("Channel", back_populates="analyses")

class MessageAnalysis(Base):
    __tablename__ = 'message_analyses'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    intent_score = Column(Float)  # 0-1 score for customer intent
    intent_type = Column(String(100))  # 'seeking_solution', 'expressing_frustration', etc.
    sentiment = Column(String(50))  # 'positive', 'negative', 'neutral'
    keywords = Column(JSON)  # List of identified keywords
    insights = Column(Text)  # LLM-generated insights
    created_at = Column(DateTime, default=datetime.utcnow)
    
    message = relationship("Message", back_populates="analyses")

class PotentialCustomer(Base):
    __tablename__ = 'potential_customers'
    
    id = Column(Integer, primary_key=True)
    discord_user_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(255))
    score = Column(Float)  # Overall score as potential customer
    pain_points = Column(JSON)  # List of identified pain points
    interests = Column(JSON)  # List of interests/needs
    engagement_level = Column(String(50))  # 'high', 'medium', 'low'
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    message_count = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database setup
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 