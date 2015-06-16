import os

ENV = os.environ.get("ENV", "local")
DBNAME = "thewulfdb" if ENV == "production" else "thewulfdbdev"
USERHOME = os.path.expanduser("~")
