# Telegram Chat ID Finder

A Claude Skill that helps you quickly discover all active chat IDs that your Telegram bot has received messages from.

## Overview

This skill makes it easy to:
- Find the chat ID of a specific group or user
- Get a complete list of all active chats your bot is monitoring
- Identify chats by their recent messages
- Set up automation based on specific chat IDs

## Files

```
telegram-chat-id-finder/
├── SKILL.md                    # Skill definition and documentation
├── README.md                   # This file
└── scripts/
    └── telegram_chat_lookup.py # Python script that queries Telegram API
```

## Quick Start

### Prerequisites
- Python 3.6+
- `requests` library: `pip install requests`
- A Telegram Bot Token (get one from [@BotFather](https://t.me/botfather))

### Usage

#### Option 1: Using the Skill in Claude Code
```
/telegram-chat-id-finder
```

Then provide your Telegram Bot Token when prompted.

#### Option 2: Run the script directly
```bash
python scripts/telegram_chat_lookup.py "YOUR_BOT_TOKEN"
```

#### Option 3: Natural language in Claude
```
I have a Telegram bot with token XXX:YYY. 
Show me all the chat IDs it has received messages from.
```

## Output Format

The skill displays results in two formats:

### Table Format
```
Chat ID         Type         Name                      Latest Message              Time
-4899242611     group        SSSAPI_主機通報群組         @sss_api_bot Test1234      2026-04-15 22:23:06
-4850418724     group        【研二】H5 KPI機器人       SSS API 數據整合報表        2026-04-15 17:39:26
```

### JSON Format
```json
[
  {
    "chat_id": -4899242611,
    "type": "group",
    "name": "SSSAPI_主機通報群組",
    "latest_message": "@sss_api_bot Test1234",
    "timestamp": "2026-04-15 22:23:26",
    "count": 2
  },
  ...
]
```

## Features

✅ Supports private chats, groups, and supergroups
✅ Shows the latest message from each chat for easy identification
✅ UTF-8 encoding support for Chinese and other languages
✅ Both table and JSON output formats
✅ Displays message count per chat
✅ Timestamp information for all messages

## Important Security Notes

⚠️ **Token Safety**: Your Telegram bot token is sensitive!
- Never share it in public channels
- Keep it in environment variables or `.env` files
- If exposed, regenerate it immediately at [@BotFather](https://t.me/botfather)

## How it Works

1. Takes your Telegram Bot Token as input
2. Calls Telegram's `getUpdates` API endpoint
3. Extracts unique chat IDs from all received messages
4. Displays chat metadata and latest messages
5. Formats output as both table and JSON

## Dependencies

- Python 3.6+
- `requests` library for HTTP requests
- Telegram Bot API (free service)

## Support

For issues or improvements, refer to the SKILL.md documentation or contact the developer.

## License

MIT

---

**Created**: 2026-04-16  
**Version**: 1.0  
**Status**: ✅ Production Ready
