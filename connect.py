
import socket
import threading
import base64

from cryptography.hazmat.primitives import serialization
from cipher import (
    generate_keys,
    load_peer_public_key,
    encrypt_message,
    decrypt_message
)

PORT = 5000


def send_message(conn, peer_public_key, message):
    encrypted = encrypt_message(message, peer_public_key)
    conn.sendall(encrypted + b"\n")


def receive_messages(conn, private_key):
    try:
        with conn.makefile("rb") as reader:
            while True:
                line = reader.readline()
                if not line:
                    print("\nConnection closed.")
                    break

                try:
                    message = decrypt_message(line.strip(), private_key)
                    print(f"\nPartner: {message}")
                    print("You: ", end="", flush=True)
                except Exception:
                    print("\nCannot decrypt received message.")
    except OSError:
        print("\nConnection ended.")


def start_chat(conn):
    generate_keys()

    with open("private_key.pem", "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=None
        )

    with open("public_key.pem", "rb") as f:
        public_key_data = f.read()

    # Exchange public keys
    encoded_key = base64.b64encode(public_key_data) + b"\n"
    conn.sendall(encoded_key)

    with conn.makefile("rb") as reader:
        peer_key_line = reader.readline()

    if not peer_key_line:
        print("Peer did not send a public key.")
        conn.close()
        return

    peer_key_data = base64.b64decode(peer_key_line.strip())
    peer_public_key = load_peer_public_key(peer_key_data)

    print("\nSecure chat connected!")
    print("Type /exit to quit.\n")

    threading.Thread(
        target=receive_messages,
        args=(conn, private_key),
        daemon=True
    ).start()

    try:
        while True:
            message = input("You: ")

            if message.strip() == "/exit":
                break

            if not message.strip():
                continue

            send_message(conn, peer_public_key, message)

    except (OSError, ConnectionError, BrokenPipeError):
        print("Connection lost.")
    finally:
        conn.close()


def start_server(host="0.0.0.0", port=PORT):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((host, port))
        server.listen(1)
        print(f"Waiting for client on port {port}...")

        conn, address = server.accept()
        print(f"Connected to {address[0]}")
        start_chat(conn)

    except OSError as error:
        print(f"Server error: {error}")
    finally:
        server.close()


def start_client(host, port=PORT):
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((host, port))
        print(f"Connected to server {host}:{port}")
        start_chat(conn)

    except OSError as error:
        print(f"Connection failed: {error}")
