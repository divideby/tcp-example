#!/usr/bin/env python3
import socket

def main():
    HOST = '127.0.0.1'
    PORT = 8888
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[*] Server listening on {HOST}:{PORT}")
        
        while True:
            client_socket, addr = server_socket.accept()
            print(f"[+] Connection from {addr[0]}:{addr[1]}")
            
            try:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    
                    print(f"[>] Received {len(data)} bytes:")
                    print(f"    Raw bytes: {data}")
                    print(f"    Hex: {data.hex()}")
                    try:
                        print(f"    Text: {data.decode('utf-8', errors='replace')}")
                    except UnicodeDecodeError:
                        pass
                    
            except Exception as e:
                print(f"[-] Error: {e}")
            finally:
                client_socket.close()
                print(f"[-] Connection closed from {addr[0]}:{addr[1]}")
                
    except KeyboardInterrupt:
        print("\n[!] Server shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()