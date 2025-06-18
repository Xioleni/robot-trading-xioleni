from binance.client import Client
import sys

def connect_to_binance(api_key, secret_key):
    client = Client(api_key, secret_key)
    try:
        client.ping()
        print("Connected successfully")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    api_key = sys.argv[1]
    secret_key = sys.argv[2]
    connect_to_binance(api_key, secret_key)