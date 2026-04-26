#!/usr/bin/env python3
import os
import sys
import json
import re
import urllib.request
import urllib.parse
import mimetypes

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(BASE_DIR, "system", "config", "trello_config.json")
LEDGER_PATH = os.path.join(BASE_DIR, "5. Trackers", ".trello_ledger.json")
TASK_MASTER_PATH = os.path.join(BASE_DIR, "5. Trackers", "TASK_MASTER.md")

class TrelloAPI:
    def __init__(self):
        if not os.path.exists(CONFIG_PATH):
            print(f"❌ Error: Trello configuration missing at {CONFIG_PATH}")
            print("Please copy trello_config.template.json to trello_config.json and fill it out.")
            sys.exit(1)
        
        with open(CONFIG_PATH, "r") as f:
            self.config = json.load(f)
            
        self.api_key = self.config["api_key"]
        self.token = self.config["token"]
        self.board_id = self.config["board_id"]
        self.list_mapping = self.config.get("list_mapping", {})
        
        # Reverse mapping: list id -> status symbol
        self.reverse_mapping = {v: k for k, v in self.list_mapping.items() if v}

    def _request(self, method, url, data=None):
        full_url = f"{url}?key={self.api_key}&token={self.token}"
        headers = {}
        encoded_data = None
        
        if data:
            if isinstance(data, dict):
                full_url += "&" + urllib.parse.urlencode(data)
            else:
                encoded_data = data
                
        req = urllib.request.Request(full_url, data=encoded_data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP Error {e.code} on {url}: {e.read().decode('utf-8')}")
            return None
        except Exception as e:
            print(f"❌ Request Error: {e}")
            return None
            
    def get_cards(self):
        url = f"https://api.trello.com/1/boards/{self.board_id}/cards"
        return self._request("GET", url)
        
    def create_card(self, list_id, name, desc):
        url = "https://api.trello.com/1/cards"
        data = {"idList": list_id, "name": name, "desc": desc}
        return self._request("POST", url, data)
        
    def update_card(self, card_id, **kwargs):
        url = f"https://api.trello.com/1/cards/{card_id}"
        return self._request("PUT", url, kwargs)

    def attach_file(self, card_id, filepath):
        import uuid
        url = f"https://api.trello.com/1/cards/{card_id}/attachments?key={self.api_key}&token={self.token}"
        boundary = uuid.uuid4().hex
        headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}
        
        filename = os.path.basename(filepath)
        mime_type = mimetypes.guess_type(filepath)[0] or 'application/octet-stream'
        
        with open(filepath, 'rb') as f:
            file_content = f.read()

        body = (
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode('utf-8') + file_content + f"\r\n--{boundary}--\r\n".encode('utf-8')

        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            res = urllib.request.urlopen(req)
            return json.loads(res.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            print(f"❌ Attachment Error {e.code}: {e.read().decode('utf-8')}")
            return None


def sync_trello():
    print("🔄 Starting Beats PM <-> Trello Sync")
    api = TrelloAPI()
    
    # Load Ledger
    ledger = {}
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, "r") as f:
            ledger = json.load(f)
            
    # Load Trello Cards
    trello_cards = api.get_cards()
    if trello_cards is None:
        return
        
    # Build maps for local comparisons
    card_by_id = {c['id']: c for c in trello_cards}
    # Link manually created cards via [ID] in title
    for c in trello_cards:
        match = re.search(r'\[([^\]]+)\]', c['name'])
        if match:
            task_id = match.group(1)
            if task_id not in ledger:
                ledger[task_id] = c['id']

    # Parse TASK_MASTER.md
    with open(TASK_MASTER_PATH, "r") as f:
        lines = f.readlines()
        
    updated_lines = []
    changes_made = False
    
    # Simple regex to extract Status Icon natively used in Beats
    def get_status_icon(text):
        for icon in ["🔴", "🟡", "✅", "⬜", "⏸️"]:
            if icon in text:
                return icon
        return "🔴" # Default to unstarted
        
    in_table = False
    for i, line in enumerate(lines):
        if line.strip().startswith("| ID |") or line.strip().startswith("|:---|"):
            updated_lines.append(line)
            continue
            
        if line.strip().startswith("|") and len(line.split("|")) >= 6:
            parts = line.split("|")
            task_id = parts[1].strip()
            task_name = re.sub(r'\*\*', '', parts[2].strip()) # strip bolding 
            status_cell = parts[5].strip()
            local_icon = get_status_icon(status_cell)
            
            # 1. Evaluate Sync Actions
            if task_id in ledger and ledger[task_id] in card_by_id:
                t_card = card_by_id[ledger[task_id]]
                t_list_id = t_card['idList']
                
                # Compare Trello List to Local Status
                trello_implied_icon = api.reverse_mapping.get(t_list_id)
                local_implied_list = api.list_mapping.get(local_icon)
                
                if trello_implied_icon and trello_implied_icon != local_icon:
                    # Trello list is different. Let's pull from Trello as source of truth for status.
                    print(f"📥 Pulling status for {task_id}: {local_icon} -> {trello_implied_icon}")
                    new_status_cell = status_cell.replace(local_icon, trello_implied_icon)
                    parts[5] = f" {new_status_cell} "
                    line = "|".join(parts)
                    changes_made = True
                elif local_implied_list and t_list_id != local_implied_list:
                    # Push from Local to Trello
                    print(f"📤 Pushing status for {task_id} to list {local_implied_list}")
                    api.update_card(t_card['id'], idList=local_implied_list)
            else:
                # Need to create card
                print(f"✨ Creating card for {task_id}")
                target_list = api.list_mapping.get(local_icon, list(api.list_mapping.values())[0])
                if target_list:
                    desc = f"Managed via Beats PM Kit\\nTask ID: {task_id}"
                    new_card = api.create_card(target_list, f"[{task_id}] {task_name}", desc)
                    if new_card:
                        ledger[task_id] = new_card['id']
                        
        updated_lines.append(line)
        
    if changes_made:
        with open(TASK_MASTER_PATH, "w") as f:
            f.writelines(updated_lines)
            
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2)
        
    print("✅ Sync complete!")

def attach_to_task(task_id, filepath):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return
        
    ledger = {}
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, "r") as f:
            ledger = json.load(f)
            
    if task_id not in ledger:
        print(f"❌ {task_id} not found in Trello ledger. Run sync first.")
        return
        
    api = TrelloAPI()
    print(f"📎 Attaching {os.path.basename(filepath)} to {task_id}...")
    res = api.attach_file(ledger[task_id], filepath)
    if res:
        print("✅ Attachment successful!")
    else:
        print("❌ Attachment failed.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "attach" and len(sys.argv) == 4:
            attach_to_task(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == "sync":
            sync_trello()
        else:
            print("Usage: trello_bridge.py sync | attach <task_id> <filepath>")
    else:
        sync_trello()
