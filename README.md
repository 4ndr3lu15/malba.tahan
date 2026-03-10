## Malba Tahan – O Enigma do Sultão: 8 Pesos de Ouro

Esta mini-demo é inspirada no espírito do livro brasileiro **“O Homem que Calculava”**, de Malba Tahan, e dá nome ao repositório **“Malba Tahan”**.  
Você é convidado a resolver um problema clássico de balança: descobrir qual das 8 esferas de ouro é ligeiramente mais pesada, usando a balança no máximo **duas vezes**.

### Visão Geral do Projeto

- **Objetivo**: Descobrir qual das 8 esferas aparentemente idênticas é a mais pesada.
- **Restrição**: Você só pode apertar o botão **“Pesar”** no máximo **duas** vezes.
- **Resultado**:
  - Se identificar corretamente a esfera mais pesada, ganha o favor do Sultão.
  - Se errar o palpite, ou não decidir em até duas pesagens, perde o desafio.

### Como o Jogo Funciona

- **Área de preparação**:
  - As 8 esferas começam na área de preparação, numeradas de 1 a 8.
  - A esfera mais pesada é escolhida aleatoriamente no início de cada partida e **não é visivelmente diferente** das demais.

- **Movendo esferas para a balança**:
  - Clique em uma esfera na área de preparação para selecioná-la.
  - Em seguida, clique em um dos pratos da balança (esquerdo ou direito) para colocá-la lá.
  - Clique em uma esfera que já esteja na balança para devolvê-la à área de preparação (banco de esferas).
  - Também é possível clicar em uma área vazia da zona de preparação para devolver a esfera atualmente selecionada.

- **Pesando**:
  - Você só pode clicar em **“Pesar”** quando **os dois pratos tiverem o mesmo número de esferas**.
  - Internamente, cada esfera “normal” tem peso 10 e a esfera mais pesada tem peso 11.
  - Ao pesar:
    - A trave da balança se inclina para o lado mais pesado, ou permanece nivelada se os pesos forem iguais.
    - O contador de pesagens é incrementado, até o máximo de 2.
    - Ao atingir a segunda pesagem, o botão de pesar é desativado e você deve identificar qual esfera é a mais pesada.

- **Identificando a esfera pesada**:
  - Clique em **“Identificar Bola Pesada”** para entrar no modo de identificação.
  - Todas as esferas ficam clicáveis como palpite, com destaques visuais.
  - Clique na esfera que você acredita ser a mais pesada:
    - Se estiver correto, aparece um modal de **vitória**.
    - Se estiver errado, aparece um modal de **derrota**, e o Sultão se mostra descontente.
  - Antes de usar todas as pesagens, você pode cancelar o modo de identificação clicando novamente no botão.

- **Reiniciando / jogando novamente**:
  - **Reiniciar**: Começa uma nova partida imediatamente, sorteando outra esfera pesada e zerando o contador de pesagens.
  - **Jogar Novamente** (no modal final): Fecha o modal e inicia uma nova partida do zero.

### Arquitetura de Arquivos

- `index.html`  
  Define a estrutura da página:
  - Sobreposição (modal) inicial com a história e as instruções.
  - Cabeçalho principal com o título e o contador de pesagens.
  - Área da balança com pratos esquerdo e direito e botões de controle (`Pesar`, `Identificar Bola Pesada`, `Reiniciar`).
  - Área de preparação onde todas as esferas começam.
  - Sobreposição final de fim de jogo para mensagens de vitória/derrota.

- `style.css`  
  Define o visual:
  - Fundo em clima de noite no deserto, com cores em tom de ouro e madeira.
  - Modais de introdução e fim de jogo.
  - Desenho estilizado da balança (trave, pratos, correntes, base).
  - Esferas de ouro com brilho, sombra e estados de hover/seleção.
  - Layout responsivo para telas menores.

- `script.js`  
  Implementa a lógica do jogo:
  - Cria as 8 esferas dinamicamente e sorteia qual será a mais pesada.
  - Controla em que lugar cada esfera está (`staging` / área de preparação, `left` / prato esquerdo, `right` / prato direito).
  - Garante que só é possível pesar quando os dois pratos têm o mesmo número de esferas.
  - Calcula o resultado da pesagem e anima a inclinação da balança.
  - Gerencia o modo de identificação, verificando vitória ou derrota.
  - Controla o contador de pesagens e a exibição dos modais de início/fim de jogo.

### Como Executar o Projeto

Você só precisa de um navegador moderno; não há dependências ou build.

1. Faça o download ou clone o repositório.
2. Abra o arquivo `index.html` diretamente no navegador (duplo clique ou `Arquivo → Abrir`).
3. Leia a introdução, clique em **“Aceitar Desafio”** e tente resolver o enigma do Sultão.

### Notas de Implementação e Limitações

- A mecânica (duas pesagens e uma esfera mais pesada entre oito) segue o problema clássico de balança muitas vezes associado a enigmas matemáticos como os de **Malba Tahan**.
- Não há opção de “revelar resposta”: a identidade da esfera pesada só é exposta pela própria lógica do jogo, ao checar o seu palpite.
- O jogo **não impõe** uma estratégia ótima; ele apenas simula a balança, conta as pesagens e informa o resultado. A arte de encontrar a solução em duas pesagens fica a cargo do jogador – como um verdadeiro “Homem que Calculava”.

