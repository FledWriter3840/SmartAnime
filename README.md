# SmartAnime 🎌

SmartAnime é uma plataforma web de recomendação de animes desenvolvida com Python e Streamlit.

O sistema permite pesquisar animes, receber recomendações inteligentes com base em similaridade de gêneros, salvar favoritos, acompanhar histórico de animes assistidos e interagir através de comentários.

---

# ✨ Funcionalidades

## 🔎 Busca Inteligente

* Pesquisa parcial
* Pesquisa por múltiplos nomes
* Sugestões automáticas
* Busca tolerante a erros de digitação

---

## 🤖 Sistema de Recomendação

O SmartAnime recomenda animes com base em:

* gêneros similares
* score
* popularidade

O sistema utiliza lógica de similaridade entre animes para gerar recomendações mais relevantes.

---

## ❤️ Favoritos

Os usuários podem:

* adicionar animes aos favoritos
* visualizar lista personalizada
* salvar favoritos localmente

---

## 📚 Histórico

O sistema permite:

* marcar animes como assistidos
* acompanhar histórico
* evitar duplicações

---

## 👤 Perfil de Usuário

O SmartAnime possui um perfil local contendo:

* nome do usuário
* quantidade de favoritos
* quantidade de animes assistidos
* estatísticas simples

---

## 💬 Comentários

Cada anime possui:

* área de comentários
* armazenamento local de mensagens
* interação entre usuários

---

# 🖼️ Interface

A interface inclui:

* cards personalizados
* imagens dos animes
* trailers
* informações detalhadas
* sidebar com gêneros
* home page com categorias

---

# 🛠️ Tecnologias Utilizadas

* Python
* Streamlit
* Pandas
* TheFuzz
* JSON
* CSS

---

# 📁 Estrutura do Projeto

```bash
SmartAnime/
│
├── app/
│   └── home.py
│
├── assets/
│   ├── logo.png
│   └── style.css
│
├── data/
│   ├── SmartAnime_dataset.csv
│   └── users.json
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

# ▶️ Como Executar o Projeto

## 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
```

---

## 2. Acesse a pasta do projeto

```bash
cd SmartAnime
```

---

## 3. Crie o ambiente virtual

```bash
python -m venv venv
```

---

## 4. Ative o ambiente virtual

### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac

```bash
source venv/bin/activate
```

---

## 5. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## 6. Execute o projeto

```bash
streamlit run app/home.py
```

---

# 📌 Funcionalidades Futuras

* autenticação real de usuários
* banco de dados SQL
* integração com APIs de anime
* sistema avançado de recomendação
* deploy completo online
* ranking personalizado
* sistema de avaliações

---

# 📊 Dataset

O projeto utiliza um dataset personalizado contendo:

* títulos
* gêneros
* scores
* popularidade
* trailers
* plataformas de streaming
* personagens
* staff
* imagens

---

# 🚀 Deploy

O SmartAnime pode ser publicado utilizando:

* Streamlit Community Cloud
* Render
* Railway

---

# 👨‍💻 Autor

Desenvolvido por Matheus.

