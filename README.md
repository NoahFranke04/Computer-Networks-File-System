# ☁️ Cloud File System

A simple **client-server cloud file system** built with Python using TCP sockets and multithreading. This project allows multiple clients to connect to a central server and perform basic file management operations remotely.

The system supports listing files, creating directories, uploading files, creating text files, moving files, downloading files, and disconnecting from the server.

---

## 🚀 Features

The Cloud File System supports the following commands:

| Command                       | Description                                      |
| ----------------------------- | ------------------------------------------------ |
| `LIST`                        | Lists files and directories stored on the server |
| `MKDIR <name>`                | Creates a new directory on the server            |
| `WRITE <local_file_path>`     | Uploads a local file to the server               |
| `WRITETEXT <filename> <text>` | Creates a text file directly on the server       |
| `MOVE <source> <destination>` | Moves or renames a file or directory             |
| `READ <remote_file_path>`     | Downloads a file from the server                 |
| `EXIT`                        | Disconnects from the server                      |

---

# 🏗️ System Architecture

This project uses a basic **client-server architecture**.

```text
                ┌─────────────────┐
                │     Client 1    │
                └────────┬────────┘
                         │
                         │ TCP Connection
                         │
                ┌────────▼────────┐
                │                 │
                │  Cloud File     │
                │     Server      │
                │                 │
                └────────▲────────┘
                         │
                         │ TCP Connection
                         │
                ┌────────┴────────┐
                │     Client 2    │
                └─────────────────┘
```

The server listens for incoming TCP connections on port `8080`. Each client connection is handled in its own thread, allowing multiple clients to interact with the server at the same time.

---

# 📁 Project Structure

```text
Cloud-File-System/
│
├── client.py
├── server.py
├── README.md
└── example files and directories created during use
```

The server stores files relative to the directory where `server.py` is executed.

---

# ⚙️ Requirements

This project requires:

* Python 3
* A network connection if connecting from another computer
* No external Python libraries

All modules used are included with Python:

```text
socket
threading
os
sys
shutil
time
```

---

# 🖥️ Running the Server

First, start the server.

Open a terminal in the project directory and run:

```bash
python server.py
```

The server should display:

```text
[LISTENING] Server is listening on port 8080
```

The server is now waiting for client connections.

The server is configured with:

```python
HOST = "0.0.0.0"
PORT = 8080
```

Using `0.0.0.0` allows the server to accept connections from other devices on the network.

---

# 💻 Running the Client

Open another terminal and run:

```bash
python client.py
```

By default, the client connects to:

```text
127.0.0.1
```

This means the client will connect to a server running on the same computer.

You should see:

```text
Connected to 127.0.0.1

--- Cloud File System Ready ---
```

---

## 🌐 Connecting to a Remote Server

If the server is running on another computer, provide its IP address when starting the client:

```bash
python client.py 192.168.1.5
```

Replace `192.168.1.5` with the actual IP address of the computer running the server.

Example:

```bash
python client.py 192.168.1.100
```

Both devices must be able to communicate over the network, and port `8080` must not be blocked by a firewall.

---

# 📖 Commands

## LIST

Displays all files and directories located in the server's current directory.

```text
cloud-fs> LIST
```

Example output:

```text
--- Files on Server ---

server.py
client.py
documents
notes.txt
```

---

## MKDIR

Creates a directory on the server.

```text
cloud-fs> MKDIR documents
```

Example response:

```text
Directory 'documents' created.
```

---

## WRITETEXT

Creates a text file directly on the server.

Syntax:

```text
WRITETEXT <filename> <your text>
```

Example:

```text
cloud-fs> WRITETEXT notes.txt Hello from the cloud file system!
```

The server will create:

```text
notes.txt
```

with the following content:

```text
Hello from the cloud file system!
```

---

## WRITE

Uploads a file from the client computer to the server.

Example:

```text
cloud-fs> WRITE example.txt
```

The client first sends the `WRITE` command to the server.

The server responds with:

```text
READY
```

The client then sends the file in chunks until the entire file has been transferred.

Example output:

```text
Uploading example.txt...
Upload complete.
```

### Missing File Behavior

If the specified file does not exist locally, the client automatically creates a sample file so the program can continue running.

For example:

```text
cloud-fs> WRITE test.txt
```

If `test.txt` does not exist, the client creates it with sample content before uploading it.

---

## READ

Downloads a file from the server.

Example:

```text
cloud-fs> READ notes.txt
```

The downloaded file is saved to the client's Downloads folder.

Example:

```text
Download complete: File saved to:

C:\Users\Username\Downloads\notes.txt
```

On Linux or macOS, the file is typically saved to:

```text
~/Downloads/
```

---

## MOVE

Moves or renames a file or directory on the server.

Syntax:

```text
MOVE <source> <destination>
```

Example:

```text
cloud-fs> MOVE notes.txt documents/notes.txt
```

The server will move `notes.txt` into the `documents` directory.

You can also use this command to rename files:

```text
cloud-fs> MOVE notes.txt new_notes.txt
```

---

## EXIT

Disconnects from the server.

```text
cloud-fs> EXIT
```

The client sends an `EXIT` command, closes the connection, and terminates the program.

---

# 🔄 File Transfer Process

Files are transferred using TCP sockets.

Both the client and server use:

```python
BUFFER_SIZE = 4096
```

Files are read and transmitted in chunks of up to 4096 bytes.

The system uses a custom end-of-file marker:

```python
EOF_MARKER = b"<--EOF-->"
```

This marker tells the receiving side that the file transfer has finished.

### Upload Process

```text
Client                  Server
   │                       │
   │ ---- WRITE file ----> │
   │                       │
   │ <------ READY ------- │
   │                       │
   │ ==== File Data ====>  │
   │                       │
   │ ==== EOF Marker ===>  │
   │                       │
```

### Download Process

```text
Client                  Server
   │                       │
   │ ---- READ file -----> │
   │                       │
   │ <-------- OK -------- │
   │                       │
   │ <==== File Data ====  │
   │                       │
   │ <==== EOF Marker ===  │
   │                       │
```

---

# 🧵 Multiple Client Support

The server uses Python's `threading` module to support multiple clients.

When a new client connects:

```python
thread = threading.Thread(
    target=handle_client,
    args=(conn, addr)
)

thread.start()
```

Each connected client receives its own thread.

This allows multiple clients to:

* Connect simultaneously
* Upload files
* Download files
* Create directories
* Create text files
* Move files

The server also displays the number of active connections:

```text
[ACTIVE CONNECTIONS] 2
```

---

# 🔌 Networking Details

The system uses a TCP socket configured with:

```python
socket.AF_INET
```

for IPv4 networking and:

```python
socket.SOCK_STREAM
```

for TCP communication.

The server creates a socket:

```python
server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)
```

The client uses the same socket configuration to connect to the server.

TCP was used because it provides:

* Reliable data delivery
* Ordered data transmission
* Error checking
* Connection-oriented communication

These characteristics are important when transferring files.

---

# 🛡️ Error Handling

The system includes basic error handling for common situations.

Examples include:

* Failed server connections
* Missing files
* Invalid commands
* Missing command arguments
* File movement errors
* Directory creation errors
* Unexpected client disconnects

If an error occurs while processing a client, the server logs it without shutting down the entire server.

---

# 🧪 Example Session

Start the server:

```bash
python server.py
```

Then start the client:

```bash
python client.py
```

Example usage:

```text
cloud-fs> MKDIR documents
Directory 'documents' created.

cloud-fs> WRITETEXT hello.txt Hello World!

Text written to 'hello.txt' successfully.

cloud-fs> LIST

--- Files on Server ---

server.py
client.py
documents
hello.txt

cloud-fs> MOVE hello.txt documents/hello.txt
Successfully moved 'hello.txt' to 'documents/hello.txt'.

cloud-fs> READ documents/hello.txt
Download complete: File saved to Downloads/hello.txt

cloud-fs> EXIT
```

---

# ⚠️ Current Limitations

This project is designed as a learning project and does not include the advanced security features of a real cloud storage platform.

Current limitations include:

* No user authentication
* No encryption
* No user accounts
* No access permissions
* Files are stored directly on the server's file system
* No database
* No file size limits
* The custom EOF marker could theoretically appear inside a transferred file
* File paths are not restricted to a dedicated server storage directory

Because of these limitations, this project should be used for educational purposes and trusted networks.

---

# 🔮 Possible Future Improvements

Potential improvements include:

* User authentication and login accounts
* Password hashing
* TLS/SSL encryption
* A dedicated server storage directory
* File permissions
* User-specific directories
* File deletion commands
* File metadata
* File size limits
* Better transfer protocols using file sizes instead of an EOF marker
* Graphical user interface
* Web-based client
* Database integration
* Cloud deployment
* Logging and monitoring

---

# 🛠️ Technologies Used

* **Python**
* **TCP/IP Networking**
* **Python Sockets**
* **Multithreading**
* **File System Operations**

---

# 📚 What This Project Demonstrates

This project demonstrates several important computer science and networking concepts:

* Client-server architecture
* TCP socket programming
* IPv4 networking
* Multithreading
* Concurrent client handling
* File I/O
* Binary file transfer
* Command parsing
* Error handling
* Remote file operations

---

# 👤 Author

**Noah Franke**

Computer Science Student

GitHub: `https://github.com/NoahFranke04`

---

## License

This project is intended for educational and learning purposes.
