import streamlit as st
import pandas as pd
from thefuzz import process
from pathlib import Path
import json
import os
import hashlib
from datetime import datetime

# Configurações da página
st.set_page_config(
    page_title="SmartAnime",
    page_icon="https://cdn-icons-png.flaticon.com/512/528/528098.png",
    layout="wide",
)

# CSS para padronizar imagens
st.markdown(
    """
    <style>
        img {
            max-height: 400px;
            object-fit: cover;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- GERENCIAMENTO DE FAVORITOS ---
base_dir = Path(__file__).resolve().parents[1]
FAVORITOS_FILE = base_dir / "data" / "favoritos.json"

# --- GERENCIAMENTO DE USUÁRIOS ---
USERS_FILE = base_dir / "data" / "users.json"

def hash_password(password):
    """Gera hash da senha para armazenamento seguro"""
    return hashlib.sha256(password.encode()).hexdigest()

def carregar_usuarios():
    """Carrega dados dos usuários do arquivo"""
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar_usuarios(users):
    """Salva dados dos usuários no arquivo"""
    USERS_FILE.parent.mkdir(exist_ok=True)
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def registrar_usuario(username, password, email=""):
    """Registra um novo usuário"""
    users = carregar_usuarios()

    if username in users:
        return False, "Usuário já existe!"

    users[username] = {
        "password": hash_password(password),
        "email": email,
        "data_criacao": datetime.now().isoformat(),
        "favoritos": []
    }

    salvar_usuarios(users)
    return True, "Usuário registrado com sucesso!"

def autenticar_usuario(username, password):
    """Autentica um usuário"""
    users = carregar_usuarios()

    if username not in users:
        return False, "Usuário não encontrado!"

    if users[username]["password"] != hash_password(password):
        return False, "Senha incorreta!"

    return True, "Login realizado com sucesso!"

def obter_favoritos_usuario(username):
    """Obtém favoritos de um usuário específico"""
    users = carregar_usuarios()
    if username in users:
        return users[username].get("favoritos", [])
    return []

def salvar_favoritos_usuario(username, favoritos):
    """Salva favoritos de um usuário específico"""
    users = carregar_usuarios()
    if username in users:
        users[username]["favoritos"] = favoritos
        salvar_usuarios(users)

def carregar_favoritos():
    """Carrega lista de animes favoritos do usuário atual"""
    if "usuario_logado" in st.session_state:
        return obter_favoritos_usuario(st.session_state.usuario_logado)
    return []

def salvar_favoritos(favoritos):
    """Salva lista de animes favoritos do usuário atual"""
    if "usuario_logado" in st.session_state:
        salvar_favoritos_usuario(st.session_state.usuario_logado, favoritos)

def toggle_favorito(anime_title):
    """Adiciona ou remove anime dos favoritos do usuário atual"""
    if "usuario_logado" not in st.session_state:
        st.warning("Você precisa estar logado para favoritar animes!")
        return

    if "favoritos" not in st.session_state:
        st.session_state.favoritos = carregar_favoritos()

    if anime_title in st.session_state.favoritos:
        st.session_state.favoritos.remove(anime_title)
    else:
        st.session_state.favoritos.append(anime_title)

    salvar_favoritos(st.session_state.favoritos)

def is_favorito(anime_title):
    """Verifica se anime está nos favoritos do usuário atual"""
    if "usuario_logado" not in st.session_state:
        return False

    if "favoritos" not in st.session_state:
        st.session_state.favoritos = carregar_favoritos()
    return anime_title in st.session_state.favoritos

# Inicializar favoritos no session_state
if "favoritos" not in st.session_state:
    st.session_state.favoritos = carregar_favoritos()

# Título e barra lateral
st.title("SMartAnime")
st.sidebar.title("Gêneros Populares")
for genero in ["Ação", "Aventura", "Drama", "Fantasia", "Romance", "Comédia"]:
    st.sidebar.button(genero)

# Seção de Favoritos na Sidebar (só mostra se logado)
if "usuario_logado" in st.session_state:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⭐ Meus Favoritos")
    if st.sidebar.button("Ver Favoritos", use_container_width=True):
        st.session_state.mostrar_favoritos = True
    else:
        st.session_state.mostrar_favoritos = False

    # Contador de favoritos
    num_favoritos = len(st.session_state.get("favoritos", []))
    st.sidebar.caption(f"{num_favoritos} anime(s) favoritado(s)")

# garantir estado inicial
if "busca" not in st.session_state:
    st.session_state.busca = ""

# Botão de perfil no topo
def meu_perfil():
    vazio1, vazio2, col_botao = st.columns([4, 4, 1])
    with col_botao:
        if "usuario_logado" in st.session_state:
            # Usuário logado - mostra menu de perfil
            if st.button(f"👤 {st.session_state.usuario_logado}"):
                st.session_state.mostrar_perfil = True
        else:
            # Usuário não logado - botão de login
            if st.button("Entrar"):
                st.session_state.mostrar_login = True

def interface_login():
    """Interface de login e registro"""
    st.markdown("### 🔐 Acesso à Conta")

    tab_login, tab_registro = st.tabs(["Entrar", "Criar Conta"])

    with tab_login:
        st.markdown("#### Faça seu login")
        with st.form("login_form"):
            username_login = st.text_input("Usuário")
            password_login = st.text_input("Senha", type="password")

            submitted = st.form_submit_button("Entrar")
            if submitted:
                if not username_login or not password_login:
                    st.error("Preencha todos os campos!")
                else:
                    sucesso, mensagem = autenticar_usuario(username_login, password_login)
                    if sucesso:
                        st.session_state.usuario_logado = username_login
                        st.session_state.favoritos = obter_favoritos_usuario(username_login)
                        st.session_state.mostrar_login = False
                        st.success(mensagem)
                        st.rerun()
                    else:
                        st.error(mensagem)

    with tab_registro:
        st.markdown("#### Criar nova conta")
        with st.form("registro_form"):
            username_reg = st.text_input("Nome de usuário")
            email_reg = st.text_input("Email (opcional)")
            password_reg = st.text_input("Senha", type="password")
            password_conf = st.text_input("Confirmar senha", type="password")

            submitted = st.form_submit_button("Criar Conta")
            if submitted:
                if not username_reg or not password_reg:
                    st.error("Usuário e senha são obrigatórios!")
                elif password_reg != password_conf:
                    st.error("As senhas não coincidem!")
                elif len(password_reg) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres!")
                else:
                    sucesso, mensagem = registrar_usuario(username_reg, password_reg, email_reg)
                    if sucesso:
                        st.success(mensagem)
                        st.info("Agora faça seu login!")
                    else:
                        st.error(mensagem)

def interface_perfil():
    """Interface do perfil do usuário logado"""
    st.markdown(f"### 👤 Perfil de {st.session_state.usuario_logado}")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 📊 Estatísticas")
        num_favoritos = len(st.session_state.get("favoritos", []))
        st.metric("Animes Favoritados", num_favoritos)

        # Carregar dados do usuário
        users = carregar_usuarios()
        if st.session_state.usuario_logado in users:
            user_data = users[st.session_state.usuario_logado]
            data_criacao = user_data.get("data_criacao", "")
            if data_criacao:
                try:
                    data_formatada = datetime.fromisoformat(data_criacao).strftime("%d/%m/%Y")
                    st.caption(f"Conta criada em: {data_formatada}")
                except:
                    pass

    with col2:
        st.markdown("#### ⚙️ Ações")
        if st.button("Ver Meus Favoritos", use_container_width=True):
            st.session_state.mostrar_favoritos = True
            st.session_state.mostrar_perfil = False
            st.rerun()

        st.markdown("---")

        if st.button("Sair da Conta", use_container_width=True, type="secondary"):
            # Limpar dados da sessão
            if "usuario_logado" in st.session_state:
                del st.session_state.usuario_logado
            if "favoritos" in st.session_state:
                del st.session_state.favoritos
            if "mostrar_favoritos" in st.session_state:
                del st.session_state.mostrar_favoritos
            if "mostrar_perfil" in st.session_state:
                del st.session_state.mostrar_perfil

            st.success("Logout realizado com sucesso!")
            st.rerun()

meu_perfil()

# Interfaces de autenticação
if st.session_state.get("mostrar_login", False):
    if "usuario_logado" not in st.session_state:
        interface_login()
        st.divider()
    else:
        st.session_state.mostrar_login = False

if st.session_state.get("mostrar_perfil", False):
    interface_perfil()
    st.divider()

csv_path = base_dir / "data" / "animes.csv"

df = pd.read_csv(csv_path, encoding="cp1252")
# Substitui todos os vazios (NaN) na coluna de episódios por 0
if "episodes" in df.columns:
    df["episodes"] = pd.to_numeric(df["episodes"], errors="coerce").fillna(0).astype(int)
else:
    df["episodes"] = 0

# --- FUNÇÕES AUXILIARES ---
def limpar_busca():
    """Limpa o estado de busca e força rerun"""
    st.session_state.busca = ""
    st.rerun()

def exibir_favoritos():
    """Exibe seção de animes favoritos"""
    st.markdown("## ⭐ Meus Favoritos")

    if not st.session_state.favoritos:
        st.info("Você ainda não favoritou nenhum anime. Clique no coração nos cards para adicionar!")
        return

    # Filtrar animes favoritos do DataFrame
    df_favoritos = df[df['title'].isin(st.session_state.favoritos)]

    if df_favoritos.empty:
        st.warning("Alguns animes favoritos podem não estar disponíveis no banco de dados atual.")
        return

    st.write(f"**{len(df_favoritos)} anime(s) favoritado(s)**")

    cols = st.columns(4)
    for i, (_, row) in enumerate(df_favoritos.iterrows()):
        with cols[i % 4]:
            with st.container():
                cover_image = row.get("cover_image_large", "")
                exibir_imagem_padronizada(cover_image)
                st.write(f"**{row.get('title', 'Título não disponível')}**")
                generos_limpos = ", ".join(row.get("generos", [])) if row.get("generos", []) else "Não informado"
                st.caption(f"⭐ {row.get('score', 0)} | {generos_limpos}")

                # Botão para remover dos favoritos
                if st.button("💔 Remover", key=f"rem_fav_{i}", use_container_width=True):
                    toggle_favorito(row.get('title', ''))
                    st.rerun()

# --- ÁREA DE BUSCA (Centralizada) ---
col_busca_1, col_busca_2, col_busca_3 = st.columns([1, 2, 1])

with col_busca_2:
    # O Enter aciona o código automaticamente aqui
    nome_buscado = st.text_input("Pesquisar:", key="busca", placeholder="Digite o nome do anime...")
    botao_clicado = st.button("Buscar Anime", use_container_width=True)
    st.button("Voltar", use_container_width=True, on_click=limpar_busca)


def string_para_lista(genres_str):
    if pd.isna(genres_str) or not genres_str:
        return []
    return [genre.strip() for genre in str(genres_str).split(',')]

if "genres" in df.columns:
    df['generos'] = df['genres'].apply(string_para_lista)
else:
    df['generos'] = [[] for _ in range(len(df))]


def get_column_series(name):
    if name in df.columns:
        return df[name].astype(str)
    return pd.Series([""] * len(df), index=df.index)


def exibir_imagem_padronizada(url, altura_px=300):
    """Exibe imagem com altura padronizada"""
    if pd.notna(url) and url:
        st.image(url, use_container_width=True)
    else:
        st.info("Imagem não disponível.")


def abrir_detalhes_anime(anime_title):
    st.session_state.anime_selecionado = anime_title


def fechar_detalhes():
    if "anime_selecionado" in st.session_state:
        del st.session_state.anime_selecionado
    st.rerun()


def exibir_pagina_detalhes(anime_title):
    anime = df[df["title"] == anime_title]
    if anime.empty:
        st.error("Anime não encontrado.")
        return

    row = anime.iloc[0]
    st.markdown(f"## 🎬 {row.get('title', 'Título não disponível')}")
    exibir_imagem_padronizada(row.get('cover_image_large', ''))

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📌 Informações")
        st.write(f"**Título original:** {row.get('english_title', 'Não disponível')}")
        st.write(f"**Título japonês:** {row.get('japanese_title', 'Não disponível')}")
        st.write(f"**Tipo:** {row.get('type', 'Não informado')}")
        st.write(f"**Status:** {row.get('status', 'Não informado')}")
        st.write(f"**Episódios:** {int(row.get('episodes', 0))}")
        st.write(f"**Duração:** {row.get('duration', 'Não informado')}")
        st.write(f"**Classificação:** {row.get('rating', 'Não informada')}")
        st.write(f"**Score:** {row.get('score', 'Não informado')}")
        generos = row.get('generos', [])
        st.write(f"**Gêneros:** {', '.join(generos) if generos else 'Não informado'}")
        st.write(f"**Sinopse:** {row.get('synopsis', 'Não disponível')}" if row.get('synopsis', '') else "**Sinopse:** Não disponível")

        trailer_id = row.get('trailer_id', '')
        if pd.notna(trailer_id) and trailer_id:
            st.link_button("▶️ Assistir Trailer", url=f"https://www.youtube.com/watch?v={trailer_id}", use_container_width=True)

    with col2:
        st.markdown("### ⭐ Favoritar")
        if "usuario_logado" in st.session_state:
            is_fav = is_favorito(row.get('title', ''))
            button_text = "❤️ Favoritado" if is_fav else "🤍 Favoritar"
            if st.button(button_text, key=f"fav_detail_{anime_title}", use_container_width=True):
                toggle_favorito(row.get('title', ''))
                st.rerun()
        else:
            st.warning("Faça login para favoritar este anime.")
            if st.button("Entrar para favoritar", use_container_width=True):
                st.session_state.mostrar_login = True
                st.rerun()

    st.divider()
    if st.button("🔙 Voltar", on_click=fechar_detalhes, use_container_width=True):
        pass


def calcular_score_recomendacao(generos_alvo, row):
    """Calcula score de recomendação baseado em gêneros, score e popularidade"""
    generos_anime = row.get("generos", [])
    
    # Contar gêneros em comum (peso maior)
    generos_iguais = len(set(generos_alvo).intersection(set(generos_anime)))
    
    # Score de popularidade/avaliação (0-10)
    score_anime = float(row.get("score", 0)) or 0
    
    # Cálculo: 70% baseado em gêneros, 30% baseado em score
    # Normaliza gêneros para escala 0-10
    max_generos = max(len(generos_alvo), len(generos_anime))
    generos_score = (generos_iguais / max_generos * 10) if max_generos > 0 else 0
    
    score_final = (generos_score * 0.7) + (score_anime * 0.3)
    
    return score_final, generos_iguais


def obter_recomendacoes(anime_alvo, generos_alvo, limit=8):
    """Retorna recomendações ordenadas por relevância"""
    df_recom = df.copy()
    
    # Filtra animes com pelo menos 1 gênero em comum
    df_recom['generos_iguais'] = df_recom['generos'].apply(
        lambda x: len(set(generos_alvo).intersection(set(x)))
    )
    
    # Remove o anime selecionado e animes sem gêneros em comum
    df_recom = df_recom[
        (df_recom['title'] != anime_alvo['title']) & 
        (df_recom['generos_iguais'] > 0)
    ]
    
    # Calcula score de recomendação de forma explícita e segura
    scores = []
    for _, row in df_recom.iterrows():
        score, _ = calcular_score_recomendacao(generos_alvo, row)
        scores.append(score)

    df_recom = df_recom.assign(score_recom=scores)
    
    # Ordena por score e retorna
    return df_recom.sort_values(by='score_recom', ascending=False).head(limit)


def aplicar_sugestao(sugestao):
    st.session_state.busca = sugestao



# --- LÓGICA DE EXIBIÇÃO ---
def buscar_anime(nome_buscado, botao_clicado):
    nome_buscado = (nome_buscado or "").strip()
    if not nome_buscado:
        if botao_clicado:
            st.warning("Digite o nome do anime antes de buscar.")
        return

    resultado = df[
        get_column_series("title").str.contains(nome_buscado, case=False, na=False)
        | get_column_series("english_title").str.contains(nome_buscado, case=False, na=False)
        | get_column_series("japanese_title").str.contains(nome_buscado, case=False, na=False)
        | get_column_series("user_preferred_title").str.contains(nome_buscado, case=False, na=False)
    ]

    if not resultado.empty:
        anime_alvo = resultado.iloc[0]
        generos_alvo = anime_alvo["generos"]

        st.write(f"### 📍 {len(resultado)} resultado(s) encontrado(s)")
        st.write("### Resultados da pesquisa")

        max_resultados = 10
        resultado_exibido = resultado.head(max_resultados)
        if len(resultado) > max_resultados:
            st.info(f"Mostrando os {max_resultados} primeiros de {len(resultado)} resultados.")

        cols = st.columns(2)
        for i, (_, row) in enumerate(resultado_exibido.iterrows()):
            with cols[i % 2]:
                with st.container():
                    cover_image = row.get("cover_image_large", "")
                    exibir_imagem_padronizada(cover_image)
                    st.subheader(row.get("title", "Título não disponível"))
                    generos_limpos = ", ".join(row.get("generos", [])) if row.get("generos", []) else "Não informado"
                    st.write(f"**Gêneros:** {generos_limpos}")
                    st.write(f"**Episódios:** {int(row.get('episodes', 0))}")
                    sinopse = str(row.get("synopsis", "") or "")
                    st.caption(sinopse[:150] + "..." if len(sinopse) > 150 else sinopse)
                    trailer_id = row.get("trailer_id", "")
                    if pd.notna(trailer_id) and trailer_id:
                        st.link_button("▶️ Assistir Trailer", url=f"https://www.youtube.com/watch?v={trailer_id}", use_container_width=True)

                    anime_title = row.get("title", "")
                    st.button("Saiba Mais", key=f"details_search_{i}", on_click=abrir_detalhes_anime, args=(anime_title,), use_container_width=True)

                    # Botão de favoritar (só mostra se logado)
                    if "usuario_logado" in st.session_state:
                        anime_title = row.get("title", "")
                        is_fav = is_favorito(anime_title)
                        button_text = "❤️ Favoritado" if is_fav else "🤍 Favoritar"
                        if st.button(button_text, key=f"fav_search_{i}", use_container_width=True):
                            toggle_favorito(anime_title)
                            st.rerun()
                    else:
                        if st.button("🤍 Favoritar (Login necessário)", key=f"fav_search_{i}", use_container_width=True, disabled=True):
                            st.session_state.mostrar_login = True
                            st.rerun()

        st.divider()
        st.write("### ✨ Animes com gêneros similares")

        recom = obter_recomendacoes(anime_alvo, generos_alvo, limit=8)

        if not recom.empty:
            cols_rec = st.columns(4)
            for i, (_, row) in enumerate(recom.iterrows()):
                with cols_rec[i % 4]:
                    with st.container():
                        cover_image = row.get("cover_image_large", "")
                        exibir_imagem_padronizada(cover_image)
                        anime_title = row.get('title', '')
                        st.write(f"**{anime_title or 'Título não disponível'}**")
                        score_recom = row.get('score_recom', 0)
                        generos_iguais = row.get('generos_iguais', 0)
                        st.caption(f"⭐ {score_recom:.1f} | {generos_iguais} gêneros iguais")
                        st.button("Saiba Mais", key=f"rec_{i}", on_click=abrir_detalhes_anime, args=(anime_title,), use_container_width=True)

                        # Botão de favoritar (só mostra se logado)
                        if "usuario_logado" in st.session_state:
                            anime_title = row.get("title", "")
                            is_fav = is_favorito(anime_title)
                            button_text = "❤️ Favoritado" if is_fav else "🤍 Favoritar"
                            if st.button(button_text, key=f"fav_rec_{i}", use_container_width=True):
                                toggle_favorito(anime_title)
                                st.rerun()
                        else:
                            if st.button("🤍 Favoritar (Login necessário)", key=f"fav_rec_{i}", use_container_width=True, disabled=True):
                                st.session_state.mostrar_login = True
                                st.rerun()
        else:
            st.info("Nenhuma recomendação com gêneros similares encontrada.")

    else:
        st.markdown(f"**Nenhum anime encontrado com '{nome_buscado}'.**")
        lista_titulos = df["title"].dropna().astype(str).unique()
        sugestoes = process.extract(nome_buscado, lista_titulos, limit=5)

        exibiu_sugestao = False
        for sugestao, score in sugestoes:
            if score >= 60:
                exibiu_sugestao = True
                st.button(
                    f"Você quis dizer: '{sugestao}'?",
                    on_click=aplicar_sugestao,
                    args=(sugestao,),
                )
        if not exibiu_sugestao:
            st.info("Nenhuma sugestão próxima encontrada. Tente outro nome.")

if st.session_state.get("anime_selecionado"):
    if botao_clicado:
        del st.session_state["anime_selecionado"]
    else:
        exibir_pagina_detalhes(st.session_state.anime_selecionado)
        st.stop()

buscar_anime(nome_buscado, botao_clicado)

# Função para criar um card de anime
def top_animes():
    top_animes_df = df.sort_values(by='score', ascending=False).head(5)
    cols = st.columns(5)
    for i, (_, row) in enumerate(top_animes_df.iterrows()):
        with cols[i]:
            with st.container():
                cover_image = row.get('cover_image_large', '')
                exibir_imagem_padronizada(cover_image)
                anime_title = row.get('title', 'Título não disponível')
                st.caption(f"**{anime_title}**")
                st.button("Saiba Mais", key=f"top_{i}", on_click=abrir_detalhes_anime, args=(anime_title,), use_container_width=True)

                # Botão de favoritar
                anime_title = row.get("title", "")
                is_fav = is_favorito(anime_title)
                button_text = "❤️ Favoritado" if is_fav else "🤍 Favoritar"
                if st.button(button_text, key=f"fav_top_{i}", use_container_width=True):
                    toggle_favorito(anime_title)
                    st.rerun()

st.markdown("## 🌟 Top Animes")

top_animes()

def top_categoria():
    generos_destaque = ["Action", "Romance", "Fantasy", "Comedy", "Drama"]

    st.markdown("🏆 Top por Categoria")
    tabs = st.tabs(generos_destaque)

    for i, genero in enumerate(generos_destaque):
        with tabs[i]:
            top_genero = df[df['genres'].astype(str).str.contains(genero, na=False)].sort_values(by='score', ascending=False).head(4)

            if not top_genero.empty:
                cols = st.columns(4)
                for j, (_, row) in enumerate(top_genero.iterrows()):
                    with cols[j]:
                        with st.container():
                            cover_image = row.get('cover_image_large', '')
                            exibir_imagem_padronizada(cover_image)
                            titulo_curto = row.get('title', '')
                            titulo_curto = titulo_curto[:20] + "..." if len(titulo_curto) > 20 else titulo_curto
                            st.markdown(f"**{titulo_curto}**")
                            st.caption(f"⭐ {row.get('score', 0)}")
                            anime_title = row.get('title', '')
                            st.button("Saiba Mais", key=f"btn_{genero}_{j}", on_click=abrir_detalhes_anime, args=(anime_title,), use_container_width=True)

                            # Botão de favoritar
                            anime_title = row.get("title", "")
                            is_fav = is_favorito(anime_title)
                            button_text = "❤️ Favoritado" if is_fav else "🤍 Favoritar"
                            if st.button(button_text, key=f"fav_cat_{genero}_{j}", use_container_width=True):
                                toggle_favorito(anime_title)
                                st.rerun()
            else:
                st.info(f"Nenhum anime de {genero} encontrado no banco de dados.")

top_categoria()

# Exibir seção de favoritos se solicitado e usuário logado
if st.session_state.get("mostrar_favoritos", False) and "usuario_logado" in st.session_state:
    exibir_favoritos()
    st.divider()
elif st.session_state.get("mostrar_favoritos", False) and "usuario_logado" not in st.session_state:
    st.warning("Você precisa estar logado para acessar seus favoritos!")
    st.session_state.mostrar_favoritos = False

st.divider()

# Funções de DataFrame para exibir tabelas de animes
def exibir_tabela_animes():
    st.markdown("## 📊 Animes em Ordem Alfabética")
    df_organizado = df.sort_values(by='title', ascending=True)
    st.dataframe(df_organizado)

exibir_tabela_animes()