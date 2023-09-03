from config import API_ID, API_HASH, APP_NAME
from repository import BlockedDataRepo
from client import Client

if __name__ == '__main__':
    client = Client(APP_NAME, API_ID, API_HASH, BlockedDataRepo())
    client.run()
