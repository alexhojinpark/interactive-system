from pythonosc import udp_client
import time


class OscSender:
    def __init__(self, ip="127.0.0.1", port=8000, rate_limit=30):
        """
        Class for OSC message sending
        
        Parameters:
            ip (str): Server IP address 대상 서버의 IP 주소 (Default: localhost)
            port (int): Server port number (Default: 8000)
            rate_limit (int): send message per second
        """
        self.client = udp_client.SimpleUDPClient(ip, port)
        self.rate_limit = rate_limit
        self.min_interval = 1.0 / rate_limit if rate_limit > 0 else 0
        self.last_sent_time = 0
        self.last_sent_value = None
        
        self.message_count = 0
        self.start_time = time.time()
    
    def send_mouth_value(self, value, force=False):
        """
        send mouth open ratio for OSC
        
        Parameters:
            value (int): (0-127)
            force (bool): force sending
            
        Returns:
            bool: message sent status
        """
        current_time = time.time()
        
        if self.last_sent_value == value and not force:
            return False
            
        if (current_time - self.last_sent_time < self.min_interval) and not force:
            return False
            
        self.client.send_message("/mouth", value)
        
        self.last_sent_time = current_time
        self.last_sent_value = value
        self.message_count += 1
        
        return True
    
    def get_statistics(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            msg_per_second = self.message_count / elapsed_time
        else:
            msg_per_second = 0
            
        return {
            "total_messages": self.message_count,
            "elapsed_time": elapsed_time,
            "messages_per_second": msg_per_second,
            "last_value": self.last_sent_value
        }
    
    def reset_statistics(self):
        self.message_count = 0
        self.start_time = time.time()