import socket
import os
import sys

PORT = 8080
BUFFER_SIZE = 4096
EOF_MARKER = b"<--EOF-->"

def run_client(server_ip):
    client = socket.socket(socket.AD_INET, socket.SOCK_STREAM)
    try:
        client.connect((server_ip, PORT))
        print(f"Connected to {server_ip}")
    except Exception as e:
        print(f"Connection failed: {e}")
        return
    
    print("Commands: LIST, MKDIR <name>, WRITE <file>, READ <file>, EXIT")

    while True:
        user_input = input("cloud-fs> ").strip()
        if not user_input: continue

        parts = user_input.split(maxsplit=1)
        cmd = parts[0].upper

        #send command to server
        client.sendall(user_input.encode('utf-8'))

        if cmd == "EXIT":
            break

        elif cmd == "LIST":
            full_response = b""
            while True:
                chunk = client.recv(BUFFER_SIZE)
                full_response += chunk
                if EOF_MARKER in full_response:
                    print(full_response.replace(EOF_MARKER, b"").decode('utf-8'))
                    break
        elif cmd == "MKDIR":
            response = client.recv(BUFFER_SIZE).decode('utf-8')
            print(response)

        elif cmd == "WRITE" and len(parts) > 1:
            filename = parts[1]
            if os.path.exists(filename):
                status = client.recv(BUFFER_SIZE).decode('utf-8')
                if status == "READY":
                    with open(filename, 'rb') as f:
                        while (chunk := f.read(BUFFER_SIZE)):
                            client.sendall(chunk)
                    client.sendall(EOF_MARKER)
                    print("Upload complete.")
            else:
                print("Local file not found.")

        elif cmd == "READ" and len(parts) > 1:
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
                print("Download complete.")
            else:
                print("File not found on server.")

    client.close()

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    run_client(ip)           
