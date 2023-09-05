import logging

from src.config import API_ID, API_HASH, APP_TITLE, get_session
from src.repository import BlockedDataRepo
from src.client import Client
from src.exceptions import SessionFileNotFoundError

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    try:
        session = get_session()
    except SessionFileNotFoundError:
        logging.error("Отсутствует файл data/session.txt! Нужно авторизоваться в телеге (python3 auth.py).")
    else:
        client = Client(
            session=session,
            app_title=APP_TITLE,
            api_id=API_ID,
            api_hash=API_HASH,
            repo=BlockedDataRepo()
        )
        client.run()
