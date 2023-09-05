import os

from dotenv import load_dotenv

from src.exceptions import SessionFileNotFoundError

load_dotenv()

API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
APP_TITLE = os.getenv('APP_TITLE')


def get_session() -> str:
    try:
        with open('/run/secrets/session') as f:
            session = f.read()
    except FileNotFoundError:
        try:
            with open('./data/session.txt') as f:
                session = f.read()
        except FileNotFoundError:
            session = None

    if not session:
        raise SessionFileNotFoundError
    return session
