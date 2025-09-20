import os
import json
import asyncio
from getpass import getpass
from telethon.sync import TelegramClient
from telethon.tl.types import User, Chat, Channel
from PIL import Image, ImageDraw, ImageOps # NEW: Import Pillow library

# --- Configuration ---
# You can hardcode your API credentials here to avoid entering them every time.
# IMPORTANT: Do NOT share this file with anyone if you hardcode your credentials.
API_ID = None  # Or replace None with your API ID, 12345
API_HASH = None # Or replace None with your API Hash, "0123456789abcdef0123456789abcdef"

SESSION_NAME = "telegram_builder"
CHAT_LIMIT = None
ICONS_DIRECTORY = "profile_icons"
OUTPUT_FILENAME = "chats.json"

def round_image(image_path):
    """
    Opens an image, crops it into a circle, and saves it.
    """
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGBA")
            size = (min(img.size),) * 2
            img = ImageOps.fit(img, size, Image.Resampling.LANCZOS)

            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0) + size, fill=255)

            output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
            output.putalpha(mask)
            
            new_path = os.path.splitext(image_path)[0] + ".png"
            output.save(new_path, "PNG")

            if image_path != new_path and os.path.exists(image_path):
                os.remove(image_path)
                
            return new_path
    except Exception as e:
        print(f"    > Could not round image {image_path}: {e}")
        return image_path

async def main():
    """
    Main function to connect to Telegram, fetch all data, and build the JSON file from scratch.
    """
    print("--- Telegram Chat Exporter for Flow Launcher Plugin Telegram Openner (Coded by MA) ---")

    api_id = API_ID or input("Please enter your API ID: ")
    api_hash = API_HASH or getpass("Please enter your API Hash: ")

    if not os.path.exists(ICONS_DIRECTORY):
        os.makedirs(ICONS_DIRECTORY)
        print(f"Created directory: '{ICONS_DIRECTORY}'")

    chats_data = []

    async with TelegramClient(SESSION_NAME, api_id, api_hash) as client:
        print(f"\nPerforming a fresh scan of the latest {CHAT_LIMIT or 'all'} chats...")

        async for dialog in client.iter_dialogs(limit=CHAT_LIMIT):
            entity = dialog.entity
            name = dialog.name

            if not name or not entity:
                continue
            
            print(f"Processing: {name}")

            identifier = str(getattr(entity, 'username', None) or entity.id)

            icon_path = None
            try:
                file_path_jpg = os.path.join(ICONS_DIRECTORY, f"{identifier}.jpg")
                downloaded_path = await client.download_profile_photo(entity, file=file_path_jpg)

                if downloaded_path:
                    final_path_png = round_image(downloaded_path)
                    icon_path = os.path.abspath(final_path_png)

            except Exception as e:
                print(f"    > Could not download profile photo for {name}: {e}")

            chats_data.append({
                "name": name,
                "identifier": identifier,
                "icon": icon_path or ""
            })

    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(chats_data, f, indent=2, ensure_ascii=False)
        print(f"\n Success! '{OUTPUT_FILENAME}' created with {len(chats_data)} entries.")
        print(f"You can now copy '{OUTPUT_FILENAME}' and the '{ICONS_DIRECTORY}' folder to your plugin directory.")
    except Exception as e:
        print(f"\n Error writing to {OUTPUT_FILENAME}: {e}")


if __name__ == "__main__":
    asyncio.run(main())