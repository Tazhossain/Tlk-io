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

DEFAULT_ROOM = "lovezone"
DEFAULT_NICKNAME = "Tom"

# Made by Taz
# Telegram: @modsbytaz
# Contact: @TazChatBot

class TlkioChat:
    def __init__(self, room_name, nickname):
        self.room_name = room_name
        self.nickname = nickname
        self.chat_id = None
        self.last_msg_id = 0
        self.running = True
        self.session = requests.Session()
        self.csrf_token = None
        
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
                print(f"Failed to get room info: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error getting chat ID: {e}")
            return None
    
    def get_messages(self):
        try:
            if not self.chat_id:
                return []
                
            response = self.session.get(f'https://tlk.io/api/chats/{self.chat_id}/messages')
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get messages: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error getting messages: {e}")
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
            print(f"Error searching for images: {e}")
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
                print(f"Failed to send message: {response.status_code}")
                if response.status_code == 422:
                    self.csrf_token = None
                return False
        except Exception as e:
            print(f"Error sending message: {e}")
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
                print(f"Failed to register nickname: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error registering nickname: {e}")
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
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"\r\033[92m{nickname}\033[0m: {body}")
                    print("\033[93m> \033[0m", end='', flush=True)
            
            time.sleep(1)
    
    def clear_screen(self):
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')
    
    def display_welcome_message(self):
        self.clear_screen()
        print(f"\033[1;36mConnected to tlk.io/{self.room_name} as {self.nickname}!\033[0m")
        print("\033[1;37mType your messages and press Enter to send.\033[0m\n")
        
        print("\033[1;33mAvailable Commands:\033[0m")
        print("\033[31m.stop\033[0m to exit.")
        print("\033[31m.leave\033[0m switch room")
        
        commands = [
            ("  \033[96m.b text\033[0m   - \033[1mBold\033[0m", 0.01),
            ("  \033[96m.i text\033[0m   - \033[3mItalic\033[0m", 0.01),
            ("  \033[96m.c text\033[0m   - \033[7mCode\033[0m", 0.01),
            ("  \033[96m.st text\033[0m  - \033[9mStrikethrough\033[0m", 0.01),
            ("  \033[96m.l text\033[0m   - \033[32mList item\033[0m", 0.01),
            ("  \033[96m.q text\033[0m   - \033[33mQuote\033[0m", 0.01),
            ("  \033[96m.hr\033[0m       - \033[34mLine\033[0m", 0.01),
            ("  \033[96m.s query\033[0m  - \033[35mSearch image\033[0m", 0.01)
        ]
        
        for cmd, delay in commands:
            print(cmd)
            time.sleep(delay)
            
    def run(self):
        print(f"Connecting to tlk.io/{self.room_name}...")
        self.chat_id = self.get_chat_id()
        if not self.chat_id:
            print("Failed to get chat ID. Could not connect to tlk.io.")
            return False
            
        print(f"Connected to room {self.room_name} (ID: {self.chat_id})")
        if not self.register_nickname():
            print("Failed to register nickname. Using default.")
        
        messages = self.get_messages()
        if messages:
            self.last_msg_id = max([msg.get('id', 0) for msg in messages])
        
        self.display_welcome_message()
        
        listener_thread = threading.Thread(target=self.message_listener)
        listener_thread.daemon = True
        listener_thread.start()
        
        try:
            while self.running:
                try:
                    message = input("\033[93m> \033[0m")
                    if message.lower() == '.stop':
                        self.running = False
                        break
                    elif message.lower() == '.leave':
                        print("\n\033[91mLeaving room...\033[0m")
                        self.running = False
                        return True
                    elif message.lower() == '.help':
                        print("\n\033[1;33mMarkdown Commands:\033[0m")
                        print("  \033[96m.b text\033[0m     - \033[1mBold text\033[0m")
                        print("  \033[96m.i text\033[0m     - \033[3mItalic text\033[0m")
                        print("  \033[96m.c text\033[0m     - \033[7mCode formatted text\033[0m")
                        print("  \033[96m.st text\033[0m    - \033[9mStrikethrough text\033[0m")
                        print("  \033[96m.l text\033[0m     - \033[32mBullet list item\033[0m")
                        print("  \033[96m.q text\033[0m     - \033[33mBlockquote text\033[0m")
                        print("  \033[96m.hr\033[0m         - \033[34mHorizontal rule\033[0m")
                        print("\n\033[1;33mImage Search Command:\033[0m")
                        print("  \033[96m.s query\033[0m    - \033[35mSearch for an image\033[0m")
                        continue
                    processed_message = self.process_markdown_commands(message)
                    self.send_message(processed_message)
                except EOFError:
                    self.running = False
                    break
                    
        except KeyboardInterrupt:
            print("\n\033[91mExiting...\033[0m")
            self.running = False
        
        if not self.running:
            print("\033[91mDisconnected from tlk.io\033[0m")
        
        return False

def prompt_for_input():
    room = input("\033[1;36mEnter room name: \033[0m").strip()
    if not room:
        room = DEFAULT_ROOM
        
    nickname = input("\033[1;36mEnter nickname: \033[0m").strip()
    if not nickname:
        nickname = DEFAULT_NICKNAME
        
    return room, nickname

def main():
    rejoining = True
    
    while rejoining:
        room, nickname = prompt_for_input()
        client = TlkioChat(room, nickname)
        rejoining = client.run()

if __name__ == "__main__":
    main()