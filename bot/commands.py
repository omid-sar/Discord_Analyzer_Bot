import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from typing import Optional
from datetime import datetime, timedelta

from config.settings import settings
from models.database import get_db, Channel
from analyzers.llm_analyzer import LLMAnalyzer
from utils.formatters import format_analysis_embed

import logging
logger = logging.getLogger(__name__)

class AnalysisCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.analyzer = LLMAnalyzer()
        
    @commands.hybrid_command(name='analyze', description='Analyze a channel for potential customers')
    @app_commands.describe(
        channel='The channel to analyze',
        days='Number of days to look back (default: 30)',
        limit='Maximum number of messages to analyze (default: 1000)'
    )
    async def analyze_channel(
        self, 
        ctx: commands.Context, 
        channel: Optional[discord.TextChannel] = None,
        days: int = 30,
        limit: int = 1000
    ):
        """Analyze a channel for potential customers"""
        # Default to current channel if none specified
        if channel is None:
            if isinstance(ctx.channel, discord.TextChannel):
                channel = ctx.channel
            else:
                await ctx.send("Please specify a text channel to analyze.")
                return
        
        # Check permissions
        if not channel.permissions_for(ctx.guild.me).read_message_history:
            await ctx.send(f"I don't have permission to read messages in {channel.mention}")
            return
        
        # Send initial response
        embed = discord.Embed(
            title="🔍 Channel Analysis Started",
            description=f"Analyzing {channel.mention} for potential customers...",
            color=discord.Color.blue()
        )
        embed.add_field(name="Time Range", value=f"Last {days} days", inline=True)
        embed.add_field(name="Message Limit", value=f"{limit} messages", inline=True)
        
        message = await ctx.send(embed=embed)
        
        try:
            # Fetch messages
            after_date = datetime.utcnow() - timedelta(days=days)
            messages = await self.bot.fetch_channel_messages(
                channel, 
                limit=limit, 
                after=after_date
            )
            
            # Update progress
            embed.description = f"Fetched {len(messages)} messages. Analyzing..."
            await message.edit(embed=embed)
            
            # Save messages to database
            for db in get_db():
                await self.bot.save_messages_to_db(db, channel.id, messages)
            
            # Analyze messages
            for db in get_db():
                db_channel = db.query(Channel).filter_by(discord_id=str(channel.id)).first()
                if db_channel:
                    analysis_results = await self.analyzer.analyze_channel(db, db_channel.id)
                    
                    # Format and send results
                    result_embed = format_analysis_embed(channel, analysis_results)
                    await message.edit(embed=result_embed)
                    
                    # Send detailed results if available
                    if analysis_results.get('potential_customers'):
                        await self._send_customer_details(ctx, analysis_results['potential_customers'])
                    
        except Exception as e:
            logger.error(f"Error analyzing channel: {e}")
            error_embed = discord.Embed(
                title="❌ Analysis Error",
                description=f"An error occurred while analyzing the channel: {str(e)}",
                color=discord.Color.red()
            )
            await message.edit(embed=error_embed)
    
    async def _send_customer_details(self, ctx, customers):
        """Send detailed information about potential customers"""
        if not customers:
            return
        
        embed = discord.Embed(
            title="🎯 Top Potential Customers",
            description="Based on message analysis, here are the most promising leads:",
            color=discord.Color.green()
        )
        
        for i, customer in enumerate(customers[:5]):  # Top 5
            embed.add_field(
                name=f"{i+1}. {customer['username']} (Score: {customer['score']:.2f})",
                value=f"**Pain Points:** {', '.join(customer['pain_points'][:3])}\n"
                      f"**Interests:** {', '.join(customer['interests'][:3])}\n"
                      f"**Messages:** {customer['message_count']}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='analyze_all', description='Analyze all channels in the server')
    @commands.has_permissions(administrator=True)
    async def analyze_all_channels(self, ctx: commands.Context):
        """Analyze all text channels in the server"""
        embed = discord.Embed(
            title="🔍 Server-Wide Analysis",
            description="Starting analysis of all text channels...",
            color=discord.Color.blue()
        )
        
        message = await ctx.send(embed=embed)
        
        analyzed = 0
        total = len(ctx.guild.text_channels)
        
        for channel in ctx.guild.text_channels:
            if not channel.permissions_for(ctx.guild.me).read_message_history:
                continue
            
            try:
                # Update progress
                embed.description = f"Analyzing channel {analyzed + 1}/{total}: {channel.mention}"
                await message.edit(embed=embed)
                
                # Fetch and analyze
                messages = await self.bot.fetch_channel_messages(channel, limit=500)
                
                for db in get_db():
                    await self.bot.save_messages_to_db(db, channel.id, messages)
                    
                analyzed += 1
                
                # Rate limiting between channels
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error analyzing {channel.name}: {e}")
        
        embed.title = "✅ Server Analysis Complete"
        embed.description = f"Analyzed {analyzed}/{total} channels successfully."
        embed.color = discord.Color.green()
        await message.edit(embed=embed)
    
    @commands.hybrid_command(name='customer_report', description='Generate a customer report')
    async def customer_report(self, ctx: commands.Context):
        """Generate a report of all potential customers"""
        embed = discord.Embed(
            title="📊 Generating Customer Report",
            description="Compiling data on potential customers...",
            color=discord.Color.blue()
        )
        
        message = await ctx.send(embed=embed)
        
        try:
            for db in get_db():
                report = await self.analyzer.generate_customer_report(db)
                
                # Create report embed
                report_embed = discord.Embed(
                    title="📊 Customer Analysis Report",
                    description=f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                    color=discord.Color.gold()
                )
                
                report_embed.add_field(
                    name="Total Potential Customers",
                    value=report['total_customers'],
                    inline=True
                )
                
                report_embed.add_field(
                    name="High Priority Leads",
                    value=report['high_priority_count'],
                    inline=True
                )
                
                report_embed.add_field(
                    name="Messages Analyzed",
                    value=report['total_messages'],
                    inline=True
                )
                
                # Add top pain points
                if report['top_pain_points']:
                    pain_points_text = "\n".join([
                        f"• {pp['pain_point']} ({pp['count']} mentions)"
                        for pp in report['top_pain_points'][:5]
                    ])
                    report_embed.add_field(
                        name="Top Pain Points",
                        value=pain_points_text,
                        inline=False
                    )
                
                await message.edit(embed=report_embed)
                
                # Send CSV file if requested (future feature)
                # await self._send_report_csv(ctx, report)
                
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            error_embed = discord.Embed(
                title="❌ Report Generation Error",
                description=f"Failed to generate report: {str(e)}",
                color=discord.Color.red()
            )
            await message.edit(embed=error_embed)
    
    @commands.hybrid_command(name='analyze_status', description='Check analysis status')
    async def analyze_status(self, ctx: commands.Context):
        """Check the status of channel analyses"""
        embed = discord.Embed(
            title="📊 Analysis Status",
            description="Channel analysis information:",
            color=discord.Color.blue()
        )
        
        for db in get_db():
            channels = db.query(Channel).filter_by(
                discord_id=str(ctx.guild.id)
            ).all()
            
            analyzed = 0
            for channel in channels:
                if channel.last_analyzed:
                    analyzed += 1
                    
            embed.add_field(
                name="Channels Analyzed",
                value=f"{analyzed}/{len(channels)}",
                inline=True
            )
            
            # Find most recent analysis
            most_recent = max(
                (ch.last_analyzed for ch in channels if ch.last_analyzed),
                default=None
            )
            
            if most_recent:
                embed.add_field(
                    name="Last Analysis",
                    value=f"{most_recent.strftime('%Y-%m-%d %H:%M UTC')}",
                    inline=True
                )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AnalysisCommands(bot)) 