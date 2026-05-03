import streamlit as st
import pandas as pd
from thefuzz import fuzz, process
import numpy as np
import csv 

# Configurações da página
st.set_page_config(
    page_title="SmartAnime",
    page_icon="https://cdn-icons-png.flaticon.com/512/528/528098.png",
    layout="wide")

# Título e barra lateral
st.title('SMartAnime')
st.sidebar.title('Gêneros Populares')
st.sidebar.button("Ação")
st.sidebar.button("Aventura")
st.sidebar.button("Drama")
st.sidebar.button("Fantasia")
st.sidebar.button("Romance")
st.sidebar.button("Comédia")

# garantir estado inicial
if "busca" not in st.session_state:
    st.session_state.busca = ""

# Botão de perfil no topo
def meu_perfil():
    vazio1, vazio2, col_botao = st.columns([4, 4, 1])
    with col_botao:
        if st.button("Meu perfil"):
            st.write("Acessando perfil do usuário...")
meu_perfil()    

df = pd.read_csv('../data/animes.csv', encoding='cp1252')
# Substitui todos os vazios (NaN) na coluna de episódios por 0
df['episodes'] = df['episodes'].fillna(0).astype(int)

# --- ÁREA DE BUSCA (Centralizada) ---
col_busca_1, col_busca_2, col_busca_3 = st.columns([1, 2, 1])

with col_busca_2:
    # O Enter aciona o código automaticamente aqui
    nome_buscado = st.text_input("Pesquisar:",key ="busca", placeholder="Digite o nome do anime...")
    botao_clicado = st.button("Buscar Anime", use_container_width=True)
    voltar_inicio = st.button("Voltar", use_container_width=True)

def string_para_lista(genres_str):
    if pd.isna(genres_str):
        return []
    return [genre.strip() for genre in genres_str.split(',')]
df['generos'] = df['genres'].apply(string_para_lista)

def similaridade_de_generos(genres1, genres2):
    if not genres1 or not genres2:
        return 0.0
    set1 = set(genres1)
    set2 = set(genres2)
    intersecao = set1.intersection(set2)
    uniao = set1.union(set2)
    return len(intersecao) / len(uniao) if uniao else 0.0


nome_buscado = nome_buscado.strip()
# --- LÓGICA DE EXIBIÇÃO ---
# Se o usuário escreveu algo E (apertou Enter OU clicou no botão)
def buscar_anime(nome_buscado, botao_clicado):  

    if nome_buscado or botao_clicado:
        
        # 1. Encontrar o anime alvo
        resultado = df[
            df['title'].str.contains(nome_buscado, case=False, na=False)|
            df['english_title'].str.contains(nome_buscado, case=False, na=False)|
            df['japanese_title'].str.contains(nome_buscado, case=False, na=False)|
            df['user_preferred_title'].str.contains(nome_buscado, case=False, na=False)
        ]

        
        if not resultado.empty:
            anime_alvo = resultado.iloc[0]
            generos_alvo = anime_alvo['generos']
            
            # --- PRIMEIRO: MOSTRAR O RESULTADO DA BUSCA (CARD) ---
            st.write("### 📍 Resultado Encontrado")
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(anime_alvo['cover_image_large'], use_container_width=True)
                with c2:
                    st.header(anime_alvo['title'])
                    generos_limpos = ", ".join(anime_alvo['generos'])
                    st.write(f"**Gêneros:** {generos_limpos}")
                    st.write(f"**Episódios:** {int(anime_alvo['episodes'])}")
                    st.markdown("**Sinopse:**")
                    st.caption(anime_alvo['synopsis'][:250] + "..." if len(anime_alvo['synopsis']) > 250 else anime_alvo['synopsis']) # ou anime_alvo['synopsis']
                    st.markdown("Onde assistir:")
                    st.write(anime_alvo['streaming_sites']) # ou anime_alvo['streaming_sites']

                    trailer_col, saiba_col = st.columns(2)
                    id_video = anime_alvo['trailer_id']
                    url_trailer = f"https://www.youtube.com/watch?v={id_video}" if pd.notna(id_video) else None
                    with trailer_col:
                        if url_trailer:
                            st.link_button("▶️ Assistir Trailer", url=str(url_trailer), use_container_width=True)
                        else:
                            st.button("🚫 Sem Trailer", disabled=True, use_container_width=True)
                    with saiba_col:
                        if st.button("ℹ️ Saiba Mais", use_container_width=True):
                            st.info(f"Abrindo detalhes de {anime_alvo['title']}...")

            st.divider()

            # --- SEGUNDO: MOSTRAR RECOMENDAÇÕES ---
            st.write("### ✨ Animes com gêneros similares")
            
            # Lógica de similaridade
            df_comp = df.copy()
            df_comp['pontos'] = df_comp['generos'].apply(
                lambda x: len(set(generos_alvo).intersection(set(x)))
            )
            
            # Filtra (tira o pesquisado) e ordena
            recom = df_comp[df_comp['title'] != anime_alvo['title']].sort_values(by='pontos', ascending=False).head(4)

            # Exibição em colunas
            cols_rec = st.columns(4)
            for i, (idx, row) in enumerate(recom.iterrows()):
                with cols_rec[i]:
                    with st.container(border=True):
                        st.image(row['cover_image_large'], use_container_width=True)
                        st.write(f"**{row['title']}**")
                        st.caption(f"{row['pontos']} gêneros iguais")
                        st.button("Detalhes", key=f"rec_{idx}", use_container_width=True)
                        

        else:
            lista_titulos = df['title'].dropna().unique()
            sugestoes = process.extract(nome_buscado, lista_titulos, limit=5)

            st.markdown(f"**Nenhum anime encontrado com '{nome_buscado}'.**")

            for i, (sugestao, score) in enumerate(sugestoes):
                if score >= 60:
                    if st.button(
                        f"Você quis dizer: '{sugestao}'?",
                        key=f"sugestao_{i}"
                    ):
                        st.session_state.busca = sugestao
                        st.rerun()
                else : st.error("Nenhum anime encontrado com esse nome.")


buscar_anime(nome_buscado, botao_clicado)

# Função para criar um card de anime
def top_animes():
    top_animes = df.sort_values(by='score', ascending=False).head(5)
    cols = st.columns(5)
    for i, (idx, row) in enumerate(top_animes.iterrows()):
        with cols[i]:
                with st.container(border=True):
                    st.image(row['cover_image_large'], use_container_width=True)
                    st.caption(f"**{row['title']}**")
                    if st.button("Detalhes", key=row['title']):
                        st.info(f"Abrindo info de {row['title']}...")

st.markdown("## 🌟 Top Animes")

top_animes()

def top_categoria():

# Lista dos gêneros que você quer destacar

    generos_destaque = ["Action", "Romance", "Fantasy", "Comedy", "Drama"]

    st.markdown("🏆 Top por Categoria")

    # Criando abas para cada gênero
    tabs = st.tabs(generos_destaque)

    for i, genero in enumerate(generos_destaque):
        with tabs[i]:
            # Filtragem: Pegamos animes que contenham o gênero e ordenamos pelo Score
            # O str.contains ajuda a achar o gênero mesmo que ele esteja no meio de outros
            top_genero = df[df['genres'].str.contains(genero, na=False)].sort_values(by='score', ascending=False).head(4)
            
            if not top_genero.empty:
                cols = st.columns(4)
                for j, (idx, row) in enumerate(top_genero.iterrows()):
                    with cols[j]:
                        with st.container(border=True):
                            # Imagem com altura fixa para não quebrar o layout
                            st.image(row['cover_image_large'], use_container_width=True)
                            
                            # Título limitado
                            titulo_curto = row['title'][:20] + "..." if len(row['title']) > 20 else row['title']
                            st.markdown(f"**{titulo_curto}**")
                            
                            # Nota em destaque
                            st.caption(f"⭐ {row['score']}")
                            
                            # Botão para ver detalhes (opcional)
                            if st.button("Detalhes", key=f"btn_{genero}_{idx}", use_container_width=True):
                                st.session_state.busca = row['title'] # Exemplo de como trocar a busca principal
            else:
                st.info(f"Nenhum anime de {genero} encontrado no banco de dados.")

top_categoria()

st.divider()

# Funções de DataFrame para exibir tabelas de animes
def exibir_tabela_animes():
    st.markdown("## 📊 Animes em Ordem Alfabética")
    df_organizado = df.sort_values(by='title', ascending=True)
    st.dataframe(df_organizado)

exibir_tabela_animes()