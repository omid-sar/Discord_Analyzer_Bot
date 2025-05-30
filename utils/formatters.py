import discord
from typing import Dict, Any, List

def format_analysis_embed(channel: discord.TextChannel, analysis: Dict[str, Any]) -> discord.Embed:
    """Format analysis results as Discord embed"""
    
    if analysis.get('status') == 'no_messages':
        embed = discord.Embed(
            title="📊 Channel Analysis Complete",
            description=f"No messages found in {channel.mention}",
            color=discord.Color.orange()
        )
        return embed
    
    # Create main embed
    embed = discord.Embed(
        title="✅ Channel Analysis Complete",
        description=f"Analysis of {channel.mention}",
        color=discord.Color.green()
    )
    
    # Add summary
    embed.add_field(
        name="📝 Summary",
        value=analysis.get('summary', 'Analysis completed successfully'),
        inline=False
    )
    
    # Add statistics
    embed.add_field(
        name="📊 Messages Analyzed",
        value=str(analysis.get('total_messages_analyzed', 0)),
        inline=True
    )
    
    embed.add_field(
        name="🎯 Potential Customers",
        value=str(len(analysis.get('potential_customers', []))),
        inline=True
    )
    
    # Add top potential customers
    customers = analysis.get('potential_customers', [])
    if customers:
        top_customers = customers[:3]  # Top 3
        customer_text = "\n".join([
            f"**{i+1}. {c['username']}** (Score: {c['score']:.2f})"
            for i, c in enumerate(top_customers)
        ])
        
        embed.add_field(
            name="🌟 Top Prospects",
            value=customer_text,
            inline=False
        )
    
    return embed

def format_customer_embed(customer: Dict[str, Any]) -> discord.Embed:
    """Format individual customer information as Discord embed"""
    
    # Determine color based on engagement level
    color_map = {
        'high': discord.Color.gold(),
        'medium': discord.Color.blue(),
        'low': discord.Color.light_gray()
    }
    
    embed = discord.Embed(
        title=f"👤 {customer['username']}",
        description=f"Potential Customer Analysis",
        color=color_map.get(customer['engagement_level'], discord.Color.blue())
    )
    
    # Score and engagement
    embed.add_field(
        name="📊 Customer Score",
        value=f"{customer['score']:.2f}/1.00",
        inline=True
    )
    
    embed.add_field(
        name="🔥 Engagement Level",
        value=customer['engagement_level'].capitalize(),
        inline=True
    )
    
    embed.add_field(
        name="💬 Messages Analyzed",
        value=str(customer['message_count']),
        inline=True
    )
    
    # Pain points
    if customer.get('pain_points'):
        pain_points_text = "\n".join([f"• {pp}" for pp in customer['pain_points'][:5]])
        embed.add_field(
            name="🎯 Pain Points",
            value=pain_points_text or "None identified",
            inline=False
        )
    
    # Interests
    if customer.get('interests'):
        interests_text = "\n".join([f"• {interest}" for interest in customer['interests'][:5]])
        embed.add_field(
            name="💡 Interests/Needs",
            value=interests_text or "None identified",
            inline=False
        )
    
    return embed

def format_report_summary(report: Dict[str, Any]) -> str:
    """Format report data as text summary"""
    
    summary = "**📊 Customer Analysis Report Summary**\n\n"
    
    summary += f"**Total Potential Customers:** {report['total_customers']}\n"
    summary += f"**High Priority Leads:** {report['high_priority_count']}\n"
    summary += f"**Total Messages Analyzed:** {report['total_messages']}\n\n"
    
    if report['top_pain_points']:
        summary += "**Top Pain Points:**\n"
        for pp in report['top_pain_points'][:5]:
            summary += f"• {pp['pain_point']} ({pp['count']} mentions)\n"
    
    return summary

def truncate_text(text: str, max_length: int = 1024) -> str:
    """Truncate text to fit Discord embed limits"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."

def format_error_embed(error: Exception) -> discord.Embed:
    """Format error as Discord embed"""
    embed = discord.Embed(
        title="❌ Error Occurred",
        description=f"An error occurred during processing",
        color=discord.Color.red()
    )
    
    embed.add_field(
        name="Error Type",
        value=type(error).__name__,
        inline=True
    )
    
    embed.add_field(
        name="Error Message",
        value=truncate_text(str(error), 1024),
        inline=False
    )
    
    return embed 