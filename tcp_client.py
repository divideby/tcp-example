#!/usr/bin/env python3
import socket
import struct
import time
import random
import sys

class TCPPacket:
    def __init__(self):
        self.src_port = random.randint(30000, 60000)
        self.dst_port = 8888
        self.seq_num = random.randint(0, 2**32 - 1)
        self.ack_num = 0
        self.data_offset = 5  # 5 * 4 = 20 bytes (minimum TCP header)
        self.flags = 0
        self.window = 65535
        self.checksum = 0
        self.urgent_ptr = 0
        self.data = b''
        
    def set_flags(self, fin=0, syn=0, rst=0, psh=0, ack=0, urg=0):
        self.flags = (urg << 5) | (ack << 4) | (psh << 3) | (rst << 2) | (syn << 1) | fin
        
    def build_packet(self, src_ip, dst_ip):
        # TCP header fields
        tcp_header = struct.pack('!HHLLBBHHH',
            self.src_port,      # Source port
            self.dst_port,      # Destination port
            self.seq_num,       # Sequence number
            self.ack_num,       # Acknowledgment number
            (self.data_offset << 4) | 0,  # Data offset and reserved
            self.flags,         # Flags
            self.window,        # Window size
            0,                  # Checksum (calculated later)
            self.urgent_ptr     # Urgent pointer
        )
        
        # Calculate checksum
        pseudo_header = struct.pack('!4s4sBBH',
            socket.inet_aton(src_ip),
            socket.inet_aton(dst_ip),
            0,
            socket.IPPROTO_TCP,
            len(tcp_header) + len(self.data)
        )
        
        pseudo_packet = pseudo_header + tcp_header + self.data
        self.checksum = self.calculate_checksum(pseudo_packet)
        
        # Rebuild header with checksum
        tcp_header = struct.pack('!HHLLBBHHH',
            self.src_port,
            self.dst_port,
            self.seq_num,
            self.ack_num,
            (self.data_offset << 4) | 0,
            self.flags,
            self.window,
            self.checksum,
            self.urgent_ptr
        )
        
        return tcp_header + self.data
    
    def calculate_checksum(self, data):
        if len(data) % 2:
            data += b'\0'
        
        s = 0
        for i in range(0, len(data), 2):
            w = (data[i] << 8) + data[i + 1]
            s = s + w
            
        s = (s >> 16) + (s & 0xffff)
        s = s + (s >> 16)
        s = ~s & 0xffff
        
        return s

class TCPClient:
    def __init__(self, dst_ip, dst_port):
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.src_ip = self.get_local_ip()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        self.sock.setsockopt(socket.SOL_IP, socket.IP_HDRINCL, 1)
        self.sock.settimeout(5)
        
        # Connection state
        self.state = "CLOSED"
        self.seq_num = random.randint(0, 2**32 - 1)
        self.ack_num = 0
        self.src_port = random.randint(30000, 60000)
        
    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect((self.dst_ip, 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip
    
    def build_ip_header(self, payload_len):
        # IP header fields
        version = 4
        ihl = 5
        tos = 0
        tot_len = 20 + payload_len
        id = random.randint(0, 65535)
        frag_off = 0
        ttl = 64
        protocol = socket.IPPROTO_TCP
        check = 0
        saddr = socket.inet_aton(self.src_ip)
        daddr = socket.inet_aton(self.dst_ip)
        
        version_ihl = (version << 4) + ihl
        
        ip_header = struct.pack('!BBHHHBBH4s4s',
            version_ihl,
            tos,
            tot_len,
            id,
            frag_off,
            ttl,
            protocol,
            check,
            saddr,
            daddr
        )
        
        return ip_header
    
    def send_packet(self, packet):
        tcp_packet = packet.build_packet(self.src_ip, self.dst_ip)
        ip_header = self.build_ip_header(len(tcp_packet))
        
        full_packet = ip_header + tcp_packet
        self.sock.sendto(full_packet, (self.dst_ip, 0))
        
    def receive_packet(self):
        try:
            data, addr = self.sock.recvfrom(65535)
            
            # Parse IP header
            ip_header_len = (data[0] & 0xF) * 4
            tcp_header_start = ip_header_len
            
            # Parse TCP header
            tcp_header = data[tcp_header_start:tcp_header_start + 20]
            unpacked = struct.unpack('!HHLLBBHHH', tcp_header)
            
            src_port = unpacked[0]
            dst_port = unpacked[1]
            seq_num = unpacked[2]
            ack_num = unpacked[3]
            flags = unpacked[5]
            
            # Check if this packet is for us
            if dst_port == self.src_port and src_port == self.dst_port:
                return {
                    'seq': seq_num,
                    'ack': ack_num,
                    'flags': flags,
                    'syn': bool(flags & 0x02),
                    'ack_flag': bool(flags & 0x10),
                    'fin': bool(flags & 0x01),
                    'psh': bool(flags & 0x08)
                }
        except socket.timeout:
            pass
        return None
    
    def perform_handshake(self):
        print(f"[*] Starting TCP handshake with {self.dst_ip}:{self.dst_port}")
        
        # Step 1: Send SYN
        syn_packet = TCPPacket()
        syn_packet.src_port = self.src_port
        syn_packet.dst_port = self.dst_port
        syn_packet.seq_num = self.seq_num
        syn_packet.set_flags(syn=1)
        
        print(f"[>] Sending SYN (seq={self.seq_num})")
        self.send_packet(syn_packet)
        
        # Step 2: Receive SYN-ACK
        print("[*] Waiting for SYN-ACK...")
        start_time = time.time()
        while time.time() - start_time < 5:
            response = self.receive_packet()
            if response and response['syn'] and response['ack_flag']:
                print(f"[<] Received SYN-ACK (seq={response['seq']}, ack={response['ack']})")
                self.ack_num = response['seq'] + 1
                self.seq_num = response['ack']
                break
        else:
            print("[-] Timeout waiting for SYN-ACK")
            return False
        
        # Step 3: Send ACK
        ack_packet = TCPPacket()
        ack_packet.src_port = self.src_port
        ack_packet.dst_port = self.dst_port
        ack_packet.seq_num = self.seq_num
        ack_packet.ack_num = self.ack_num
        ack_packet.set_flags(ack=1)
        
        print(f"[>] Sending ACK (seq={self.seq_num}, ack={self.ack_num})")
        self.send_packet(ack_packet)
        
        self.state = "ESTABLISHED"
        print("[+] TCP connection established!")
        return True
    
    def send_data(self, data):
        if self.state != "ESTABLISHED":
            print("[-] Connection not established")
            return False
            
        data_packet = TCPPacket()
        data_packet.src_port = self.src_port
        data_packet.dst_port = self.dst_port
        data_packet.seq_num = self.seq_num
        data_packet.ack_num = self.ack_num
        data_packet.set_flags(ack=1, psh=1)
        data_packet.data = data.encode() if isinstance(data, str) else data
        
        print(f"[>] Sending data: {data}")
        self.send_packet(data_packet)
        
        self.seq_num += len(data_packet.data)
        return True
    
    def close(self):
        if self.sock:
            self.sock.close()

def main():
    if len(sys.argv) > 1:
        dst_ip = sys.argv[1]
    else:
        dst_ip = "127.0.0.1"
    
    client = TCPClient(dst_ip, 8888)
    
    try:
        if client.perform_handshake():
            time.sleep(0.5)  # Small delay to ensure connection is ready
            
            # Send some test data
            client.send_data("Hello from custom TCP client!")
            time.sleep(0.5)
            
            client.send_data("This is a test message")
            time.sleep(0.5)
            
            print("[*] Data sent successfully")
    except Exception as e:
        print(f"[-] Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    main()