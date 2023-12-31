import os
from dotenv import load_dotenv

from app import create_app, db

app = create_app(os.getenv("FLASK_CONFIG", "default"))


@app.shell_context_processor
def make_shell_context():
    return dict(db=db)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
