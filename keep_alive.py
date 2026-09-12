from flask import Flask
import os
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot activo 24/7"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()
