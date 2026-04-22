import socket
import os
import sys

PORT = 8080
BUFFER_SIZE = 4096
EOF_MARKER = b"<--EOF-->"

def run_client(server_ip):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((server_ip, PORT))
        print(f"Connected to {server_ip}")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    print("\n--- Cloud File System Ready ---")
    print("Commands: LIST, MKDIR <name>, WRITE <file>, READ <file>, EXIT\n")
    
    while True:
        user_input = input("cloud-fs> ").strip()
        if not user_input: continue
        
        parts = user_input.split(maxsplit=1)
        cmd = parts[0].upper()
        
        if cmd == "EXIT":
            client.sendall(b"EXIT")
            break

        elif cmd == "LIST":
            client.sendall(b"LIST")
            full_response = b""
            while True:
                chunk = client.recv(BUFFER_SIZE)
                full_response += chunk
                if EOF_MARKER in full_response:
                    print("\n--- Files on Server ---")
                    print(full_response.replace(EOF_MARKER, b"").decode('utf-8'))
                    break

        elif cmd == "MKDIR" and len(parts) > 1:
            client.sendall(user_input.encode('utf-8'))
            response = client.recv(BUFFER_SIZE).decode('utf-8')
            print(response)

        elif cmd == "WRITE" and len(parts) > 1:
            filename = parts[1]
            
            # --- THE FIX: AUTO-CREATE FILE IF MISSING ---
            if not os.path.exists(filename):
                print(f"Local file '{filename}' not found. Creating a sample version for you...")
                with open(filename, 'w') as f:
                    f.write(f"Sample content for {filename}\nCreated by Cloud-FS Client.")
            
            client.sendall(user_input.encode('utf-8'))
            status = client.recv(BUFFER_SIZE).decode('utf-8')
            
            if status == "READY":
                print(f"Uploading {filename}...")
                with open(filename, 'rb') as f:
                    while (chunk := f.read(BUFFER_SIZE)):
                        client.sendall(chunk)
                # Small pause to ensure TCP buffer separation
                import time
                time.sleep(0.1)
                client.sendall(EOF_MARKER)
                print("Upload complete.")

        elif cmd == "READ" and len(parts) > 1:
            client.sendall(user_input.encode('utf-8'))
            filename = parts[1]
            status = client.recv(5).decode('utf-8')
            if status == "OK":
                with open(filename, 'wb') as f:
                    while True:
                        chunk = client.recv(BUFFER_SIZE)
                        if EOF_MARKER in chunk:
                            f.write(chunk.replace(EOF_MARKER, b""))
                            break
                        f.write(chunk)
                print(f"Download complete: {filename} saved locally.")
            else:
                print("Error: File not found on server.")
        
        else:
            print("Invalid command or missing argument.")

    client.close()

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    run_client(ip)