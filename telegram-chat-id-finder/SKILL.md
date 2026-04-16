---
name: telegram-chat-id-finder
description: Query a Telegram bot's active chat IDs. Use this skill whenever the user wants to find chat IDs from their Telegram bot, look up which groups or users the bot has interacted with, or identify a specific chat by its recent messages. Just provide the bot token and the skill will fetch all active chats with their latest messages for easy comparison and identification.
compatibility: Python 3.6+, requests library, Telegram Bot API
---

# Telegram Chat ID Finder

Quickly discover all active chat IDs that your Telegram bot has received messages from, complete with recent messages for easy identification.

## What this skill does

- Takes a Telegram Bot Token as input
- Fetches all updates the bot has received using Telegram's `getUpdates` API
- Extracts unique chat IDs from all messages
- Displays each chat ID with metadata (type, user info) and the most recent message for identification

## When to use this

Use this skill when you need to:
- Find the chat ID of a specific group or user
- Get a complete list of all active chats your bot is monitoring
- Identify chats by their recent messages
- Set up automation based on specific chat IDs

## How to use

### Step 1: Get your Telegram Bot Token
If you don't have one, create a bot by messaging [@BotFather](https://t.me/botfather) on Telegram and following the instructions.

### Step 2: Ask Claude to run this skill
Simply tell Claude: "Show me all the chat IDs for my Telegram bot" and provide your bot token.

**Example queries:**
- "我的 TG 机器人最近在哪些群和用户那收到过消息？Token 是 123:ABC..."
- "Find all chat IDs my bot has received messages from, my token is..."
- "列出我的 Telegram bot 的所有活跃 chat ID"

### Step 3: Review the results
The skill will display:
- **Chat ID**: The unique identifier for the chat
- **Type**: Whether it's a private chat, group, or supergroup
- **Latest Message**: The most recent message received in that chat (for identification)
- **Sender**: Who sent the message (user name or group name)

## Output Format

The results are presented as a table with columns:
| Chat ID | Type | Sender/Group | Latest Message | Message Time |
|---------|------|-------------|-----------------|--------------|

This makes it easy to scan through and identify the chat you're looking for.

## Important Notes

- **Token Security**: Your bot token is sensitive — handle it carefully and don't share it in public channels
- **Update Limit**: Telegram's API returns the last 100 updates by default (configurable)
- **Message History**: Only shows chats that have sent messages to the bot (inactive chats won't appear)

## Example

**Input:**
```
Bot Token: 123456789:ABCdefGHIjklmnoPQRstuvWXYZ
```

**Output:**
```
Chat ID        | Type      | Sender/Group        | Latest Message           | Time
---------------|-----------|---------------------|--------------------------|----------
12345678       | private   | John Doe            | Hello bot!               | 2026-04-15 10:30
-100123456789  | supergroup| My Awesome Group    | /start                   | 2026-04-15 10:15
87654321       | private   | Jane Smith          | Thanks for the update    | 2026-04-15 09:45
```

## Implementation

This skill uses the Telegram Bot API's `getUpdates` endpoint to retrieve all messages sent to your bot. It then:

1. Extracts unique chat IDs
2. Groups messages by chat for analysis
3. Displays the most recent message from each chat
4. Formats results in an easy-to-read table

No data is stored or transmitted anywhere except for the local processing in this tool.
