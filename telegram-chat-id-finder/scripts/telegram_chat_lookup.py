#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Chat ID Finder
Fetches all active chat IDs that a Telegram bot has received messages from.
"""

import requests
import json
import sys
import io
from datetime import datetime
from collections import defaultdict

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def get_chat_updates(token, limit=100):
    """
    Fetch all updates from Telegram bot API.

    Args:
        token: Telegram Bot Token
        limit: Maximum number of updates to fetch (default 100)

    Returns:
        List of updates or None if failed
    """
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"limit": limit}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not data.get("ok"):
            print(f"Error: {data.get('description', 'Unknown error')}")
            return None

        return data.get("result", [])

    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Invalid response from Telegram API")
        return None

def extract_chat_info(updates):
    """
    Extract chat IDs and metadata from updates.

    Returns:
        Dictionary mapping chat_id to chat info with latest message
    """
    chats = defaultdict(lambda: {
        "type": None,
        "title": None,
        "username": None,
        "first_name": None,
        "last_name": None,
        "latest_message": None,
        "latest_timestamp": None,
        "sender_name": None,
        "message_count": 0
    })

    for update in updates:
        # Handle message updates
        if "message" in update:
            msg = update["message"]
            chat = msg.get("chat", {})
            chat_id = chat.get("id")

            if chat_id:
                # Update chat info
                chats[chat_id]["type"] = chat.get("type", "unknown")
                chats[chat_id]["title"] = chat.get("title")
                chats[chat_id]["username"] = chat.get("username")
                chats[chat_id]["first_name"] = chat.get("first_name")
                chats[chat_id]["last_name"] = chat.get("last_name")
                chats[chat_id]["message_count"] += 1

                # Extract message content
                msg_text = msg.get("text", "")
                if not msg_text and msg.get("caption"):
                    msg_text = f"[{msg.get('type', 'media')}] {msg.get('caption')}"
                elif not msg_text:
                    msg_type = msg.get("type", "message")
                    if "photo" in msg:
                        msg_text = "[Photo]"
                    elif "video" in msg:
                        msg_text = "[Video]"
                    elif "voice" in msg:
                        msg_text = "[Voice]"
                    elif "document" in msg:
                        msg_text = f"[Document: {msg['document'].get('file_name', 'file')}]"
                    elif "sticker" in msg:
                        msg_text = "[Sticker]"
                    else:
                        msg_text = f"[{msg_type.upper()}]"

                # Truncate long messages
                if len(msg_text) > 60:
                    msg_text = msg_text[:57] + "..."

                # Update latest message
                msg_time = msg.get("date", 0)
                if msg_time >= (chats[chat_id]["latest_timestamp"] or 0):
                    chats[chat_id]["latest_message"] = msg_text
                    chats[chat_id]["latest_timestamp"] = msg_time

                    # Get sender name
                    sender = msg.get("from", {})
                    sender_name = sender.get("first_name", "")
                    if sender.get("last_name"):
                        sender_name += f" {sender.get('last_name')}"
                    if sender.get("username"):
                        sender_name += f" (@{sender.get('username')})"

                    if not sender_name:
                        sender_name = chat.get("title") or f"User {sender.get('id')}"

                    chats[chat_id]["sender_name"] = sender_name

    return chats

def format_chat_display(chat_id, info):
    """Format a single chat for display."""
    chat_type = info["type"] or "unknown"

    # Determine display name
    if info["title"]:
        display_name = info["title"]
    elif info["first_name"]:
        display_name = info["first_name"]
        if info["last_name"]:
            display_name += f" {info['last_name']}"
    elif info["username"]:
        display_name = f"@{info['username']}"
    else:
        display_name = f"User {chat_id}"

    message = info["latest_message"] or "[No messages yet]"
    timestamp = ""
    if info["latest_timestamp"]:
        dt = datetime.fromtimestamp(info["latest_timestamp"])
        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "chat_id": chat_id,
        "type": chat_type,
        "name": display_name,
        "latest_message": message,
        "timestamp": timestamp,
        "count": info["message_count"]
    }

def main():
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        # Read token from stdin if provided
        try:
            token = input("Enter Telegram Bot Token: ").strip()
        except EOFError:
            print("No token provided")
            sys.exit(1)

    if not token:
        print("Token cannot be empty")
        sys.exit(1)

    print(f"[*] Fetching updates from Telegram bot...")
    updates = get_chat_updates(token)

    if updates is None:
        sys.exit(1)

    if not updates:
        print("[OK] Bot has no updates yet. Send a message to your bot first.")
        sys.exit(0)

    # Extract chat information
    chats = extract_chat_info(updates)

    if not chats:
        print("[OK] No chat IDs found in updates.")
        sys.exit(0)

    # Sort by latest timestamp (newest first)
    sorted_chats = sorted(
        chats.items(),
        key=lambda x: x[1]["latest_timestamp"] or 0,
        reverse=True
    )

    # Display results
    print(f"\n[OK] Found {len(sorted_chats)} active chat(s):\n")
    print("=" * 130)
    print(f"{'Chat ID':<15} {'Type':<12} {'Name':<30} {'Latest Message':<50} {'Time':<20}")
    print("=" * 130)

    for chat_id, info in sorted_chats:
        display = format_chat_display(chat_id, info)
        print(
            f"{str(display['chat_id']):<15} "
            f"{display['type']:<12} "
            f"{display['name'][:29]:<30} "
            f"{display['latest_message'][:49]:<50} "
            f"{display['timestamp']:<20}"
        )

    print("=" * 130)
    print(f"\n[Summary] {len(sorted_chats)} chat(s), {sum(info['message_count'] for info in chats.values())} total message(s)")

    # Also output as JSON for programmatic use
    json_output = [format_chat_display(cid, info) for cid, info in sorted_chats]
    print("\n[JSON Output]")
    print(json.dumps(json_output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
