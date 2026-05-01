import streamlit as st
import pandas as pd
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
st.sidebar.button("Isekai")
st.sidebar.button("Seinen")
st.sidebar.button("Romance")
st.sidebar.button("Comédia")

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
    nome_buscado = st.text_input("Pesquisar:", placeholder="Digite o nome do anime...")
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

# --- LÓGICA DE EXIBIÇÃO ---
# Se o usuário escreveu algo E (apertou Enter OU clicou no botão)
def buscar_anime():
    if nome_buscado or botao_clicado:
        
        # 1. Encontrar o anime alvo
        resultado = df[df['title'].str.contains(nome_buscado, case=False, na=False)]
        
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
                    sinopse = anime_alvo['synopsis'] # ou anime_alvo['synopsis']
                    limite = 200

                    if len(sinopse) > limite:
                        sinopse_exibir = sinopse[:limite] + "..."
                    else:
                        sinopse_exibir = sinopse

                    st.write(sinopse_exibir)

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
                        
        else:
            st.error("Nenhum anime encontrado com esse nome.")


buscar_anime()

# Função para criar um card de anime
def anime_card(titulo, imagem_url):
    with st.container():
        st.image(imagem_url, use_container_width=True)
        st.caption(f"**{titulo}**")
        if st.button("Detalhes", key=titulo):
            st.info(f"Abrindo info de {titulo}...")

st.markdown("## 🎬 Top Categorias de Anime")

# --- CATEGORIA 1: SHONEN ---
st.markdown("## 🔥 Shonen")
# Criamos 4 colunas para 4 animes lado a lado
col1, col2, col3, col4 = st.columns(4)

with col1:
    anime_card("Dragon Ball Z", "https://geekmega.com/uploads/geek-obras/obra-3-capa.webp")
with col2:
    anime_card("Naruto", "https://i.pinimg.com/474x/0f/14/43/0f14432778f5435ab82f2801d250bcea.jpg")
with col3:
    anime_card("One Piece", "https://cdn.selectgame.net/wp-content/uploads/2023/05/One-Piece-Capa-Anime-001-Luffy-Nami-Zoro-Usopp-Sanji.webp")
with col4:
    anime_card("Bleach", "https://cinema10.com.br/upload/series/series_2624_bleach_Easy-Resize.com%20(1).jpg?default=poster")

st.divider() # Linha separadora

# --- CATEGORIA 2: ISEKAI ---
st.markdown("## 🌌 Isekai")
col5, col6, col7, col8 = st.columns(4)

with col5:
    anime_card("Sword Art Online", "https://via.placeholder.com/150x200?text=SAO")
with col6:
    anime_card("Overlord", "https://via.placeholder.com/150x200?text=Overlord")
with col7:
    anime_card("Re:Zero", "https://via.placeholder.com/150x200?text=ReZero")
with col8:
    anime_card("Konosuba", "https://via.placeholder.com/150x200?text=Konosuba")

st.divider()

# --- CATEGORIA 3: ROMANCE ---
st.markdown("## 🤍 Romance")
col9, col10, col11, col12 = st.columns(4)

with col9:
    anime_card("MY Dress Up Darling", "https://via.placeholder.com/150x200?text=SAO")
with col10:
    anime_card("Kaguya-sama: Love is War", "https://via.placeholder.com/150x200?text=Overlord")
with col11:
    anime_card("Horimiya", "https://via.placeholder.com/150x200?text=ReZero")
with col12:
    anime_card("The Fragrant Flower Blooms with Dignity", "https://via.placeholder.com/150x200?text=Konosuba")

st.divider()

# --- CATEGORIA 4: COMEDIA ---
st.markdown("## 🎤 Comédia")
col13, col14, col15, col16 = st.columns(4)

with col13:
    anime_card("Spy x Family", "https://via.placeholder.com/150x200?text=SAO")
with col14:
    anime_card("Gintama", "https://via.placeholder.com/150x200?text=Overlord")
with col15:
    anime_card("My Deer Friend Nokotan", "https://via.placeholder.com/150x200?text=ReZero")
with col16:
    anime_card("Grand Blue", "https://via.placeholder.com/150x200?text=Konosuba")

st.divider()

# Funções de DataFrame para exibir tabelas de animes
def exibir_tabela_animes():
    st.markdown("## 📊 Animes em Ordem Alfabética")
    df_organizado = df.sort_values(by='title', ascending=True)
    st.dataframe(df_organizado)

exibir_tabela_animes()