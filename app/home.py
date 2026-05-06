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
        "favoritos": [],
        "historico": [],
        "comentarios": {}
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

# --- GERENCIAMENTO DE HISTÓRICO ---
def normalizar_historico(historico):
    """Converte histórico antigo (lista de títulos) para registros com data."""
    if not historico:
        return []

    historico_normalizado = []
    for item in historico:
        if isinstance(item, dict):
            title = item.get("title")
            date = item.get("data") or item.get("date")
            if title:
                historico_normalizado.append({"title": title, "data": date or datetime.now().isoformat()})
        elif isinstance(item, str):
            historico_normalizado.append({"title": item, "data": datetime.now().isoformat()})

    # Remover duplicatas mantendo o primeiro registro encontrado
    vistos = set()
    resultado = []
    for item in historico_normalizado:
        if item["title"] not in vistos:
            resultado.append(item)
            vistos.add(item["title"])

    return resultado


def obter_historico_usuario(username):
    """Obtém histórico de animes assistidos do usuário"""
    users = carregar_usuarios()
    if username in users:
        return normalizar_historico(users[username].get("historico", []))
    return []


def salvar_historico_usuario(username, historico):
    """Salva histórico de animes assistidos do usuário"""
    users = carregar_usuarios()
    if username in users:
        users[username]["historico"] = historico
        salvar_usuarios(users)


def carregar_historico():
    """Carrega histórico do usuário atual"""
    if "usuario_logado" in st.session_state:
        return obter_historico_usuario(st.session_state.usuario_logado)
    return []


def salvar_historico(historico):
    """Salva histórico do usuário atual"""
    if "usuario_logado" in st.session_state:
        salvar_historico_usuario(st.session_state.usuario_logado, historico)


def obter_titulos_historico(historico):
    """Extrai títulos do histórico para checagens e filtragem."""
    return [item.get("title") for item in historico if isinstance(item, dict) and item.get("title")]


def marcar_como_assistido(anime_title):
    """Marca um anime como assistido no histórico sem duplicar"""
    if "usuario_logado" not in st.session_state:
        st.warning("Você precisa estar logado para marcar como assistido!")
        return

    if "historico" not in st.session_state:
        st.session_state.historico = carregar_historico()

    titulos = obter_titulos_historico(st.session_state.historico)
    if anime_title in titulos:
        st.info("Este anime já está no seu histórico.")
        return

    st.session_state.historico.append({"title": anime_title, "data": datetime.now().isoformat()})
    salvar_historico(st.session_state.historico)
    st.success("Anime marcado como assistido!")


def is_assistido(anime_title):
    """Verifica se anime já foi marcado como assistido"""
    if "usuario_logado" not in st.session_state:
        return False

    if "historico" not in st.session_state:
        st.session_state.historico = carregar_historico()
    return anime_title in obter_titulos_historico(st.session_state.historico)


def obter_comentarios_usuario(username):
    """Obtém os comentários registrados pelo usuário"""
    users = carregar_usuarios()
    if username in users:
        return users[username].get("comentarios", {})
    return {}


def salvar_comentarios_usuario(username, comentarios):
    """Salva os comentários do usuário"""
    users = carregar_usuarios()
    if username in users:
        users[username]["comentarios"] = comentarios
        salvar_usuarios(users)


def adicionar_comentario(anime_title, safe_key):
    """Adiciona um comentário do usuário ao anime"""
    if "usuario_logado" not in st.session_state:
        st.warning("Você precisa estar logado para comentar!")
        return

    input_key = f"{safe_key}_input"
    texto = st.session_state.get(input_key, "").strip()
    if not texto:
        st.warning("Digite um comentário antes de enviar.")
        return

    username = st.session_state.usuario_logado
    comentarios = obter_comentarios_usuario(username)
    if not isinstance(comentarios, dict):
        comentarios = {}

    comentarios_por_anime = comentarios.get(anime_title, [])
    comentarios_por_anime.append({
        "texto": texto,
        "data": datetime.now().isoformat()
    })

    comentarios[anime_title] = comentarios_por_anime
    salvar_comentarios_usuario(username, comentarios)
    st.session_state[input_key] = ""
    st.success("Comentário publicado!")


def todos_comentarios_anime(anime_title):
    """Retorna todos os comentários de um anime por todos os usuários"""
    users = carregar_usuarios()
    comentarios = []

    for username, dados in users.items():
        user_comentarios = dados.get("comentarios", {})
        anime_comentarios = user_comentarios.get(anime_title, [])
        for comentario in anime_comentarios:
            comentarios.append({
                "usuario": username,
                "texto": comentario.get("texto", ""),
                "data": comentario.get("data", datetime.now().isoformat())
            })

    return sorted(comentarios, key=lambda c: c.get("data", ""), reverse=True)


# Inicializar favoritos e histórico no session_state
if "favoritos" not in st.session_state:
    st.session_state.favoritos = carregar_favoritos()
if "historico" not in st.session_state:
    st.session_state.historico = carregar_historico()

# Título e barra lateral
st.title("SMartAnime")
st.sidebar.title("Gêneros Populares")
generos_sidebar = [
    "Ação", "Aventura", "Drama", "Fantasia", "Romance", "Comédia",
    "Ecchi", "Hentai", "Horror", "Mahou Shoujo", "Mecha", "Music",
    "Mystery", "Psychological", "Sci-Fi", "Slice of Life", "Sports",
    "Supernatural", "Thriller"
]
cols_sidebar = st.sidebar.columns(3)
for i, genero in enumerate(generos_sidebar):
    with cols_sidebar[i % 3]:
        if st.button(genero, key=f"genero_btn_{i}", use_container_width=True):
            st.session_state.selected_genero = genero
            st.session_state.pagina_genero = 1
            st.session_state.mostrar_favoritos = False
            st.session_state.mostrar_historico = False
            st.session_state.mostrar_perfil = False

# Seção de Favoritos e Histórico na Sidebar (só mostra se logado)
if "usuario_logado" in st.session_state:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⭐ Meus Favoritos")
    favoritos_preview = st.session_state.get("favoritos", [])[:3]
    if favoritos_preview:
        for title in favoritos_preview:
            st.sidebar.write(f"• {title}")
        restante = len(st.session_state.get("favoritos", [])) - 3
        if restante > 0:
            if st.sidebar.button(f"Ver mais favoritos ({restante})", use_container_width=True, key="ver_mais_favoritos"):
                st.session_state.selected_genero = None
                st.session_state.mostrar_favoritos = True
                st.session_state.mostrar_historico = False
                st.session_state.mostrar_perfil = False
        else:
            if st.sidebar.button("Ver todos os favoritos", use_container_width=True, key="ver_todos_favoritos"):
                st.session_state.selected_genero = None
                st.session_state.mostrar_favoritos = True
                st.session_state.mostrar_historico = False
                st.session_state.mostrar_perfil = False
    else:
        st.sidebar.caption("Nenhum favorito ainda.")

    st.sidebar.markdown("---")
    st.sidebar.subheader("📚 Meu Histórico")
    historico_preview = obter_titulos_historico(st.session_state.get("historico", []))[:3]
    if historico_preview:
        for title in historico_preview:
            st.sidebar.write(f"• {title}")
        restante = len(st.session_state.get("historico", [])) - 3
        if restante > 0:
            if st.sidebar.button(f"Ver mais histórico ({restante})", use_container_width=True, key="ver_mais_historico"):
                st.session_state.selected_genero = None
                st.session_state.mostrar_historico = True
                st.session_state.mostrar_favoritos = False
                st.session_state.mostrar_perfil = False
        else:
            if st.sidebar.button("Ver todo o histórico", use_container_width=True, key="ver_todo_historico"):
                st.session_state.selected_genero = None
                st.session_state.mostrar_historico = True
                st.session_state.mostrar_favoritos = False
                st.session_state.mostrar_perfil = False
    else:
        st.sidebar.caption("Nenhum anime assistido ainda.")

    # Contador de favoritos e histórico
    num_favoritos = len(st.session_state.get("favoritos", []))
    num_historico = len(st.session_state.get("historico", []))
    st.sidebar.caption(f"{num_favoritos} anime(s) favoritado(s)")
    st.sidebar.caption(f"{num_historico} anime(s) assistido(s)")

# garantir estado inicial
if "busca" not in st.session_state:
    st.session_state.busca = ""
if "selected_genero" not in st.session_state:
    st.session_state.selected_genero = None
if "pagina_genero" not in st.session_state:
    st.session_state.pagina_genero = 1

# Botão de perfil no topo
def meu_perfil():
    vazio1, vazio2, col_botao = st.columns([4, 4, 1])
    with col_botao:
        if "usuario_logado" in st.session_state:
            # Usuário logado - abre página de perfil
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
                        st.session_state.historico = obter_historico_usuario(username_login)
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
    """Interface do perfil do usuário logado em página exclusiva"""
    st.markdown(f"# 👤 {st.session_state.usuario_logado}")
    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📊 Estatísticas")
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

            num_historico = len(st.session_state.get("historico", []))
            st.metric("Animes Assistidos", num_historico)

    with col2:
        st.markdown("### ⚙️ Ações")
        if st.button("Ver Meus Favoritos", use_container_width=True):
            st.session_state.selected_genero = None
            st.session_state.mostrar_favoritos = True
            st.session_state.mostrar_perfil = False
        if st.button("Ver Meu Histórico", use_container_width=True):
            st.session_state.selected_genero = None
            st.session_state.mostrar_historico = True
            st.session_state.mostrar_perfil = False

        st.markdown("---")

        if st.button("Voltar", use_container_width=True):
            st.session_state.mostrar_perfil = False

        if st.button("Sair da Conta", use_container_width=True, type="secondary"):
            # Limpar dados da sessão
            if "usuario_logado" in st.session_state:
                del st.session_state.usuario_logado
            if "favoritos" in st.session_state:
                del st.session_state.favoritos
            if "historico" in st.session_state:
                del st.session_state.historico
            if "mostrar_favoritos" in st.session_state:
                del st.session_state.mostrar_favoritos
            if "mostrar_historico" in st.session_state:
                del st.session_state.mostrar_historico
            if "mostrar_perfil" in st.session_state:
                del st.session_state.mostrar_perfil

            st.success("Logout realizado com sucesso!")
            st.rerun()

meu_perfil()

# Exibir página exclusiva de perfil se solicitado
if st.session_state.get("mostrar_perfil", False):
    if "usuario_logado" in st.session_state:
        interface_perfil()
        st.stop()
    else:
        st.session_state.mostrar_perfil = False

# Interfaces de autenticação
if st.session_state.get("mostrar_login", False):
    if "usuario_logado" not in st.session_state:
        interface_login()
        st.divider()
    else:
        st.session_state.mostrar_login = False

csv_path = base_dir / "data" / "animes.csv"

# Carregar dados dos animes
df = pd.read_csv(csv_path, encoding="cp1252")
if "episodes" in df.columns:
    df["episodes"] = pd.to_numeric(df["episodes"], errors="coerce").fillna(0).astype(int)
else:
    df["episodes"] = 0

# Exibir página de favoritos se solicitado (ANTES de renderizar o conteúdo principal)
if st.session_state.get("mostrar_favoritos", False):
    if "usuario_logado" in st.session_state:
        st.markdown("# ⭐ Meus Favoritos")
        st.divider()
        
        if not st.session_state.favoritos:
            st.info("Você ainda não favoritou nenhum anime. Clique no coração nos cards para adicionar!")
        else:
            df_favoritos = df[df['title'].isin(st.session_state.favoritos)]
            if df_favoritos.empty:
                st.warning("Alguns animes favoritos podem não estar disponíveis no banco de dados atual.")
            else:
                st.write(f"**{len(df_favoritos)} anime(s) favoritado(s)**")
                cols = st.columns(4)
                for i, (_, row) in enumerate(df_favoritos.iterrows()):
                    with cols[i % 4]:
                        with st.container():
                            cover_image = row.get("cover_image_large", "")
                            if pd.notna(cover_image) and cover_image:
                                st.image(cover_image, use_container_width=True)
                            else:
                                st.info("Imagem não disponível.")
                            st.write(f"**{row.get('title', 'Título não disponível')}**")
                            generos_limpos = ", ".join(row.get("generos", [])) if row.get("generos", []) else "Não informado"
                            st.caption(f"⭐ {row.get('score', 0)} | {generos_limpos}")
                            if st.button("💔 Remover", key=f"rem_fav_{i}", use_container_width=True):
                                toggle_favorito(row.get('title', ''))
        
        st.divider()
        if st.button("🔙 Voltar", use_container_width=True):
            st.session_state.mostrar_favoritos = False
        st.stop()
    else:
        st.warning("Você precisa estar logado para acessar seus favoritos!")
        st.session_state.mostrar_favoritos = False

# Exibir página de histórico se solicitado (ANTES de renderizar o conteúdo principal)
if st.session_state.get("mostrar_historico", False):
    if "usuario_logado" in st.session_state:
        st.markdown("# 📚 Histórico de Assistidos")
        st.divider()
        
        if not st.session_state.historico:
            st.info("Seu histórico de assistidos está vazio. Marque um anime como assistido na página de detalhes.")
        else:
            historico_ordenado = sorted(
                st.session_state.historico,
                key=lambda item: item.get("data", ""),
                reverse=True,
            )
            st.write(f"**{len(historico_ordenado)} anime(s) assistido(s)**")
            cols = st.columns(4)
            index = 0
            for item in historico_ordenado:
                anime_title = item.get("title")
                data_marcacao = item.get("data")
                if not anime_title:
                    continue
                row = df[df["title"] == anime_title]
                if row.empty:
                    continue
                row = row.iloc[0]
                data_formatada = data_marcacao
                try:
                    data_formatada = datetime.fromisoformat(data_marcacao).strftime("%d/%m/%Y %H:%M")
                except Exception:
                    pass
                with cols[index % 4]:
                    with st.container():
                        cover_image = row.get("cover_image_large", "")
                        if pd.notna(cover_image) and cover_image:
                            st.image(cover_image, use_container_width=True)
                        else:
                            st.info("Imagem não disponível.")
                        st.write(f"**{anime_title}**")
                        generos_limpos = ", ".join(row.get("generos", [])) if row.get("generos", []) else "Não informado"
                        st.caption(f"⭐ {row.get('score', 0)} | {generos_limpos}")
                        st.caption(f"🗓️ Assistido em: {data_formatada}")
                        st.markdown("✅ Assistido")
                index += 1
        
        st.divider()
        if st.button("🔙 Voltar", use_container_width=True):
            st.session_state.mostrar_historico = False
        st.stop()
    else:
        st.warning("Você precisa estar logado para acessar seu histórico!")
        st.session_state.mostrar_historico = False

df = pd.read_csv(csv_path, encoding="cp1252")
# Substitui todos os vazios (NaN) na coluna de episódios por 0
if "episodes" in df.columns:
    df["episodes"] = pd.to_numeric(df["episodes"], errors="coerce").fillna(0).astype(int)
else:
    df["episodes"] = 0

# --- FUNÇÕES AUXILIARES ---
def limpar_busca():
    """Limpa o estado de busca"""
    st.session_state.busca = ""

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


def exibir_historico():
    """Exibe seção de animes assistidos"""
    st.markdown("## 📚 Histórico de Assistidos")

    if not st.session_state.historico:
        st.info("Seu histórico de assistidos está vazio. Marque um anime como assistido na página de detalhes.")
        return

    historico_ordenado = sorted(
        st.session_state.historico,
        key=lambda item: item.get("data", ""),
        reverse=True,
    )

    st.write(f"**{len(historico_ordenado)} anime(s) assistido(s)**")

    cols = st.columns(4)
    index = 0
    for item in historico_ordenado:
        anime_title = item.get("title")
        data_marcacao = item.get("data")
        if not anime_title:
            continue

        row = df[df["title"] == anime_title]
        if row.empty:
            continue

        row = row.iloc[0]
        data_formatada = data_marcacao
        try:
            data_formatada = datetime.fromisoformat(data_marcacao).strftime("%d/%m/%Y %H:%M")
        except Exception:
            pass

        with cols[index % 4]:
            with st.container():
                cover_image = row.get("cover_image_large", "")
                exibir_imagem_padronizada(cover_image)
                st.write(f"**{anime_title}**")
                generos_limpos = ", ".join(row.get("generos", [])) if row.get("generos", []) else "Não informado"
                st.caption(f"⭐ {row.get('score', 0)} | {generos_limpos}")
                st.caption(f"🗓️ Assistido em: {data_formatada}")
                st.markdown("✅ Assistido")
        index += 1


def exibir_pagina_genero(genero, page=1, page_size=12):
    """Exibe todos os animes de um gênero com paginação."""
    st.markdown(f"# 🎬 {genero}")
    df_filtrado = df[df['generos'].apply(lambda generos: genero in generos if isinstance(generos, list) else False)]
    total = len(df_filtrado)

    if total == 0:
        st.warning(f"Nenhum anime encontrado para o gênero {genero}.")
        return

    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    df_pagina = df_filtrado.iloc[start:start + page_size]

    st.markdown(f"**Total de animes:** {total}  \n" \
                f"**Página:** {page} de {total_pages}  \n" \
                f"**Mostrando:** {len(df_pagina)} por página")
    st.divider()

    cols = st.columns(4)
    for i, (_, row) in enumerate(df_pagina.iterrows()):
        with cols[i % 4]:
            renderizar_card_anime(row, f"genre_{genero}_{start + i}")

    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("◀️ Anterior", key=f"gen_prev_{genero}", disabled=page <= 1):
            st.session_state.pagina_genero = page - 1
            st.rerun()
    with col2:
        if st.button("Limpar filtro", key=f"gen_clear_{genero}"):
            st.session_state.selected_genero = None
            st.session_state.pagina_genero = 1
            st.rerun()
    with col3:
        if st.button("Próxima ▶️", key=f"gen_next_{genero}", disabled=page >= total_pages):
            st.session_state.pagina_genero = page + 1
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

        st.markdown("### ✅ Histórico")
        if "usuario_logado" in st.session_state:
            is_watched = is_assistido(row.get('title', ''))
            watch_text = "✅ Assistido" if is_watched else "📌 Marcar como assistido"
            if st.button(watch_text, key=f"watched_detail_{anime_title}", use_container_width=True, disabled=is_watched):
                marcar_como_assistido(row.get('title', ''))
                st.rerun()
        else:
            st.warning("Faça login para marcar este anime como assistido.")
            if st.button("Entrar para marcar como assistido", use_container_width=True):
                st.session_state.mostrar_login = True
                st.rerun()

        st.divider()
        st.markdown("### 💬 Comentários")
        if "usuario_logado" in st.session_state:
            safe_key = "comentario_" + "".join(ch if ch.isalnum() else "_" for ch in anime_title)
            input_key = f"{safe_key}_input"
            if input_key not in st.session_state:
                st.session_state[input_key] = ""
            st.text_area("Escreva seu comentário:", key=input_key, height=120)
            st.button("Comentar", key=f"{safe_key}_btn", on_click=adicionar_comentario, args=(anime_title, safe_key), use_container_width=True)
        else:
            st.warning("Faça login para comentar neste anime.")

        comentarios = todos_comentarios_anime(anime_title)
        if comentarios:
            for comentario in comentarios:
                data_formatada = comentario.get("data", "")
                try:
                    data_formatada = datetime.fromisoformat(data_formatada).strftime("%d/%m/%Y %H:%M")
                except Exception:
                    pass
                st.markdown(f"**{comentario.get('usuario', 'Anônimo')}** — {data_formatada}")
                st.write(comentario.get("texto", ""))
                st.divider()
        else:
            st.info("Seja o primeiro a comentar neste anime!")

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


def obter_recomendacoes_historico(limit=8):
    """Retorna recomendações baseadas no histórico de assistidos do usuário"""
    if "usuario_logado" not in st.session_state or not st.session_state.historico:
        return pd.DataFrame()  # Retorna DataFrame vazio se não logado ou sem histórico

    # Obter títulos assistidos
    titulos_assistidos = obter_titulos_historico(st.session_state.historico)

    # Filtrar animes assistidos do DataFrame
    df_assistidos = df[df['title'].isin(titulos_assistidos)]

    if df_assistidos.empty:
        return pd.DataFrame()

    # Calcular gêneros mais frequentes nos assistidos
    generos_contagem = {}
    for _, row in df_assistidos.iterrows():
        for genero in row.get('generos', []):
            generos_contagem[genero] = generos_contagem.get(genero, 0) + 1

    # Ordenar gêneros por frequência
    generos_alvo = sorted(generos_contagem.keys(), key=lambda g: generos_contagem[g], reverse=True)[:5]  # Top 5 gêneros

    if not generos_alvo:
        return pd.DataFrame()

    # Filtrar animes não assistidos
    df_recom = df[~df['title'].isin(titulos_assistidos)].copy()

    # Filtrar animes com pelo menos 1 gênero em comum
    df_recom['generos_iguais'] = df_recom['generos'].apply(
        lambda x: len(set(generos_alvo).intersection(set(x)))
    )

    # Manter apenas animes com gêneros em comum
    df_recom = df_recom[df_recom['generos_iguais'] > 0]

    # Calcular score de recomendação
    scores = []
    for _, row in df_recom.iterrows():
        score, _ = calcular_score_recomendacao(generos_alvo, row)
        scores.append(score)

    df_recom = df_recom.assign(score_recom=scores)

    # Ordena por score e retorna
    return df_recom.sort_values(by='score_recom', ascending=False).head(limit)


def renderizar_card_anime(row, key_prefix, show_favorito=True, show_assistido=True, show_detalhes=True):
    """Renderiza um card de anime com opções de favorito e status de assistido"""
    with st.container():
        cover_image = row.get("cover_image_large", "")
        exibir_imagem_padronizada(cover_image)
        anime_title = row.get('title', 'Título não disponível')
        st.write(f"**{anime_title}**")

        # Indicador de já assistido
        if show_assistido and "usuario_logado" in st.session_state:
            if is_assistido(anime_title):
                st.markdown("✅ **Já assistido**")

        generos_limpos = ", ".join(row.get("generos", [])) if row.get("generos", []) else "Não informado"
        st.caption(f"⭐ {row.get('score', 0)} | {generos_limpos}")

        # Botão de favoritar
        if show_favorito and "usuario_logado" in st.session_state:
            is_fav = is_favorito(anime_title)
            button_text = "❤️ Favoritado" if is_fav else "🤍 Favoritar"
            if st.button(button_text, key=f"fav_{key_prefix}_{anime_title}", use_container_width=True):
                toggle_favorito(anime_title)
                st.rerun()
        elif show_favorito:
            if st.button("🤍 Favoritar (Login necessário)", key=f"fav_{key_prefix}_{anime_title}", use_container_width=True, disabled=True):
                st.session_state.mostrar_login = True
                st.rerun()

        if show_detalhes:
            st.button("Saiba Mais", key=f"details_{key_prefix}_{anime_title}", on_click=abrir_detalhes_anime, args=(anime_title,), use_container_width=True)


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
    
    # Se logado, excluir animes já assistidos
    if "usuario_logado" in st.session_state and st.session_state.historico:
        titulos_assistidos = obter_titulos_historico(st.session_state.historico)
        df_recom = df_recom[~df_recom['title'].isin(titulos_assistidos)]
    
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
                renderizar_card_anime(row, f"search_{i}")

        st.divider()
        st.write("### ✨ Animes com gêneros similares")

        recom = obter_recomendacoes(anime_alvo, generos_alvo, limit=8)

        if not recom.empty:
            cols_rec = st.columns(4)
            for i, (_, row) in enumerate(recom.iterrows()):
                with cols_rec[i % 4]:
                    renderizar_card_anime(row, f"rec_{i}")
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

if st.session_state.get("selected_genero"):
    exibir_pagina_genero(st.session_state.selected_genero, st.session_state.pagina_genero)
    st.stop()

buscar_anime(nome_buscado, botao_clicado)

# Função para criar um card de anime
def top_animes():
    top_animes_df = df.sort_values(by='score', ascending=False).head(5)
    cols = st.columns(5)
    for i, (_, row) in enumerate(top_animes_df.iterrows()):
        with cols[i]:
            renderizar_card_anime(row, f"top_{i}")

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
                        renderizar_card_anime(row, f"cat_{genero}_{j}")
            else:
                st.info(f"Nenhum anime de {genero} encontrado no banco de dados.")

top_categoria()

# Recomendações baseadas no histórico (só mostra se logado e com histórico)
if "usuario_logado" in st.session_state and st.session_state.historico:
    st.markdown("## 🎯 Recomendações para Você")
    recom_historico = obter_recomendacoes_historico(limit=8)

    if not recom_historico.empty:
        cols_rec_hist = st.columns(4)
        for i, (_, row) in enumerate(recom_historico.iterrows()):
            with cols_rec_hist[i % 4]:
                renderizar_card_anime(row, f"hist_rec_{i}")
    else:
        st.info("Não conseguimos encontrar recomendações baseadas no seu histórico. Continue assistindo animes para melhorar as sugestões!")

st.divider()

# Funções de DataFrame para exibir tabelas de animes
def exibir_tabela_animes():
    st.markdown("## 📊 Animes em Ordem Alfabética")
    df_organizado = df.sort_values(by='title', ascending=True)
    st.dataframe(df_organizado)

exibir_tabela_animes()