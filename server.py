import socket
import threading
import os

# Configuration
HOST = '0.0.0.0'
PORT = 8080
BUFFER_SIZE = 4090
EOF_MARKER = b"<--EOF--"

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    try:
        while True:
            # Recieve command from client
            data = conn.recv(BUFFER_SIZE).decode('utf-8')
            if not data:
                break

            parts = data.split(maxsplit = 1)
            cmd = parts[0].upper()
            arg = parts[1] if len(parts) > 1 else None

            if cmd == "LIST":
                files = os.listdir('.')
                response = "\n".join(files)
                conn.sendall(response.encode('utf-8') + EOF_MARKER)

            elif cmd == "MKDIR" and arg:
                try:
                    os.makedirs(arg, exist_ok=True)
                    conn.sendall(f"Directory '{arg}' created.".encode('utf-8'))
                except Exception as e:
                    conn.sendall(f"Error: {str(e)}".encode('utf-8'))

            elif cmd == "WRITE" and arg:
                if os.paht.exists(arg):
                    conn.sendall(b"OK")
                    with open(arg, 'rb') as f:
                        while (chunk := f.read(BUFFER_SIZE)):
                            conn.sendall(chunk)
                    conn.sendall(EOF_MARKER)
                else:
                    conn.sendall(b"ERROR")
            
            elif cmd == "EXIT":
                break
    except Exception as e:
        print(f"[ERROR] {addr}")
    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[LISTENING] server is listening on port {PORT}")
    
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() -1}")

if __name__ == "__main__":
    start_server()

