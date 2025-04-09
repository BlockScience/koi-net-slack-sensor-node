import os
from dotenv import load_dotenv

load_dotenv()

HOST = "127.0.0.1"
PORT = 8001
URL = f"http://{HOST}:{PORT}/koi-net"

FIRST_CONTACT = "http://127.0.0.1:8000/koi-net"

OBSERVING_CHANNELS = [
    "C0593RJJ2CW", #koi-research
    "C082YTFAA83"  #koi-sensor-testing
]

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]