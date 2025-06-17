# Custom TCP Implementation in Python

A basic TCP protocol implementation using raw sockets in Python for educational purposes.

## Overview

This project demonstrates how TCP works at a low level by implementing:
- Manual TCP packet construction
- TCP three-way handshake (SYN, SYN-ACK, ACK)
- Basic data transmission
- Raw socket programming

## Files

- `tcp_client.py` - Custom TCP client implementation using raw sockets
- `test_server.py` - Standard TCP server for testing the client

## Requirements

- Python 3.x
- Linux/Unix system (for raw socket support)
- Root/sudo privileges (required for raw socket operations)

## How to Run

1. Start the test server (in terminal 1):
```bash
sudo python3 test_server.py
```

2. Run the TCP client (in terminal 2):
```bash
sudo python3 tcp_client.py [server_ip]
```

If no server IP is provided, it defaults to localhost (127.0.0.1).

## How It Works

### TCP Client Implementation

1. **Packet Structure**: The client manually constructs TCP packets with:
   - Source/destination ports
   - Sequence and acknowledgment numbers
   - TCP flags (SYN, ACK, PSH, etc.)
   - Checksum calculation
   - Window size

2. **Three-Way Handshake**:
   - Client sends SYN packet
   - Server responds with SYN-ACK
   - Client sends ACK to complete connection

3. **Data Transmission**: After establishing connection, the client can send data packets with proper sequence numbers.

### Test Server

A simple TCP server that:
- Listens on port 8888
- Accepts connections
- Displays received data in multiple formats (raw bytes, hex, text)

## Example Output

Server output:
```
[*] Server listening on 127.0.0.1:8888
[+] Connection from 127.0.0.1:45678
[>] Received 29 bytes:
    Raw bytes: b'Hello from custom TCP client!'
    Hex: 48656c6c6f2066726f6d20637573746f6d2054435020636c69656e7421
    Text: Hello from custom TCP client!
```

Client output:
```
[*] Starting TCP handshake with 127.0.0.1:8888
[>] Sending SYN (seq=123456789)
[<] Received SYN-ACK (seq=987654321, ack=123456790)
[>] Sending ACK (seq=123456790, ack=987654322)
[+] TCP connection established!
[>] Sending data: Hello from custom TCP client!
[*] Data sent successfully
```

## Educational Notes

This implementation is simplified for learning purposes and doesn't include:
- Congestion control
- Flow control
- Retransmission
- Full error handling
- Options handling

It demonstrates the core concepts of how TCP packets are structured and how the basic handshake works at the protocol level.