
from cipher import generate_keys
from connect import start_server, start_client, PORT


def main():
    generate_keys()

    print("=== END-TO-END ENCRYPTION CHAT ===")
    print("1. Start Server")
    print("2. Connect as Client")

    choice = input("Choose mode (1/2): ").strip()

    if choice == "1":
        start_server("0.0.0.0", PORT)

    elif choice == "2":
        host = input("Enter server computer IP address: ").strip()
        if host:
            start_client(host, PORT)
        else:
            print("Please enter a valid IP address.")

    else:
        print("Invalid choice. Run the program again.")


if __name__ == "__main__":
    main()
