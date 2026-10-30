import pytest
from app import app, FIGURAS, CONFIG_CARTOES

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Testa se a rota principal (/) carrega com sucesso."""
    response = client.get("/")
    assert response.status_code == 200

def test_como_funciona_route(client):
    """Testa se a página de explicação (/como-funciona) carrega com sucesso."""
    response = client.get("/como-funciona")
    assert response.status_code == 200

def test_como_funciona_com_parametros(client):
    """Testa a página /como-funciona recebendo parâmetros via GET de uma jogada."""
    response = client.get("/como-funciona?figura=Mundo&icone=🌍&binario=1010&soma=3&pesos=1,2")
    assert response.status_code == 200
    assert b"Mundo" in response.data
    assert b"1010" in response.data

def test_api_figuras(client):
    """Testa o endpoint GET /api/figuras (retorna 15 figuras)."""
    response = client.get("/api/figuras")
    assert response.status_code == 200
    data = response.get_json()
    assert data["sucesso"] is True
    assert len(data["figuras"]) == 15

def test_api_cartoes(client):
    """Testa o endpoint GET /api/cartoes (retorna 4 cartões binários)."""
    response = client.get("/api/cartoes")
    assert response.status_code == 200
    data = response.get_json()
    assert data["sucesso"] is True
    cartoes = data["cartoes"]
    assert len(cartoes) == 4
    for cartao in cartoes:
        assert len(cartao["itens"]) == 8  # Cada cartão tem exatamente 8 itens

def test_api_adivinhar_sucesso(client):
    """Testa o endpoint POST /api/adivinhar com pesos válidos (ex: Sapo = 2 + 4 + 8 = 14)."""
    response = client.post("/api/adivinhar", json={"pesos_selecionados": [1, 8]})
    assert response.status_code == 200
    data = response.get_json()
    assert data["sucesso"] is True
    assert data["resultado"]["figura"]["nome"] == "Sapo"
    assert data["resultado"]["calculo"]["soma"] == 9
    assert data["resultado"]["calculo"]["binario"] == "1001"

def test_api_adivinhar_casos_diversos(client):
    """Testa múltiplos cenários de adivinhação (mínimo, máximo e intermediário)."""
    # ID 1 (Gato) = peso [1]
    res1 = client.post("/api/adivinhar", json={"pesos_selecionados": [1]})
    assert res1.status_code == 200
    assert res1.get_json()["resultado"]["figura"]["nome"] == "Gato"

    # ID 15 (Estrela) = pesos [1, 2, 4, 8]
    res15 = client.post("/api/adivinhar", json={"pesos_selecionados": [1, 2, 4, 8]})
    assert res15.status_code == 200
    assert res15.get_json()["resultado"]["figura"]["nome"] == "Estrela"

def test_api_adivinhar_erro_sem_selecao(client):
    """Testa o endpoint POST /api/adivinhar com lista vazia (nenhum cartão visto), gerando erro 400."""
    response = client.post("/api/adivinhar", json={"pesos_selecionados": []})
    assert response.status_code == 400
    data = response.get_json()
    assert data["sucesso"] is False
    assert "erro" in data

def test_ola_route_redis(client):
    """Testa se a rota /ola executa o incremento no Redis e carrega com sucesso."""
    response = client.get("/ola")
    assert response.status_code == 200
