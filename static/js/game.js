// Aguarda o carregamento completo do HTML antes de executar o código JS
document.addEventListener("DOMContentLoaded", () => {
  const API_URL = "/api";

  // Variáveis de controle do jogo
  let cartoes = [];
  let cartaoAtualIndex = 0;
  let pesosConfirmados = [];
  let ultimoResultado = null;

  // Captura dos elementos HTML (Etapas e Botões)
  const stepEscolha = document.getElementById("step-escolha");
  if (!stepEscolha) return;

  const stepCartao = document.getElementById("step-cartao");
  const stepResultado = document.getElementById("step-resultado");

  const gridCatalogo = document.getElementById("grid-catalogo");
  const btnIniciar = document.getElementById("btn-iniciar");

  const gridCartaoItens = document.getElementById("grid-cartao-itens");
  const labelProgresso = document.getElementById("label-progresso");
  const barraProgresso = document.getElementById("barra-progresso");
  const btnSim = document.getElementById("btn-sim");
  const btnNao = document.getElementById("btn-nao");

  const resultadoIcone = document.getElementById("resultado-icone");
  const resultadoNome = document.getElementById("resultado-nome");
  const btnReiniciar = document.getElementById("btn-reiniciar");
  const btnComoFunciona = document.getElementById("btn-como-funciona");

  // Cria um elemento visual para cada figura (ícone e nome)
  function criarCardElemento(icone, nome) {
    const card = document.createElement("div");
    card.className = "card-item";
    card.innerHTML = `
      <span class="text-3xl mb-1">${icone}</span>
      <span class="text-xs font-medium text-slate-300 text-center">${nome}</span>
    `;
    return card;
  }

  // Busca as figuras no Flask via API (GET)
  async function carregarFiguras() {
    const resposta = await fetch(`${API_URL}/figuras`);
    const dados = await resposta.json();
    
    gridCatalogo.innerHTML = "";
    dados.figuras.forEach(figura => {
      gridCatalogo.appendChild(criarCardElemento(figura.icone, figura.nome));
    });
  }

  // Busca os cartões gerados pelo Flask via API (GET)
  async function carregarCartoes() {
    const resposta = await fetch(`${API_URL}/cartoes`);
    const dados = await resposta.json();
    return dados.cartoes;
  }

  // Exibe o cartão atual na tela
  function renderizarCartaoAtual() {
    const cartao = cartoes[cartaoAtualIndex];
    labelProgresso.textContent = `Cartão ${cartaoAtualIndex + 1} de ${cartoes.length}`;
    barraProgresso.style.width = `${((cartaoAtualIndex + 1) / cartoes.length) * 100}%`;

    gridCartaoItens.innerHTML = "";
    cartao.itens.forEach(item => {
      gridCartaoItens.appendChild(criarCardElemento(item.icone, item.nome));
    });
  }

  // Envia as escolhas para o Flask adivinhar a figura (POST)
  async function resolverMagica() {
    const resposta = await fetch(`${API_URL}/adivinhar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pesos_selecionados: pesosConfirmados })
    });
    const dados = await resposta.json();
    
    if (!resposta.ok || !dados.sucesso) {
      throw new Error(dados.erro || "Erro ao adivinhar figura.");
    }
    return dados.resultado;
  }

  // Controla a resposta do usuário ("Sim" ou "Não") para cada cartão
  async function tratarResposta(aparece) {
    // Se a figura aparece no cartão atual, guarda o peso correspondente
    if (aparece) {
      pesosConfirmados.push(cartoes[cartaoAtualIndex].peso);
    }

    cartaoAtualIndex++;

    // Se ainda houver cartões, mostra o próximo
    if (cartaoAtualIndex < cartoes.length) {
      renderizarCartaoAtual();
    } else {
      // Tenta revelar a figura calculada pelo servidor
      try {
        stepCartao.classList.add("hidden");
        const resultado = await resolverMagica();
        ultimoResultado = resultado;
        stepResultado.classList.remove("hidden");

        resultadoIcone.textContent = resultado.figura.icone;
        resultadoNome.textContent = resultado.figura.nome;
      } catch (err) {
        alert("Você indicou não ter visto a figura escolhida em todos os cartões! Por favor, tente novamente.");
        stepResultado.classList.add("hidden");
        stepCartao.classList.add("hidden");
        stepEscolha.classList.remove("hidden");
        carregarFiguras();
      }
    }
  }

  // Eventos de clique nos botões
  btnIniciar.addEventListener("click", async () => {
    cartoes = await carregarCartoes();
    cartaoAtualIndex = 0;
    pesosConfirmados = [];
    stepEscolha.classList.add("hidden");
    stepCartao.classList.remove("hidden");
    renderizarCartaoAtual();
  });

  btnSim.addEventListener("click", () => tratarResposta(true));
  btnNao.addEventListener("click", () => tratarResposta(false));

  btnReiniciar.addEventListener("click", () => {
    stepResultado.classList.add("hidden");
    stepEscolha.classList.remove("hidden");
    carregarFiguras();
  });

  if (btnComoFunciona) {
    btnComoFunciona.addEventListener("click", (e) => {
      e.preventDefault();
      if (ultimoResultado) {
        const params = new URLSearchParams({
          figura: ultimoResultado.figura.nome,
          icone: ultimoResultado.figura.icone,
          binario: ultimoResultado.calculo.binario,
          soma: ultimoResultado.calculo.soma,
          pesos: ultimoResultado.calculo.pesos.join(",")
        });
        window.location.href = `/como-funciona?${params.toString()}`;
      } else {
        window.location.href = "/como-funciona";
      }
    });
  }

  // Inicializa o jogo carregando as figuras na tela inicial
  carregarFiguras();
});