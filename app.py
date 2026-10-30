import os
import redis
import random
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Inicializa o aplicativo Flask
app = Flask(__name__)
CORS(app)  

# Conexão com o Redis (banco de dados em memória para cache)
cache = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", "6379")),
)

def gerar_cor_hex():
    """Gera uma cor aleatória em formato hexadecimal."""
    r = random.randint(200, 255)
    g = random.randint(200, 255)
    b = random.randint(200, 255)
    return f"#{r:02x}{g:02x}{b:02x}"

@app.route("/ola")
def ola_mundo():
    """Rota de exemplo com contador usando Redis e exibição de cor dinâmica."""
    cor_de_fundo = gerar_cor_hex()
    try:
        count = cache.incr("views")
    except Exception:
        count = 1  # Fallback caso o Redis não esteja rodando localmente (ex: testes sem Docker)
    return render_template('ola.html', **{'bg_color': cor_de_fundo, 'count': count})


@app.route("/")
def index():
    """Rota principal que renderiza a página do jogo da adivinhação."""
    return render_template("index.html")


@app.route("/como-funciona")
def como_funciona():
    """Rota da página que explica o funcionamento matemático do jogo, opcionalmente com dados da última jogada."""
    figura_nome = request.args.get("figura")
    figura_icone = request.args.get("icone")
    binario = request.args.get("binario")
    soma = request.args.get("soma")
    pesos = request.args.get("pesos")

    resultado_usuario = None
    if figura_nome and binario and soma:
        cartoes_detalhes = []
        bits_lista = list(binario)
        pesos_config = [
            {"num": 4, "peso": 8, "bit_idx": 0},
            {"num": 3, "peso": 4, "bit_idx": 1},
            {"num": 2, "peso": 2, "bit_idx": 2},
            {"num": 1, "peso": 1, "bit_idx": 3},
        ]
        
        for c in pesos_config:
            char_bit = bits_lista[c["bit_idx"]] if c["bit_idx"] < len(bits_lista) else "0"
            cartoes_detalhes.append({
                "cartao": c["num"],
                "peso": c["peso"],
                "presente": char_bit == "1"
            })

        resultado_usuario = {
            "nome": figura_nome,
            "icone": figura_icone,
            "binario": binario,
            "soma": soma,
            "pesos": pesos,
            "cartoes_detalhes": cartoes_detalhes
        }

    return render_template("como_funciona.html", resultado=resultado_usuario)

# Lista com as 15 figuras utilizadas no jogo (IDs de 1 a 15)
FIGURAS = [
    {"id": 1,  "nome": "Gato",     "icone": "🐱"},
    {"id": 2,  "nome": "Cachorro", "icone": "🐶"},
    {"id": 3,  "nome": "Mundo",    "icone": "🌍"},
    {"id": 4,  "nome": "Casa",     "icone": "🏠"},
    {"id": 5,  "nome": "Leão",     "icone": "🦁"},
    {"id": 6,  "nome": "Bola",     "icone": "⚽"},
    {"id": 7,  "nome": "Banana",   "icone": "🍌"},
    {"id": 8,  "nome": "Maçã",     "icone": "🍎"},
    {"id": 9,  "nome": "Sapo",     "icone": "🐸"},
    {"id": 10, "nome": "Avião",    "icone": "✈️"},
    {"id": 11, "nome": "Sol",      "icone": "☀️"},
    {"id": 12, "nome": "Coração",  "icone": "❤️"},
    {"id": 13, "nome": "Dinheiro", "icone": "💵"},
    {"id": 14, "nome": "Peixe",    "icone": "🐟"},
    {"id": 15, "nome": "Estrela",  "icone": "⭐"}
]

# Configuração dos 4 cartões binários (pesos 1, 2, 4 e 8)
CONFIG_CARTOES = [
    {"bit": 0, "peso": 1, "posicao_estrela": 0},
    {"bit": 1, "peso": 2, "posicao_estrela": 1},
    {"bit": 2, "peso": 4, "posicao_estrela": 3},
    {"bit": 3, "peso": 8, "posicao_estrela": 7}
]


def gerar_cartoes():
    """Gera a distribuição dos 4 cartões com base na lógica binária."""
    cartoes = []
    estrela = next(f for f in FIGURAS if f["id"] == 15)

    for cfg in CONFIG_CARTOES:
        peso = cfg["peso"]
        # Filtra figuras cujo bit correspondente está ativo
        outras = [f for f in FIGURAS if (f["id"] & peso) == peso and f["id"] != 15]

        itens = list(outras)
        itens.insert(cfg["posicao_estrela"], estrela)

        cartoes.append({
            "bit": cfg["bit"],
            "peso": cfg["peso"],
            "itens": itens
        })
    return cartoes


# ===================== ROTAS DA API (JSON) =====================

@app.route("/api/figuras", methods=["GET"])
def get_figuras():
    """Retorna a lista de figuras para o jogador escolher."""
    return jsonify({
        "sucesso": True,
        "figuras": [{"nome": f["nome"], "icone": f["icone"]} for f in FIGURAS]
    })


@app.route("/api/cartoes", methods=["GET"])
def get_cartoes():
    """Retorna os cartões gerados para o jogo."""
    return jsonify({
        "sucesso": True,
        "cartoes": gerar_cartoes()
    })


@app.route("/api/adivinhar", methods=["POST"])
def adivinhar():
    """Recebe os pesos selecionados pelo usuário e descobre qual figura ele escolheu."""
    dados = request.get_json() or {}
    pesos = dados.get("pesos_selecionados", [])

    # Soma os pesos dos cartões onde o usuário disse "Sim"
    soma_binaria = sum(pesos)

    # Procura na lista FIGURAS qual delas tem o "id" igual à soma dos pesos
    figura_encontrada = None
    for f in FIGURAS:
        if f["id"] == soma_binaria:
            figura_encontrada = f
            break  # Encontrou a figura, pode parar a procura

    # Se nenhum cartão foi selecionado ou a soma for inválida
    if not figura_encontrada:
        return jsonify({
            "sucesso": False,
            "erro": "Nenhuma figura válida corresponde aos cartões selecionados."
        }), 400

    binario_str = f"{soma_binaria:04b}"

    return jsonify({
        "sucesso": True,
        "resultado": {
            "figura": {
                "nome": figura_encontrada["nome"],
                "icone": figura_encontrada["icone"]
            },
            "calculo": {
                "pesos": pesos,
                "soma": soma_binaria,
                "binario": binario_str
            }
        }
    })
