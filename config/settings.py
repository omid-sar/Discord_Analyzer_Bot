import os
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings configuration"""
    
    # Discord Configuration
    DISCORD_BOT_TOKEN: str = os.getenv("DISCORD_BOT_TOKEN", "")
    DISCORD_GUILD_ID: Optional[int] = int(os.getenv("DISCORD_GUILD_ID", "0")) if os.getenv("DISCORD_GUILD_ID") else None
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///discord_analyzer.db")
    
    # Analysis Configuration
    MAX_MESSAGES_PER_CHANNEL: int = int(os.getenv("MAX_MESSAGES_PER_CHANNEL", "1000"))
    ANALYSIS_BATCH_SIZE: int = int(os.getenv("ANALYSIS_BATCH_SIZE", "50"))
    
    # Letta Configuration
    LETTA_API_KEY: Optional[str] = os.getenv("LETTA_API_KEY")
    USE_LETTA_MEMORY: bool = os.getenv("USE_LETTA_MEMORY", "false").lower() == "true"
    
    # Customer Analysis Keywords
    CUSTOMER_KEYWORDS: List[str] = [
        k.strip() for k in os.getenv(
            "CUSTOMER_KEYWORDS", 
            "looking for,need help with,does anyone know,recommendation,suggest,problem with,issue with,frustrated with,solution for"
        ).split(",")
    ]
    
    # Rate Limiting
    DISCORD_RATE_LIMIT_DELAY: float = 1.0  # seconds between API calls
    OPENAI_RATE_LIMIT_DELAY: float = 0.5  # seconds between API calls
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    def __init__(self):
        # Create necessary directories
        self.DATA_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)
    
    def validate(self) -> List[str]:
        """Validate required settings and return list of errors"""
        errors = []
        
        if not self.DISCORD_BOT_TOKEN:
            errors.append("DISCORD_BOT_TOKEN is required")
        
        if not self.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")
            
        return errors

settings = Settings() 