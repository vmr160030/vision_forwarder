# Example: command_receiver_forwarder.py
import socket
import threading
import struct

LISTEN_PORT = 9876
FORWARD_HOST = '128.95.10.228'  # Replace with actual destination
FORWARD_PORT = 9100                      # Replace with actual port

RUN_SPIKE_FINDING = 34

def handle_client(client_sock, addr):
    try:
        # Read 4 bytes as an integer command (big-endian)
        data = client_sock.recv(4)
        if len(data) < 4:
            print("Incomplete command received")
            client_sock.close()
            return
        command = struct.unpack('>i', data)[0]
        print(f"Command {command} received from {addr}")

        # Dummy acknowledgment
        client_sock.sendall(b'\x01')

        if command == RUN_SPIKE_FINDING:
            # Connect to the forward destination
            with socket.create_connection((FORWARD_HOST, FORWARD_PORT)) as forward_sock:
                print(f"Forwarding data to {FORWARD_HOST}:{FORWARD_PORT}")
                # Forward the rest of the data stream
                while True:
                    chunk = client_sock.recv(4096)
                    if not chunk:
                        break
                    forward_sock.sendall(chunk)
            print("Forwarding complete.")
        else:
            print(f"Unknown command {command}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_sock.close()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind(('', LISTEN_PORT))
        server_sock.listen()
        print(f"Listening for commands on port {LISTEN_PORT}...")
        while True:
            client_sock, addr = server_sock.accept()
            print(f"Connection from {addr}")
            threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True).start()

if __name__ == "__main__":
    main()