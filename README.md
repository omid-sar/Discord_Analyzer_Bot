# Discord Customer Analyzer Bot 🎯

An intelligent Discord bot that uses LLMs to analyze channel messages and identify potential customers for your startup. The bot can scan Discord conversations, identify pain points, and generate detailed reports on potential leads.

## 🚀 Features

- **Channel Analysis**: Scan Discord channels for customer intent
- **Smart Identification**: Uses LLMs to identify pain points and buying signals
- **Customer Scoring**: Rates users based on their likelihood to be customers
- **Detailed Reports**: Generate comprehensive reports with insights
- **Real-time Monitoring**: Optionally analyze new messages as they come in
- **Database Storage**: Persist all data for long-term analysis
- **Rate Limiting**: Respects Discord and OpenAI API limits

## 📋 Implementation Plan Overview

### ✅ Phase 1: Research & Setup (Complete)
- Researched Discord API capabilities and limitations
- Investigated Letta (MemGPT) integration possibilities
- Designed database schema for message storage
- Created project structure

### ✅ Phase 2: Core Bot Development (Complete)
- Built Discord bot with message reading capabilities
- Implemented database models for persistent storage
- Created command system for channel analysis
- Added rate limiting and error handling

### ✅ Phase 3: LLM Integration (Complete)
- Integrated OpenAI API for message analysis
- Created intelligent message batching system
- Built customer identification algorithms
- Implemented scoring and ranking system

### 🔄 Phase 4: Advanced Features (Next Steps)
- [ ] Letta integration for memory management
- [ ] CSV export functionality
- [ ] Webhook notifications for high-value leads
- [ ] Dashboard web interface
- [ ] Multi-language support
- [ ] Custom analysis templates

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Discord Bot Token
- OpenAI API Key
- Discord Server with appropriate permissions

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd discord-customer-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the root directory:

```env
# Discord Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Database Configuration
DATABASE_URL=sqlite:///discord_analyzer.db

# Analysis Configuration
MAX_MESSAGES_PER_CHANNEL=1000
ANALYSIS_BATCH_SIZE=50

# Customer Keywords (customize for your startup)
CUSTOMER_KEYWORDS=looking for,need help with,does anyone know,recommendation,suggest,problem with,issue with,frustrated with,solution for
```

### 4. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token to your `.env` file
5. Enable these Privileged Gateway Intents:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT
6. Generate invite link with these permissions:
   - Read Messages/View Channels
   - Send Messages
   - Read Message History
   - Add Reactions
   - Embed Links

### 5. Run the Bot

```bash
python main.py
```

## 📝 Usage

### Basic Commands

- **`!analyze [#channel] [days] [limit]`** - Analyze a specific channel
  - Example: `!analyze #general 30 1000`
  
- **`!analyze_all`** - Analyze all channels in the server (Admin only)

- **`!customer_report`** - Generate a report of all potential customers

- **`!analyze_status`** - Check the status of channel analyses

### Analysis Process

1. The bot fetches messages from the specified channel
2. Messages are batched based on token limits
3. Each batch is analyzed by the LLM for:
   - Customer intent signals
   - Pain points
   - Interests/needs
   - Engagement level
4. Results are aggregated and scored
5. Potential customers are saved to the database
6. A summary report is generated

## 🗂️ Project Structure

```
discord-customer-analyzer/
├── config/
│   └── settings.py          # Configuration management
├── models/
│   └── database.py          # Database models
├── bot/
│   ├── discord_bot.py       # Main bot class
│   └── commands.py          # Command handlers
├── analyzers/
│   └── llm_analyzer.py      # LLM analysis logic
├── utils/
│   └── formatters.py        # Discord embed formatters
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## 🔍 How It Works

### Message Analysis Pipeline

1. **Message Collection**: Bot reads historical messages from channels
2. **Preprocessing**: Messages are cleaned and batched
3. **LLM Analysis**: Each batch is analyzed for customer signals
4. **Score Calculation**: Users are scored based on their messages
5. **Aggregation**: Multiple messages from same user are combined
6. **Reporting**: Results are formatted and presented

### Customer Scoring Algorithm

- **Intent Score** (0-1): How likely the message shows buying intent
- **Engagement Level**: Based on score and message frequency
  - High: Score > 0.8 and messages > 5
  - Medium: Score > 0.6 or messages > 3
  - Low: All others
- **Pain Points**: Extracted problems mentioned
- **Interests**: What solutions they're looking for

## 🚧 Future Enhancements

### Letta (MemGPT) Integration
- Persistent memory across analysis sessions
- Advanced reasoning about customer relationships
- Context-aware follow-up suggestions

### Advanced Analytics
- Sentiment analysis over time
- Conversation thread analysis
- Network analysis (who talks to whom)
- Topic modeling and clustering

### Automation Features
- Auto-generate outreach messages
- Schedule periodic analysis
- Alert on high-value prospects
- Integration with CRM systems

## 🔒 Privacy & Ethics

- Only analyzes public channels you have access to
- Respects Discord's Terms of Service
- Stores minimal personal data
- Provides transparency in analysis methods
- Allows users to opt-out (future feature)

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

MIT License - see LICENSE file for details

## ⚠️ Disclaimer

This tool should be used responsibly and in accordance with Discord's Terms of Service. Always respect user privacy and community guidelines. 