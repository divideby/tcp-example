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
- `test_server.py` - Standard TCP server (won't show data from raw client)
- `raw_server.py` - Raw socket server that can display packets from the custom client

## Requirements

- Python 3.x
- Linux/Unix system (for raw socket support)
- Root/sudo privileges (required for raw socket operations)

## How to Run

To see the data from the custom TCP client, use the raw server:

1. Start the raw server:
```bash
sudo python3 raw_server.py
```

2. Run the TCP client:
```bash
sudo python3 tcp_client.py
```

Alternatively, to test with standard TCP:
```bash
# Terminal 1
sudo python3 test_server.py

# Terminal 2 - use netcat or telnet
echo "Hello" | nc localhost 8888
```

## How It Works

The TCP client manually constructs packets with:
- TCP headers (ports, sequence numbers, flags, checksum)
- IP headers for raw socket transmission
- Proper three-way handshake sequence
- Data packets after connection establishment

## Why Two Servers?

- `test_server.py` - Uses standard sockets, good for normal TCP testing but can't see raw packet data
- `raw_server.py` - Uses raw sockets to capture and display all TCP packets including those from our custom client

This demonstrates the difference between OS-managed TCP connections and raw packet handling.