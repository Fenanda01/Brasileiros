from pathlib import Path
from io import BytesIO
import pandas as pd
import streamlit as st
from PIL import Image, ImageOps
from rede import normalizar, informar, filtrar_rede, distancia, rota

st.set_page_config(page_title='Brasileiro | Consultare', page_icon='🏥', layout='wide')
BASE = Path(__file__).resolve().parent
st.markdown('''<style>
.block-container {max-width:1200px;padding-top:2rem;padding-bottom:3rem;}
h1,h2,h3 {color:#176B53;}
[data-testid="stMetric"] {background:#EFF6F2;border-radius:12px;padding:16px;}
</style>''', unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def ler(conteudo, tipo, csv=False):
    if csv:
        df = pd.read_csv(BytesIO(conteudo))
    else:
        livro = pd.ExcelFile(BytesIO(conteudo))
        nomes = ['atletas_planos', 'atletas'] if tipo == 'atletas' else ['Hospitais_Planos', 'hospitais_planos']
        aba = next((n for n in nomes if n in livro.sheet_names), livro.sheet_names[0])
        df = pd.read_excel(livro, sheet_name=aba)
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df.dropna(how='all')


def carregar(upload, tipo):
    if upload is not None:
        return ler(upload.getvalue(), tipo, upload.name.lower().endswith('.csv'))
    nomes = ['Atletas_Tabelas_Atualizadas.xlsx', 'atletas_planos.xlsx'] if tipo == 'atletas' else ['hospitais_goiania_planos.xlsx', 'hospitais_goiania_planos.csv']
    for nome in nomes:
        for pasta in [BASE / 'dados', BASE]:
            p = pasta / nome
            if p.exists():
                return ler(p.read_bytes(), tipo, p.suffix == '.csv')
    return None


def foto(nome):
    nome = Path(str(nome)).name
    nomes = [nome, '4(1).jpeg'] if nome == '4.jpeg' else [nome]
    p = next((BASE/'Fotos'/n for n in nomes if (BASE/'Fotos'/n).is_file()), None)
    if p is None:
        st.caption('Foto não disponível')
        return
    try:
        with Image.open(p) as im:
            im = ImageOps.exif_transpose(im).convert('RGB')
            st.image(ImageOps.fit(im, (420, 420)), use_container_width=True)
    except OSError:
        st.caption('Não foi possível abrir a foto')


with st.sidebar:
    st.header('Arquivos')
    st.caption('Uploads substituem os arquivos apenas nesta sessão. Não atualizam o GitHub.')
    ua = st.file_uploader('Atletas', type=['xlsx'], key='atletas_upload')
    uh = st.file_uploader('Hospitais', type=['xlsx', 'csv'], key='hospitais_upload')

logo = next((BASE/'Fotos'/n for n in ['CONSULTARE.jpg','CONSULTARE(2).jpg'] if (BASE/'Fotos'/n).exists()), None)
if logo:
    st.image(str(logo), width=230)
st.title('Brasileiro | Consultare')
st.caption('Atletas, planos de saúde e rede cadastrada')
try:
    atletas, hospitais = carregar(ua, 'atletas'), carregar(uh, 'hospitais')
except Exception as exc:
    st.error(f'Não foi possível ler os arquivos: {exc}')
    st.stop()
if atletas is None or atletas.empty:
    st.info('Adicione a planilha de atletas à pasta dados ou envie pela barra lateral.')
    st.stop()
faltam = {'id_atleta','nome','operadora','plano'} - set(atletas.columns)
if faltam:
    st.error('Colunas ausentes em atletas: ' + ', '.join(sorted(faltam)))
    st.stop()
if atletas.id_atleta.isna().any() or atletas.id_atleta.duplicated().any():
    st.error('Os IDs das atletas precisam estar preenchidos e ser únicos.')
    st.stop()
for c in ['foto','tipo_contratacao','acomodacao','abrangencia','segmentacao_observacao']:
    if c not in atletas:
        atletas[c] = ''

a,b,c = st.columns(3)
a.metric('Atletas', len(atletas))
b.metric('Operadoras', atletas.operadora.nunique())
c.metric('Planos', atletas.plano.nunique())
galeria, rede, tabela = st.tabs(['👥 Atletas','🏥 Rede de atendimento','📋 Cadastro'])
with galeria:
    a,b = st.columns([2,1])
    busca = a.text_input('Buscar pelo nome')
    op = b.selectbox('Operadora', ['Todas'] + sorted(atletas.operadora.dropna().astype(str).unique()))
    dados = atletas.copy()
    if busca:
        dados = dados[dados.nome.map(normalizar).str.contains(normalizar(busca), regex=False)]
    if op != 'Todas':
        dados = dados[dados.operadora.astype(str).eq(op)]
    st.caption(f'{len(dados)} atleta(s) encontrada(s)')
    registros = dados.to_dict('records')
    for inicio in range(0, len(registros), 3):
        for coluna, atleta in zip(st.columns(3), registros[inicio:inicio+3]):
            with coluna, st.container(border=True):
                foto(atleta['foto'])
                st.subheader(str(atleta['nome']))
                st.write(informar(atleta['operadora']))
                st.caption(informar(atleta['plano']))
                with st.expander('Detalhes do plano'):
                    for chave, titulo in [('tipo_contratacao','Contratação'),('acomodacao','Acomodação'),('abrangencia','Abrangência'),('segmentacao_observacao','Segmentação / observação')]:
                        st.write(f'**{titulo}:** {informar(atleta[chave])}')

with rede:
    ident = st.selectbox('Atleta', atletas.id_atleta.tolist(), format_func=lambda i: str(atletas.loc[atletas.id_atleta.eq(i),'nome'].iloc[0]))
    atleta = atletas.loc[atletas.id_atleta.eq(ident)].iloc[0]
    st.write(f"**{informar(atleta['operadora'])}** · {informar(atleta['plano'])}")
    if hospitais is None:
        st.info('A base de hospitais ainda não foi adicionada. Envie-a na barra lateral.')
    else:
        faltam = {'hospital','operadora','plano','endereco'} - set(hospitais.columns)
        if faltam:
            st.warning('Colunas ausentes em hospitais: ' + ', '.join(sorted(faltam)))
        else:
            lista = filtrar_rede(hospitais, atleta['operadora'], atleta['plano'])
            busca_h = st.text_input('Buscar hospital ou endereço')
            if busca_h:
                texto = lista.hospital.fillna('').astype(str) + ' ' + lista.endereco.fillna('').astype(str)
                lista = lista[texto.map(normalizar).str.contains(normalizar(busca_h), regex=False)]
            for campo in ['latitude','longitude']:
                if campo not in lista:
                    lista[campo] = float('nan')
                lista[campo] = pd.to_numeric(lista[campo].astype(str).str.replace(',','.',regex=False),errors='coerce')
            validas = lista.latitude.between(-90,90) & lista.longitude.between(-180,180)
            lista.loc[~validas,['latitude','longitude']] = float('nan')
            if st.checkbox('Ordenar por distância a um ponto de referência'):
                x,y = st.columns(2)
                lat = x.number_input('Latitude',min_value=-90.,max_value=90.,value=-16.6869,format='%.6f')
                lon = y.number_input('Longitude',min_value=-180.,max_value=180.,value=-49.2648,format='%.6f')
                st.caption('Referência inicial: Goiânia. Distância em linha reta; não representa o percurso de carro.')
                lista['distancia_km'] = [distancia(lat,lon,r.latitude,r.longitude) if pd.notna(r.latitude) and pd.notna(r.longitude) else float('nan') for r in lista.itertuples()]
                lista = lista.sort_values('distancia_km',na_position='last')
            else:
                lista = lista.sort_values('hospital')
            st.caption(f'{len(lista)} registro(s). A listagem reproduz a base cadastrada; confirme o atendimento ao plano com a operadora.')
            if lista.empty:
                st.info('Nenhum hospital cadastrado para essa combinação exata de operadora e plano.')
            pontos = lista.dropna(subset=['latitude','longitude'])
            if not pontos.empty:
                with st.expander('Mapa'):
                    st.map(pontos[['latitude','longitude']])
            for _, h in lista.iterrows():
                with st.container(border=True):
                    st.subheader(str(h['hospital']))
                    st.write(informar(h['endereco']))
                    if informar(h.get('telefone')) != 'Não informado':
                        st.write('Telefone: ' + str(h['telefone']))
                    if pd.notna(h.get('distancia_km')):
                        st.caption(f"{h['distancia_km']:.1f} km em linha reta")
                    st.link_button('Abrir rota no Google Maps', rota(h))

with tabela:
    st.dataframe(atletas, hide_index=True, use_container_width=True)
    st.download_button('Baixar cadastro em CSV', atletas.to_csv(index=False).encode('utf-8-sig'), 'atletas.csv', 'text/csv')
st.divider()
st.caption('CONSULTARE • Brasileiro')
