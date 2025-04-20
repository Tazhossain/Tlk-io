import telebot
import requests
import json
import time
import threading
import re
import random
from datetime import datetime
import sys
import os
import platform
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", 0))
DEFAULT_ROOM = os.getenv("DEFAULT_ROOM", "lovezone")
DEFAULT_NICKNAME = os.getenv("DEFAULT_NICKNAME", "Tom")

# Made by Taz
# Telegram: @modsbytaz
# Contact: @TazChatBot

bot = telebot.TeleBot(BOT_TOKEN)

active_chats = {}

class TlkioChat:
    def __init__(self, room_name, nickname, chat_id):
        self.room_name = room_name
        self.nickname = nickname
        self.telegram_chat_id = chat_id
        self.chat_id = None
        self.last_msg_id = 0
        self.running = True
        self.session = requests.Session()
        self.csrf_token = None
        self.listener_thread = None
        
    def get_chat_id(self):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            room_page = self.session.get(f'https://tlk.io/{self.room_name}', headers=headers)
            chat_id_match = re.search(r"chat_id\s*=\s*'(\d+)'", room_page.text)
            if chat_id_match:
                csrf_match = re.search(r'<meta content="(.*?)" name="csrf-token"', room_page.text)
                if csrf_match:
                    self.csrf_token = csrf_match.group(1)
                return chat_id_match.group(1)
            
            response = self.session.get(f'https://tlk.io/api/rooms/{self.room_name}')
            if response.status_code == 200:
                data = response.json()
                return data.get('id')
            else:
                bot.send_message(self.telegram_chat_id, f"Failed to get room info: {response.status_code}")
                return None
        except Exception as e:
            bot.send_message(self.telegram_chat_id, f"Error getting chat ID: {e}")
            return None
    
    def get_messages(self):
        try:
            if not self.chat_id:
                return []
                
            response = self.session.get(f'https://tlk.io/api/chats/{self.chat_id}/messages')
            if response.status_code == 200:
                return response.json()
            else:
                bot.send_message(self.telegram_chat_id, f"Failed to get messages: {response.status_code}")
                return []
        except Exception as e:
            bot.send_message(self.telegram_chat_id, f"Error getting messages: {e}")
            return []
    
    def search_image(self, query):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            search_url = f"https://www.google.com/search?q={query}&tbm=isch"
            response = self.session.get(search_url, headers=headers)
            cdn_pattern = r'https://[^"]*cdn[^"]*\.(jpg|jpeg|png|gif)'
            image_urls = re.findall(cdn_pattern, response.text)
            
            full_urls = []
            for ext in image_urls:
                pattern = r'https://[^"]*cdn[^"]*\.' + re.escape(ext)
                matches = re.findall(pattern, response.text)
                full_urls.extend(matches)
            
            return random.choice(full_urls) if full_urls else None
            
        except Exception as e:
            bot.send_message(self.telegram_chat_id, f"Error searching for images: {e}")
            return None
            
    def fallback_image_search(self, query):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            search_url = f"https://www.google.com/search?q={query}+cdn+image&tbm=isch"
            response = self.session.get(search_url, headers=headers)
            pattern = r'(https://[^"]*cdn[^"]*\.(jpg|jpeg|png|gif))'
            matches = re.findall(pattern, response.text)
            if matches:
                urls = [match[0] for match in matches]
                return random.choice(urls)
            return "No CDN image found"
        except Exception:
            return "No CDN image found"
            
    def send_message(self, message):
        if not message.strip() or not self.chat_id:
            return False
            
        try:
            data = {"body": message}
            headers = {
                'Content-Type': 'application/json',
                'Referer': f'https://tlk.io/{self.room_name}',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://tlk.io',
                'Accept': 'application/json, text/javascript, */*; q=0.01'
            }
            
            if not self.csrf_token:
                room_page = self.session.get(f'https://tlk.io/{self.room_name}')
                csrf_match = re.search(r'<meta content="(.*?)" name="csrf-token"', room_page.text)
                if csrf_match:
                    self.csrf_token = csrf_match.group(1)
            
            if self.csrf_token:
                headers['X-CSRF-Token'] = self.csrf_token
                
            response = self.session.post(
                f'https://tlk.io/api/chats/{self.chat_id}/messages', 
                json=data,
                headers=headers
            )
            
            if response.status_code == 200:
                return True
            else:
                bot.send_message(self.telegram_chat_id, f"Failed to send message: {response.status_code}")
                if response.status_code == 422:
                    self.csrf_token = None
                return False
        except Exception as e:
            bot.send_message(self.telegram_chat_id, f"Error sending message: {e}")
            return False
    
    def register_nickname(self):
        try:
            data = {
                "nickname": self.nickname,
                "provider": "anonymous"
            }
            headers = {
                'Content-Type': 'application/json',
                'Referer': f'https://tlk.io/{self.room_name}',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://tlk.io',
                'Accept': 'application/json, text/javascript, */*; q=0.01'
            }
            
            if not self.csrf_token:
                room_page = self.session.get(f'https://tlk.io/{self.room_name}')
                csrf_match = re.search(r'<meta content="(.*?)" name="csrf-token"', room_page.text)
                if csrf_match:
                    self.csrf_token = csrf_match.group(1)
            
            if self.csrf_token:
                headers['X-CSRF-Token'] = self.csrf_token
            
            response = self.session.post(
                f'https://tlk.io/api/participant', 
                json=data,
                headers=headers
            )
            
            if response.status_code == 200:
                return True
            else:
                bot.send_message(self.telegram_chat_id, f"Failed to register nickname: {response.status_code}")
                return False
        except Exception as e:
            bot.send_message(self.telegram_chat_id, f"Error registering nickname: {e}")
            return False
    
    def process_markdown_commands(self, message):
        if message.startswith('.b '):
            return f"__{message[3:]}__"
        elif message.startswith('.i '):
            return f"_{message[3:]}_"
        elif message.startswith('.c '):
            return f"`{message[3:]}`"
        elif message.startswith('.st '):
            return f"~~{message[4:]}~~"
        elif message.startswith('.l '):
            return f"* {message[3:]}"
        elif message.startswith('.q '):
            return f"> {message[3:]}"
        elif message.startswith('.hr'):
            return "---"
        elif message.startswith('.s '):
            query = message[3:]
            image_url = self.search_image(query)
            if image_url:
                return image_url
            else:
                return self.fallback_image_search(query)
        else:
            return message
            
    def message_listener(self):
        while self.running:
            messages = self.get_messages()
            
            for msg in messages:
                msg_id = msg.get('id', 0)
                if msg_id > self.last_msg_id:
                    self.last_msg_id = msg_id
                    nickname = msg.get('nickname', 'Unknown')
                    if nickname == self.nickname:
                        continue
                    
                    body = msg.get('body', '')
                    body = re.sub(r'<[^>]*>', '', body)
                    
                    formatted_message = f"{nickname}: {body}"
                    bot.send_message(self.telegram_chat_id, formatted_message)
            
            time.sleep(1)
    
    def start(self):
        self.chat_id = self.get_chat_id()
        if not self.chat_id:
            bot.send_message(self.telegram_chat_id, "Failed to get chat ID. Could not connect to tlk.io.")
            return False
        
        if not self.register_nickname():
            bot.send_message(self.telegram_chat_id, "Failed to register nickname. Using default.")
        
        messages = self.get_messages()
        if messages:
            self.last_msg_id = max([msg.get('id', 0) for msg in messages])
        
        welcome_message = f"Welcome to {self.room_name} as {self.nickname}!\n\n"
        welcome_message += "Available Markdown Commands:\n"
        welcome_message += ".b text - Bold\n"
        welcome_message += ".i text - Italic\n"
        welcome_message += ".c text - Code\n"
        welcome_message += ".st text - Strikethrough\n"
        welcome_message += ".l text - List item\n"
        welcome_message += ".q text - Quote\n"
        welcome_message += ".hr - Horizontal line\n"
        welcome_message += ".s query - Search image\n\n"
        welcome_message += "Type /stop to disconnect from the room."
        
        bot.send_message(self.telegram_chat_id, welcome_message)
        
        self.listener_thread = threading.Thread(target=self.message_listener)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        
        return True
        
    def stop(self):
        self.running = False
        if self.listener_thread:
            self.listener_thread.join(timeout=1)
        return True

def is_owner(message):
    return message.from_user.id == OWNER_ID

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not is_owner(message):
        return
        
    bot.reply_to(message, "Welcome to Tlk-io Bot! Made by Taz\n\n"
                         "Commands:\n"
                         "/join roomname nickname - Join to a room\n"
                         "/stop - Disconnect from current room\n"
                         "/help - Show this help message")

@bot.message_handler(commands=['join'])
def join_command(message):
    if not is_owner(message):
        return
        
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if len(args) >= 2:
        room = args[0]
        nickname = args[1]
    elif len(args) == 1:
        room = args[0]
        nickname = DEFAULT_NICKNAME
    else:
        room = DEFAULT_ROOM
        nickname = DEFAULT_NICKNAME
    
    chat_id = message.chat.id
    
    if chat_id in active_chats:
        bot.reply_to(message, "Already connected to a room. Use /stop to disconnect first.")
        return
    
    tlkio_client = TlkioChat(room, nickname, chat_id)
    if tlkio_client.start():
        active_chats[chat_id] = tlkio_client
    else:
        bot.reply_to(message, "Failed to connect.")

@bot.message_handler(commands=['stop'])
def stop_command(message):
    if not is_owner(message):
        return
        
    chat_id = message.chat.id
    
    if chat_id in active_chats:
        active_chats[chat_id].stop()
        del active_chats[chat_id]
        bot.send_message(chat_id, "Disconnected from tlk.io room.")
    else:
        bot.reply_to(message, "Not connected to any room.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if not is_owner(message):
        return
        
    chat_id = message.chat.id
    
    if chat_id in active_chats:
        client = active_chats[chat_id]
        processed_message = client.process_markdown_commands(message.text)
        if client.send_message(processed_message):
            pass
        else:
            bot.reply_to(message, "Failed to send message to tlk.io")
    else:
        bot.reply_to(message, "Not connected to any tlk.io room. Use /join roomname nickname to connect.")

if __name__ == "__main__":
    print("Bot is running...")
    bot.polling(none_stop=True)
