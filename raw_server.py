#!/usr/bin/env python3
import socket
import struct
import threading
import time

class RawTCPServer:
    def __init__(self, port=8888):
        self.port = port
        self.connections = {}
        self.running = True
        
        # Create raw socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        
        # Also create a regular socket to participate in handshake
        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_sock.bind(('127.0.0.1', port))
        self.tcp_sock.listen(5)
        
    def parse_packet(self, data):
        # Parse IP header
        ip_header_len = (data[0] & 0xF) * 4
        
        # Parse TCP header
        tcp_header_start = ip_header_len
        tcp_header = data[tcp_header_start:tcp_header_start + 20]
        
        if len(tcp_header) < 20:
            return None
            
        unpacked = struct.unpack('!HHLLBBHHH', tcp_header)
        
        src_port = unpacked[0]
        dst_port = unpacked[1]
        seq_num = unpacked[2]
        ack_num = unpacked[3]
        data_offset = (unpacked[4] >> 4) * 4
        flags = unpacked[5]
        
        # Get flags
        syn = bool(flags & 0x02)
        ack = bool(flags & 0x10)
        psh = bool(flags & 0x08)
        
        # Get data
        tcp_data_start = ip_header_len + data_offset
        tcp_data = data[tcp_data_start:]
        
        return {
            'src_port': src_port,
            'dst_port': dst_port,
            'seq': seq_num,
            'ack': ack_num,
            'syn': syn,
            'ack_flag': ack,
            'psh': psh,
            'data': tcp_data
        }
    
    def handle_tcp_connections(self):
        """Handle regular TCP connections for handshake"""
        while self.running:
            try:
                self.tcp_sock.settimeout(0.5)
                conn, addr = self.tcp_sock.accept()
                # Just accept and close to complete handshake
                conn.close()
            except socket.timeout:
                continue
            except Exception:
                break
    
    def run(self):
        print(f"[*] Raw TCP Server listening on port {self.port}")
        print("[*] Waiting for packets...")
        
        # Start TCP handler thread
        tcp_thread = threading.Thread(target=self.handle_tcp_connections)
        tcp_thread.daemon = True
        tcp_thread.start()
        
        try:
            while self.running:
                data, addr = self.sock.recvfrom(65535)
                
                packet = self.parse_packet(data)
                if packet and packet['dst_port'] == self.port:
                    # Log packet info
                    flags = []
                    if packet['syn']: flags.append('SYN')
                    if packet['ack_flag']: flags.append('ACK')
                    if packet['psh']: flags.append('PSH')
                    
                    print(f"\n[+] Packet from port {packet['src_port']} [{','.join(flags)}]")
                    print(f"    Seq: {packet['seq']}, Ack: {packet['ack']}")
                    
                    if packet['data']:
                        print(f"[>] Data received ({len(packet['data'])} bytes):")
                        print(f"    Raw: {packet['data']}")
                        print(f"    Hex: {packet['data'].hex()}")
                        try:
                            text = packet['data'].decode('utf-8', errors='replace')
                            print(f"    Text: {text}")
                        except:
                            pass
                            
        except KeyboardInterrupt:
            print("\n[!] Server shutting down...")
        finally:
            self.running = False
            self.sock.close()
            self.tcp_sock.close()

def main():
    server = RawTCPServer()
    server.run()

if __name__ == "__main__":
    main()