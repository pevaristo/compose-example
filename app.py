import os
import redis
import random
from flask import Flask, render_template

app = Flask(__name__)
cache = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
)

def gerar_cor_hex():
    r = random.randint(200, 255)
    g = random.randint(200, 255)
    b = random.randint(200, 255)
    return f"#{r:02x}{g:02x}{b:02x}"

@app.route("/")
def ola_mundo():
    cor_de_fundo = gerar_cor_hex()
    count = cache.incr("views")
    return render_template('index.html', **{'bg_color': cor_de_fundo, 'count': count})