import streamlit as st
import pydeck as pdk
import pandas as pd
import time
import altair as alt
import csv

# Título do projeto
st.title('Análise de dados de acidentes de trânsito no Ceará (2022/2023)')
# ---------------------------------------

# Botões
container = st.container(height=90)
with container:
    escala = st.radio(
        "Selecione a escala da análise:",
        ["Região Metropolitana", "Região Estadual"],
        horizontal=True
    )
# ---------------------------------------

# Carregando, filtrando e limpando os dados
# df_2023 = pd.read_csv('~/Archive/Faculdade/big_data/projeto/dados/accidents_prf_2023.csv', sep=';', encoding='iso-8859-1',  on_bad_lines='skip', quoting=csv.QUOTE_NONE)
# df_2022 = pd.read_csv('~/Archive/Faculdade/big_data/projeto/dados/accidents_prf_2022.csv', sep=';', encoding='iso-8859-1',  on_bad_lines='skip', quoting=csv.QUOTE_NONE)

url1 = 'https://drive.google.com/file/d/16-__wGh9iSbjJVgK4e8nnMFQgd8j885E/view?usp=sharing'
url1 = 'https://drive.google.com/uc?id=' + url1.split('/')[-2]
url2 = 'https://drive.google.com/file/d/1BNsNNFtTqtmb9KQVLEgLbLxm9LPFeE5z/view?usp=sharing'
url2 = 'https://drive.google.com/uc?id=' + url2.split('/')[-2]

df_2023 = pd.read_csv(url1,  sep=';', encoding='iso-8859-1',  on_bad_lines='skip', quoting=csv.QUOTE_NONE)
df_2022 = pd.read_csv(url2,  sep=';', encoding='iso-8859-1',  on_bad_lines='skip', quoting=csv.QUOTE_NONE)
df = pd.concat([df_2022, df_2023])

if escala == 'Região Metropolitana':
    metropolitan_area = ['"FORTALEZA"', '"CAUCAIA"', '"EUSEBIO"', '"AQUIRAZ"', '"CASCAVEL"', '"CHOROZINHO"', '"HORIZONTE"', '"MARANGUAPE"', '"MARACANAU"', '"PACAJUS"', '"PARACURU"', '"PINDORETAMA"', '"PARAIPABA"', '"SAO GONÇALO DO AMARANTE"', '"SAO LUIZ DO CURU"', '"TRAIRI"']
    df = df.loc[df['"municipio"'].isin(metropolitan_area)]
if escala == 'Região Estadual':
    df = df

df.columns = df.columns.str.replace('"', '')
df = df.map(lambda x: x.replace('"', '') if isinstance(x, str) else x)
df['latitude'] = df['latitude'].str.replace(',', '.')
df['longitude'] = df['longitude'].str.replace(',', '.')
df['longitude'] = pd.to_numeric(df['longitude'])
df['latitude'] = pd.to_numeric(df['latitude'])

df.columns = df.columns.str.lower()
columns_to_drop = ['pesid', 'ano_fabricacao_veiculo', 'marca']
columns_to_drop = [col for col in columns_to_drop if col in df.columns]
df = df.drop(columns=columns_to_drop)

df['data_inversa'] = pd.to_datetime(df['data_inversa']).dt.to_period('M')
df['mes'] = df['data_inversa'].dt.strftime('%m')
# ---------------------------------------

# Mapa de Incidência de Acidentes
st.markdown('## Mapa de Incidência de Acidentes')
st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=-3.76327,
        longitude=-38.5270,
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=df,
            get_position=['longitude', 'latitude'],
            auto_highlight=True,
            radius=200,
            elevation_scale=8,
            pickable=True,
            elevation_range=[0, 1000],
            extruded=True,
            coverage=1,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position=['longitude', 'latitude'],
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
    ],
))
# ---------------------------------------

st.divider()
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Por idade", "Por tipo de veículo", "Por município", "Por mês", "Por condição meteorológica"])

# Idade dos envolvidos
with tab1:
    st.markdown('## Idade dos envolvidos em acidentes')
    acidentes_por_idade = df[df['idade'] <= 100]
    hist_data = acidentes_por_idade['idade'].value_counts().sort_index()
    chart_placeholder = st.empty()
    num_frames = len(hist_data)
    for i in range(1, num_frames + 1):
        current_data = hist_data.iloc[:i]
        current_df = pd.DataFrame({'idade': current_data.index, 'count': current_data.values})
        chart_placeholder.bar_chart(current_df.set_index('idade'))
        time.sleep(0.1)

# ---------------------------------------

st.divider()

# Tipo de veículos
with tab2:
    st.markdown('## Acidentes por tipo de veículos')

    acidentes_por_veiculo = df['tipo_veiculo'].value_counts()
    acidentes_por_veiculo = acidentes_por_veiculo.dropna()
    acidentes_por_veiculo = acidentes_por_veiculo[acidentes_por_veiculo > 1] 
    acidentes_por_veiculo = acidentes_por_veiculo.sort_values(ascending=True)

    acidentes_df = acidentes_por_veiculo.reset_index()
    acidentes_df.columns = ['Tipo de Veículo', 'Contagem']

    chart_placeholder = st.empty()
    num_frames = len(acidentes_df)

    for i in range(1, num_frames + 1):
        current_data = acidentes_df.iloc[:i]
        bar_chart = alt.Chart(current_data).mark_bar().encode(
            x='Contagem',
            y=alt.Y('Tipo de Veículo', sort='-x')
        ).properties(
            width=600,
            height=500,
            padding={'left': 10, 'top': 10, 'right': 10, 'bottom': 10}
        )
        chart_placeholder.altair_chart(bar_chart, use_container_width=True)
        time.sleep(0.2)
# ---------------------------------------

st.divider()

# Top cidades
with tab3:
    st.markdown('## Cidades com mais óbitos por acidentes')

    df_filtered = df[df['mortos'] > 0]
    obitos_por_municipio = df_filtered.groupby('municipio')['mortos'].sum()
    top_10_municipio = obitos_por_municipio.nlargest(10)
    top_10_municipio = top_10_municipio.sort_values(ascending=True)

    acidentes_df = top_10_municipio.reset_index()
    acidentes_df.columns = ['Município', 'Contagem']

    chart_placeholder = st.empty()
    num_frames = len(acidentes_df)

    for i in range(1, num_frames + 1):
        current_data = acidentes_df.iloc[:i]
        bar_chart = alt.Chart(current_data).mark_bar().encode(
            x='Contagem',
            y=alt.Y('Município', sort='-x')
        ).properties(
            width=600,
            height=500,
            padding={'left': 10, 'top': 10, 'right': 10, 'bottom': 10}
        )
        chart_placeholder.altair_chart(bar_chart, use_container_width=True)
        time.sleep(0.2)
# ---------------------------------------

st.divider()

# Acidentes por período do ano
with tab4:
    st.markdown('## Número de acidentes por periodo do ano')
    acidentes_mensais = df['mes'].value_counts().sort_index()
    chart_placeholder = st.empty()
    num_frames = len(acidentes_mensais)
    for i in range(1, num_frames + 1):
        current_data = acidentes_mensais.iloc[:i]
        current_df = pd.DataFrame({'mes': current_data.index, 'count': current_data.values})
        chart_placeholder.line_chart(current_df.set_index('mes'))
        time.sleep(0.2)
# ---------------------------------------

st.divider()

# Acidentes por condição meteorológica
with tab5:
    st.markdown('## Distribuição de acidentes por condição meteorológica')

    df_filtered = df[df['condicao_metereologica'] != 'Ignorado']
    acidentes_clima = df_filtered['condicao_metereologica'].value_counts().reset_index()
    acidentes_clima.columns = ['condicao_metereologica', 'count']

    pie_chart = alt.Chart(acidentes_clima).mark_arc().encode(
        theta=alt.Theta(field="count", type="quantitative"),
        color=alt.Color(field="condicao_metereologica", type="nominal", title='Condição Meteorológica'),
        tooltip=[
            alt.Tooltip(field='condicao_metereologica', type='nominal', title='Condição Meteorológica'),
            alt.Tooltip(field='count', type='quantitative', title='Contagem')
        ]
    ).properties(
        width=600,
        height=500,
        padding={'left': 10, 'top': 10, 'right': 10, 'bottom': 10}
    )

    st.altair_chart(pie_chart, use_container_width=True)
# ---------------------------------------
