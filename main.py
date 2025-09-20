# -*- coding: utf-8 -*-

import os
import json
import webbrowser

from flowlauncher import FlowLauncher

class Telegram(FlowLauncher):
    """
    A Flow Launcher plugin to quickly open Telegram chats from a manually managed list.
    """

    def query(self, query):
        """
        Handles user input from Flow Launcher.
        """
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        chats_file = os.path.join(plugin_dir, "chats.json")
        default_icon = os.path.join(plugin_dir, "icon.png")
        
        results = []
        
        try:
            with open(chats_file, 'r', encoding='utf-8') as f:
                chats = json.load(f)
        except FileNotFoundError:
            results.append({
                "Title": "Error: chats.json not found",
                "SubTitle": "Please create a chats.json file in the plugin directory.",
                "IcoPath": default_icon
            })
            return results
        except json.JSONDecodeError:
            results.append({
                "Title": "Error: Invalid JSON in chats.json",
                "SubTitle": "Please check the file for syntax errors.",
                "IcoPath": default_icon
            })
            return results

        search_term = query.strip().lower()

        if not search_term:
            filtered_chats = chats
        else:
            filtered_chats = [
                chat for chat in chats 
                if search_term in chat.get("name", "").lower()
            ]

        for chat in filtered_chats:
            if "name" in chat and "identifier" in chat:
                # MODIFIED: Use the custom icon if it exists, otherwise use the default.
                icon_path = chat.get("icon", default_icon)
                # Ensure the custom icon path exists, otherwise fall back.
                if not os.path.exists(icon_path):
                    icon_path = default_icon

                results.append({
                    "Title": chat["name"],
                    "SubTitle": f"Open chat with identifier: {chat['identifier']}",
                    "IcoPath": icon_path,
                    # This action is for the primary action (Enter key).
                    "JsonRPCAction": {
                        "method": "open_telegram_chat",
                        "parameters": [chat["identifier"]]
                    },
                    # NEW: Add context data to be used by the context_menu method.
                    "ContextData": chat["identifier"]
                })
        
        return results

    def context_menu(self, identifier):
        """
        Creates context menu options for a selected item.
        """
        results = []
        identifier_str = str(identifier)

        if identifier_str.isdigit() and not identifier_str.startswith('-'):
            results.append({
                "Title": "Open Profile",
                "SubTitle": f"Show profile for user ID: {identifier_str}",
                "IcoPath": os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png"),
                "JsonRPCAction": {
                    "method": "open_telegram_profile",
                    "parameters": [identifier_str]
                }
            })
        
        return results

    def open_telegram_chat(self, identifier):
        """
        Constructs the chat URL and opens it.
        """
        identifier_str = str(identifier)
        if identifier_str.lstrip('-').isdigit():
            url = f"tg://openmessage?user_id={identifier_str}"
        else:
            url = f"tg://resolve?domain={identifier_str}"
        webbrowser.open(url)

    def open_telegram_profile(self, identifier):
        """
        Constructs the profile URL and opens it.
        """
        url = f"tg://user?id={identifier}"
        webbrowser.open(url)


if __name__ == "__main__":
    Telegram()