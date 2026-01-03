
import pywhatkit as kit
import webbrowser
import logging
import time
from config import WHATSAPP_NUMBER

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppSender:
    def __init__(self):
        self.phone_number = f"+{WHATSAPP_NUMBER}" if not WHATSAPP_NUMBER.startswith("+") else WHATSAPP_NUMBER
    
    def login_whatsapp(self):
        """First time login helper."""
        print("\n--- WhatsApp Web Login ---")
        print("1. Browser opening...")
        print("2. Scan QR code via Phone Linked Devices")
        print("3. Wait for chats to load, then close this script.")
        webbrowser.open("https://web.whatsapp.com")
    
    def send_message(self, message: str, phone_number: str = None) -> bool:
        """Send message using PyWhatKit instant (best effort)."""
        target = phone_number or self.phone_number
        if not target.startswith("+"): target = f"+{target}"
        
        try:
            logger.info(f"📱 Sending to {target}...")
            # wait_time=20 allows Web to load, close_time=3 closes tab after send
            kit.sendwhatmsg_instantly(target, message, wait_time=20, tab_close=True, close_time=3)
            logger.info("✅ Send command issued.")
            return True
        except Exception as e:
            logger.error(f"❌ Send failed: {e}")
            return False
    
    def send_long_message(self, message: str, phone_number: str = None) -> bool:
        return self.send_message(message, phone_number)

if __name__ == "__main__":
    sender = WhatsAppSender()
    print(f"Target: {sender.phone_number}")
    opt = input("1: Login, 2: Test Send\n> ")
    if opt == "1": sender.login_whatsapp()
    elif opt == "2": sender.send_message("Test Message")
