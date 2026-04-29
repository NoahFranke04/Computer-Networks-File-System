import socket      # Imports the socket module to handle network connections
import threading   # Imports threading to allow multiple clients to connect at once
import os          # Imports os to interact with the file system (directories, paths)
import shutil      # Imports shutil to perform high-level file operations like moving files

# Configuration constants
HOST = '0.0.0.0'   # Binds the server to all available network interfaces (allows remote access)
PORT = 8080        # The port number the server will listen on
BUFFER_SIZE = 4096 # The maximum number of bytes to receive in a single chunk
EOF_MARKER = b"<--EOF-->" # A custom byte string used to signal the end of a file transfer

def handle_client(conn, addr):
    # This function handles individual client connections in their own thread
    print(f"[NEW CONNECTION] {addr} connected.")
    try:
        while True: # Keep listening for commands from this client
            # Receive data from the client, up to BUFFER_SIZE bytes, and decode it to a string
            data = conn.recv(BUFFER_SIZE).decode('utf-8')
            if not data: # If no data is received, the client likely disconnected
                break
            
            # Split the received string into at most two parts: the command and the argument
            parts = data.split(maxsplit=1)
            cmd = parts[0].upper() # Capitalize the command to ensure case-insensitivity
            arg = parts[1] if len(parts) > 1 else None # The rest is the argument (if any)

            if cmd == "LIST":
                # List all files and directories in the current server directory
                files = os.listdir('.')
                # Join the list into a single string separated by newlines, or return a fallback message
                response = "\n".join(files) if files else "(Directory is empty)"
                # Send the response back to the client, followed by the EOF marker
                conn.sendall(response.encode('utf-8') + EOF_MARKER)

            elif cmd == "MKDIR" and arg:
                try:
                    # Attempt to create a directory with the provided argument name
                    os.makedirs(arg, exist_ok=True) # exist_ok=True prevents errors if it already exists
                    conn.sendall(f"Directory '{arg}' created.".encode('utf-8')) # Send success message
                except Exception as e:
                    # If it fails, send the error message back to the client
                    conn.sendall(f"Error: {str(e)}".encode('utf-8'))

            elif cmd == "WRITETEXT" and arg:
                try:
                    # Split the argument into the filename and the actual text content
                    file_parts = arg.split(maxsplit=1)
                    if len(file_parts) < 2:
                        conn.sendall(b"Error: Please provide a filename and text.")
                    else:
                        filename, content = file_parts
                        # Open the file in write mode ('w') and save the text
                        with open(filename, 'w') as f:
                            f.write(content)
                        conn.sendall(f"Text written to '{filename}' successfully.".encode('utf-8'))
                except Exception as e:
                    conn.sendall(f"Error: {str(e)}".encode('utf-8'))

            elif cmd == "MOVE" and arg:
                try:
                    # Split the argument into source path and destination path
                    paths = arg.split(maxsplit=1)
                    if len(paths) < 2:
                        conn.sendall(b"Error: Usage: MOVE <source> <destination>")
                    else:
                        src, dest = paths
                        # Use shutil to move the file or directory
                        shutil.move(src, dest)
                        conn.sendall(f"Successfully moved '{src}' to '{dest}'.".encode('utf-8'))
                except Exception as e:
                    conn.sendall(f"Error moving file: {str(e)}".encode('utf-8'))

            elif cmd == "WRITE" and arg:
                # The client wants to upload a file; tell them the server is ready to receive
                conn.sendall(b"READY") 
                # Open a new file in binary write mode ('wb')
                with open(arg, 'wb') as f:
                    while True: # Loop to receive the file in chunks
                        chunk = conn.recv(BUFFER_SIZE)
                        # Check if this chunk contains the end-of-file marker
                        if chunk.endswith(EOF_MARKER):
                            # Write everything except the marker and break the loop
                            f.write(chunk[:-len(EOF_MARKER)])
                            break
                        # Otherwise, write the chunk to the file
                        f.write(chunk)
                print(f"[FILE RECEIVED] {arg} from {addr}")

            elif cmd == "READ" and arg:
                # The client wants to download a file; check if it exists on the server
                if os.path.exists(arg):
                    conn.sendall(b"OK") # Tell the client the file exists
                    # Open the file in binary read mode ('rb')
                    with open(arg, 'rb') as f:
                        # Read the file in chunks until there's nothing left
                        while (chunk := f.read(BUFFER_SIZE)):
                            conn.sendall(chunk) # Send each chunk to the client
                    # A tiny pause ensures the last chunk and the EOF marker don't get merged improperly
                    import time
                    time.sleep(0.1)
                    conn.sendall(EOF_MARKER) # Signal that the file transfer is complete
                else:
                    # File doesn't exist, tell the client
                    conn.sendall(b"ERROR")

            elif cmd == "EXIT":
                break # Exit the loop, which will close the connection in the 'finally' block
    except Exception as e:
        print(f"[ERROR] {addr}: {e}") # Print any unexpected connection errors to the server console
    finally:
        conn.close() # Always close the connection socket when done
        print(f"[DISCONNECTED] {addr}")

def start_server():
    # Create a TCP socket (IPv4, Stream)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to our designated IP and port
    server.bind((HOST, PORT))
    # Start listening for incoming connections
    server.listen()
    print(f"[LISTENING] Server is listening on port {PORT}")
    
    while True:
        # Accept a new client connection (this blocks until someone connects)
        conn, addr = server.accept()
        # Create a new thread for this client so the server can handle multiple people at once
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start() # Start the thread
        # Print how many active clients are connected (subtract 1 for the main server thread)
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

# Standard Python idiom to only run the server if this file is executed directly
if __name__ == "__main__":
    start_server()