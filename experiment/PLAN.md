# Discord Customer Analyzer - Toy Experiment Plan 🧪

## 🎯 Project Overview

**Goal**: Create a minimal proof-of-concept to test the core pipeline: Discord → AI Analysis → Results
**Scope**: Toy example with ~100 lines of code total
**Purpose**: Validate API connectivity and basic functionality before building complex features

## 📁 Directory Structure 
```
experiment/
├── PLAN.md # This file - our north star
├── init.py # Empty init file
├── config.py # Simple configuration (API keys, settings)
├── discord_reader.py # Tool 1: Fetch messages from Discord
├── claude_analyzer.py # Tool 2: Analyze messages with Anthropic Claude
├── main_experiment.py # Main orchestrator - runs the pipeline
└── test_experiment.py # High-level integration tests
```
## 🛠️ Implementation Sections

### Section 1: Configuration Setup ⚙️
**Files**: `config.py`, `__init__.py`
- Load environment variables (Discord token, Anthropic API key)
- Simple configuration class
- Validation that keys exist
- **Success Criteria**: Configuration loads without errors

### Section 2: Discord Reader Tool 🔍
**File**: `discord_reader.py`
- Minimal Discord client
- Connect to a single channel
- Fetch last 10-20 messages
- Return clean message data (author, content, timestamp)
- **Success Criteria**: Can fetch messages from Discord channel

### Section 3: Claude Analyzer Tool 🧠
**File**: `claude_analyzer.py`
- Connect to Anthropic API
- Use cheapest model: `claude-3-haiku-20240307`
- Simple prompt: "Find potential customers in these messages"
- Return structured analysis
- **Success Criteria**: Claude responds with analysis

### Section 4: Main Pipeline Orchestrator 🚀
**File**: `main_experiment.py`
- Chain the tools together
- Error handling for each step
- Simple console output
- **Success Criteria**: End-to-end pipeline runs successfully

### Section 5: Integration Testing 🧪
**File**: `test_experiment.py`
- High-level tests that simulate real usage
- Test full pipeline end-to-end
- Validate API connections
- Catch regressions when code changes
- **Success Criteria**: All tests pass

## 🚫 Explicitly OUT OF SCOPE

### Won't Do (Too Complex for Toy Example):
- ❌ Database storage
- ❌ Complex message filtering
- ❌ Multiple channel analysis
- ❌ Customer scoring algorithms
- ❌ Discord embeds/responses
- ❌ Rate limiting (using tiny message counts)
- ❌ Async operations (keeping it simple)
- ❌ Error recovery mechanisms
- ❌ Logging infrastructure
- ❌ Configuration validation beyond existence checks

### Ideas for Later 💡
- Real-time message streaming
- Customer scoring with multiple criteria
- Integration with main bot codebase
- Cost tracking and optimization
- Message deduplication
- Multi-server support

## 📋 Detailed Implementation Plan

### Section 1: Configuration Setup

```python
# config.py - Simple and minimal
class ExperimentConfig:
    def __init__(self):
        self.discord_token = os.getenv("DISCORD_BOT_TOKEN")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")  # New key needed
        self.test_channel_id = os.getenv("TEST_CHANNEL_ID")
        
    def validate(self):
        # Just check keys exist
        pass
```

**Requirements**:
- Add `ANTHROPIC_API_KEY` to `.env`
- Add `TEST_CHANNEL_ID` for specific channel to test
- Keep it under 20 lines

### Section 2: Discord Reader Tool

```python
# discord_reader.py - Minimal message fetcher
class SimpleDiscordReader:
    def connect(self):
        # Simple discord client setup
        pass
        
    def fetch_recent_messages(self, channel_id, limit=15):
        # Get last N messages
        # Return: [{"author": "user", "content": "text", "timestamp": "time"}]
        pass
```

**Requirements**:
- Synchronous operation (no async complexity)
- Return plain Python dictionaries
- Handle basic connection errors
- Keep it under 30 lines

### Section 3: Claude Analyzer Tool

```python
# claude_analyzer.py - Simple AI analysis
class SimpleClaudeAnalyzer:
    def analyze_messages(self, messages):
        prompt = """
        Analyze these Discord messages for potential customers.
        Look for: pain points, questions about solutions, buying signals.
        Return JSON: {"potential_customers": int, "key_phrases": []}
        """
        # Send to Claude Haiku
        # Parse response
        pass
```

**Requirements**:
- Use `claude-3-haiku-20240307` (cheapest model)
- Simple prompt under 200 tokens
- Parse JSON response
- Basic error handling
- Keep it under 25 lines

### Section 4: Main Pipeline

```python
# main_experiment.py - Orchestrate everything
def run_experiment():
    print("🧪 Starting Discord Customer Analysis Experiment")
    
    # 1. Load config
    # 2. Connect to Discord
    # 3. Fetch messages
    # 4. Analyze with Claude
    # 5. Print results
    
    print("✅ Experiment complete!")
```

**Requirements**:
- Clear step-by-step output
- Handle errors gracefully
- Show costs/token usage
- Keep it under 25 lines

## 🧪 Testing Strategy

### High-Level Integration Tests

Focus on **real user behavior simulation**, not unit tests:

```python
# test_experiment.py
def test_full_pipeline():
    """Test complete Discord → Claude → Results pipeline"""
    pass

def test_api_connectivity():
    """Test that both Discord and Anthropic APIs work"""
    pass

def test_error_handling():
    """Test pipeline handles errors gracefully"""
    pass
```

### Why Integration Tests Over Unit Tests:
- **Catch API changes**: Real API calls detect breaking changes
- **Prevent regressions**: When LLMs modify unrelated code
- **Validate real behavior**: Tests what users actually experience
- **End-to-end validation**: Ensures the full pipeline works

## 🎯 Success Metrics

### Definition of Done for Each Section:
1. **Config**: Environment loads, keys validated
2. **Discord Reader**: Successfully fetches 10+ messages
3. **Claude Analyzer**: Returns structured analysis from real messages
4. **Main Pipeline**: Runs end-to-end without errors
5. **Tests**: All integration tests pass

### Final Success Criteria:
- [ ] Can fetch real Discord messages
- [ ] Anthropic API responds with analysis
- [ ] Pipeline runs end-to-end
- [ ] Total code under 100 lines
- [ ] API costs under $0.01 per run
- [ ] All tests pass

## 🔄 Implementation Process

1. **Read this plan** before starting each section
2. **Implement section by section** - don't try to do everything at once
3. **Test after each section** - ensure it works before moving on
4. **Update plan** if we discover issues or scope changes
5. **Use diff view** to check all LLM changes after each iteration

## 📝 Notes & Decisions

- **AI Model Choice**: Claude Haiku for cost optimization (~$0.25/1M tokens)
- **Discord Approach**: Simple synchronous client, no bot permissions needed
- **Error Handling**: Basic try/catch, fail fast approach
- **Data Format**: Plain Python dictionaries, no complex objects
- **Testing Approach**: Integration tests over unit tests for better regression detection

---

**Next Step**: Implement Section 1 (Configuration Setup) 
