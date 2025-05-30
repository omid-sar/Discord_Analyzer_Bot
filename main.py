import asyncio
import logging
from rich.console import Console
from rich.logging import RichHandler

from config.settings import settings
from models.database import init_db
from bot.discord_bot import bot

# Setup logging with rich
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the Discord bot"""
    console.print("[bold green]Discord Customer Analyzer Bot Starting...[/bold green]")
    
    # Validate settings
    errors = settings.validate()
    if errors:
        console.print("[bold red]Configuration errors found:[/bold red]")
        for error in errors:
            console.print(f"  • {error}")
        return
    
    # Initialize database
    console.print("Initializing database...")
    init_db()
    console.print("[green]✓[/green] Database initialized")
    
    # Start bot
    try:
        console.print("Starting Discord bot...")
        await bot.start(settings.DISCORD_BOT_TOKEN)
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down bot...[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        logger.exception("Bot crashed")
    finally:
        await bot.close()
        console.print("[green]Bot shut down successfully[/green]")

if __name__ == "__main__":
    asyncio.run(main()) 