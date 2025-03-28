import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os
from datetime import datetime
from jinja2 import Template
import logging
from typing import Tuple

# Configuração do logging aprimorada
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações de parâmetros
CONFIG = {
    "default_chart_width": 800,
    "default_chart_height": 500,
    "required_columns": [
        'Tipo de publicação', 'Respostas', 'Compartilhamentos',
        'Alcance', 'Nome da conta', 'Horário de publicação'
    ]
}

# Exceções customizadas para tratamento de erros
class DataValidationError(Exception):
    pass

class DataProcessingError(Exception):
    pass

# Função para aplicação de CSS customizado
def apply_custom_css() -> None:
    custom_css = """
    <style>
    .app-title {
        font-family: 'Arial', sans-serif;
        color: #00000;
        font-size: 2.8em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
        transition: all 0.3s ease-in-out;
    }
    @media only screen and (max-width: 600px) {
        .app-title { font-size: 2em; }
    }
    body {
        background-color: #f9f9f9;
        color: #faf7f7;
        margin: 0;
        padding: 0;
    }
    .stButton button {
        background-color: #003366;
        color: #ffffff;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #005599;
    }
    .kpi-card {
        background: #faf7f7;
        padding: 5px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
        text-align: center;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        border: 1px solid #ccc;
        padding: 10px;
        text-align: center;
    }
    th {
        background-color: #e6e6e6;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

# Classe responsável pelo processamento e validação dos dados
class DataProcessor:
    def __init__(self, required_columns: list):
        self.required_columns = required_columns

    def validate_csv_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        missing = [col for col in self.required_columns if col not in df.columns]
        if missing:
            error_msg = f"Colunas ausentes: {missing}. Dados inconsistentes impossibilitam a continuidade."
            logger.error(error_msg)
            raise DataValidationError(error_msg)
        return df

    @st.cache_data(show_spinner=False)
    def padronizar(_self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            df = _self.validate_csv_schema(df)
            col_rename = {
                'Tipo de publicação': 'Tipo',
                'Respostas': 'Respostas',
                'Compartilhamentos': 'Compartilhamentos',
                'Alcance': 'Alcance',
                'Nome da conta': 'Nome da conta',
                'Horário de publicação': 'Horário de publicação'
            }
            df = df.rename(columns=col_rename)
            # Conversão para numérico com preenchimento para evitar nulos problemáticos
            numeric_cols = ['Respostas', 'Compartilhamentos', 'Alcance']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            df.fillna(0, inplace=True)
            logger.info("Padronização concluída com sucesso.")
            return df
        except Exception as e:
            logger.exception("Erro na padronização.")
            raise DataProcessingError(e)

    @st.cache_data(show_spinner=False)
    def calcular_engajamento(_self, df: pd.DataFrame) -> pd.DataFrame:
        required = ['Respostas', 'Compartilhamentos', 'Alcance']
        if not all(col in df.columns for col in required):
            error_msg = "Colunas necessárias para engajamento não estão presentes."
            logger.error(error_msg)
            raise DataValidationError(error_msg)
        df['Engajamento Total'] = df['Respostas'] + df['Compartilhamentos']
        df['Taxa de Engajamento (%)'] = df.apply(
            lambda row: round((row['Engajamento Total'] / row['Alcance'] * 100), 2) if row['Alcance'] != 0 else 0,
            axis=1
        )
        logger.info("Engajamento calculado com sucesso.")
        return df

    @st.cache_data(show_spinner=False)
    def converter_data(_self, df: pd.DataFrame) -> pd.DataFrame:
        if 'Horário de publicação' not in df.columns:
            error_msg = "Coluna 'Horário de publicação' ausente."
            logger.error(error_msg)
            raise DataValidationError(error_msg)
        df['Data'] = pd.to_datetime(df['Horário de publicação'], errors='coerce')
        if df['Data'].isnull().all():
            error_msg = "Erro na conversão das datas. Verifique o formato dos dados."
            logger.error(error_msg)
            raise DataProcessingError(error_msg)
        df['Mês'] = df['Data'].dt.to_period('M').astype(str)
        df['Trimestre'] = df['Data'].dt.to_period('Q').astype(str)
        logger.info("Conversão de data concluída com sucesso.")
        return df

# Função auxiliar para extração da marca
def extrair_marca(nome: str) -> str:
    if not isinstance(nome, str):
        return 'Desconhecida'
    nome = nome.lower()
    marcas_mapping = {
        'MARCA1': 'MARCA 1',
        'MARCA2': 'MARCA 2',
        'MARCA3': 'MARCA 3',
        'OUTRAS': 'OUTRAS MARCAS (Outro)'
    }
    for chave, marca in marcas_mapping.items():
        if chave in nome:
            return marca
    return 'Desconhecida'

# Classe responsável pela visualização, relatórios e interação com o usuário
class DashboardVisualizer:
    def __init__(self):
        pass

    def gerar_grafico_interativo(self, df: pd.DataFrame, titulo: str, coluna: str, ylabel: str) -> None:
        if 'Marca' not in df.columns or 'Período' not in df.columns:
            st.error("Colunas necessárias para gráfico não estão presentes.")
            return
        # Agrupar os dados para obter a média por marca e período
        df_group = df.groupby(['Marca', 'Período'])[coluna].mean().reset_index()
        fig = px.bar(
            df_group, x='Marca', y=coluna, color='Período',
            title=titulo, labels={coluna: ylabel},
            barmode='group'
        )
        fig.update_layout(width=CONFIG["default_chart_width"], height=CONFIG["default_chart_height"])
        st.plotly_chart(fig, use_container_width=True)

    def gerar_relatorio_html(self, comparativo: pd.DataFrame, comparativo_tipo: pd.DataFrame) -> str:
        html_template = """
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <title>Relatório Comparativo Stories</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
              th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
              th { background-color: #f2f2f2; }
            </style>
          </head>
          <body>
            <h1>Relatório Comparativo Stories</h1>
            <h2>Comparativo Geral</h2>
            {{ comparativo_html | safe }}
            <h2>Comparativo por Marca, Tipo e Período</h2>
            {{ comparativo_tipo_html | safe }}
            <p>Relatório gerado em: {{ current_date }}</p>
          </body>
        </html>
        """
        template = Template(html_template)
        relatorio = template.render(
            comparativo_html=comparativo.to_html(index=False),
            comparativo_tipo_html=comparativo_tipo.to_html(index=False),
            current_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        return relatorio

    def exibir_kpis(self, df_total: pd.DataFrame, df_filtered: pd.DataFrame) -> None:
        total_pub = df_filtered.shape[0]
        # KPI: Respostas
        media_respostas = df_filtered['Respostas'].mean()
        media_respostas_passado = df_filtered[df_filtered['Período'] == 'Ano Passado']['Respostas'].mean()
        media_respostas_atual = df_filtered[df_filtered['Período'] == 'Ano Atual']['Respostas'].mean()
        variacao_respostas = ((media_respostas_atual - media_respostas_passado) / media_respostas_passado * 100) if media_respostas_passado else 0

        # KPI: Engajamento
        media_engajamento = df_filtered['Engajamento Total'].mean()
        media_engajamento_passado = df_filtered[df_filtered['Período'] == 'Ano Passado']['Engajamento Total'].mean()
        media_engajamento_atual = df_filtered[df_filtered['Período'] == 'Ano Atual']['Engajamento Total'].mean()
        variacao_engajamento = ((media_engajamento_atual - media_engajamento_passado) / media_engajamento_passado * 100) if media_engajamento_passado else 0

        def format_variation(variacao: float) -> str:
            arrow = "▲" if variacao >= 0 else "▼"
            color = "green" if variacao >= 0 else "red"
            return f"<p style='color:{color}; font-size:0.9em;'>{arrow} {abs(variacao):.1f}%</p>"

        with st.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='kpi-card'><h4>Total de Stories</h4><p>{total_pub:,}</p></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(
                    f"<div class='kpi-card'><h4>Média de Respostas</h4><p>{media_respostas:.1f}</p>{format_variation(variacao_respostas)}</div>",
                    unsafe_allow_html=True
                )
            with col3:
                st.markdown(
                    f"<div class='kpi-card'><h4>Média de Engajamento</h4><p>{media_engajamento:.1f}</p>{format_variation(variacao_engajamento)}</div>",
                    unsafe_allow_html=True
                )

    def exportar_excel(self, comparativo: pd.DataFrame, comparativo_tipo: pd.DataFrame) -> bytes:
        try:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                comparativo.to_excel(writer, sheet_name="Comparativo", index=False)
                comparativo_tipo.to_excel(writer, sheet_name="Comparativo_Tipo", index=False)
            return output.getvalue()
        except Exception as e:
            logger.exception("Erro na exportação para Excel.")
            st.error(f"Erro ao exportar para Excel: {e}")
            return b""

# Função para agrupamento dos dados
def get_comparativo(df: pd.DataFrame, group_col: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    required_cols = ['Marca', group_col, 'Tipo', 'Respostas', 'Compartilhamentos', 'Taxa de Engajamento (%)']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        error_msg = f"Colunas ausentes para agrupamento: {missing}"
        logger.error(error_msg)
        raise DataValidationError(error_msg)
    
    comparativo = df.groupby(['Marca', group_col]).agg({
        'Tipo': 'count',
        'Respostas': 'mean',
        'Compartilhamentos': 'mean',
        'Taxa de Engajamento (%)': 'mean'
    }).rename(columns={'Tipo': 'Qtd Stories'}).reset_index()
    
    comparativo_tipo = df.groupby(['Marca', 'Tipo', group_col]).agg({
        'Tipo': 'count',
        'Respostas': 'mean',
        'Compartilhamentos': 'mean',
        'Taxa de Engajamento (%)': 'mean'
    }).rename(columns={'Tipo': 'Qtd Stories'}).reset_index()
    
    return comparativo, comparativo_tipo

# Função principal de execução da aplicação Streamlit
def main() -> None:
    apply_custom_css()
    
    # Exibição da logo (se disponível)
    logo_path = os.path.join(os.path.dirname(__file__), "LOGO DA MARCA.JPEG")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as file:
            st.image(file.read(), caption="NOME DA MARCA", width=100)
    else:
        st.error("Logo não encontrada!")
    
    st.markdown('<div class="app-title">Dashboard de Stories do Instagram</div>', unsafe_allow_html=True)
    st.write("Carregue os arquivos CSV referentes aos Stories do Ano Passado e do Ano Atual para comparação.")
    
    # Upload dos CSVs
    uploaded_file_passado = st.file_uploader("Selecione o CSV do Ano Passado", type="csv")
    uploaded_file_atual = st.file_uploader("Selecione o CSV do Ano Atual", type="csv")
    if not uploaded_file_passado or not uploaded_file_atual:
        st.info("Por favor, carregue os arquivos CSV para prosseguir.")
        st.stop()
    
    try:
        df_antigo = pd.read_csv(uploaded_file_passado)
        df_novo = pd.read_csv(uploaded_file_atual)
    except Exception as e:
        st.error(f"Erro ao ler os arquivos CSV: {e}")
        logger.exception(f"Erro ao ler os CSVs: {e}")
        return
    
    # Processamento dos dados utilizando a classe DataProcessor
    processor = DataProcessor(CONFIG["required_columns"])
    try:
        df_antigo = processor.padronizar(df_antigo)
        df_novo = processor.padronizar(df_novo)
        df_antigo = processor.calcular_engajamento(df_antigo)
        df_novo = processor.calcular_engajamento(df_novo)
        df_antigo = processor.converter_data(df_antigo)
        df_novo = processor.converter_data(df_novo)
    except (DataValidationError, DataProcessingError) as e:
        st.error(f"Erro durante o processamento dos dados: {e}")
        return
    
    df_antigo['Período'] = 'Ano Passado'
    df_novo['Período'] = 'Ano Atual'
    df_total = pd.concat([df_antigo, df_novo], ignore_index=True)
    df_total['Marca'] = df_total['Nome da conta'].apply(extrair_marca)
    
    # Conversão explícita para string de todas as colunas do tipo object
    for col in df_total.select_dtypes(include=['object']).columns:
        df_total[col] = df_total[col].astype(str)
    
    # Filtros na barra lateral
    with st.sidebar.expander("Filtros Avançados", expanded=True):
        unique_brands = sorted(df_total['Marca'].unique())
        selected_brands = st.multiselect("Selecione as marcas", unique_brands, default=unique_brands)
        df_filtered = df_total[df_total['Marca'].isin(selected_brands)]
    
        unique_tipos = sorted(df_filtered['Tipo'].unique())
        selected_tipos = st.multiselect("Selecione os tipos de publicação", unique_tipos, default=unique_tipos)
        df_filtered = df_filtered[df_filtered['Tipo'].isin(selected_tipos)]
    
        if 'Data' in df_filtered.columns and not df_filtered['Data'].isnull().all():
            min_date = df_filtered['Data'].min().date()
            max_date = df_filtered['Data'].max().date()
            date_range = st.date_input("Selecione o intervalo de datas", [min_date, max_date])
            if isinstance(date_range, list) and len(date_range) == 2:
                start_date, end_date = date_range
                df_filtered = df_filtered[(df_filtered['Data'].dt.date >= start_date) & (df_filtered['Data'].dt.date <= end_date)]
    
    # Organização em Tabs
    tabs = st.tabs(["Dados Consolidados", "Gráficos Interativos", "Relatórios e Downloads"])
    visualizer = DashboardVisualizer()
    
    with tabs[0]:
        st.subheader("Dados Consolidados")
        st.dataframe(df_total.head().fillna(''))
        visualizer.exibir_kpis(df_total, df_filtered)
    
        group_options = {
            "Período (Ano Passado vs Ano Atual)": "Período",
            "Mensal": "Mês",
            "Trimestral": "Trimestre"
        }
        group_option = st.selectbox("Agrupar dados por:", list(group_options.keys()))
        group_col = group_options[group_option]
        try:
            comparativo, comparativo_tipo = get_comparativo(df_filtered, group_col)
        except Exception as e:
            st.error(f"Erro ao agrupar dados: {e}")
            logger.exception(f"Erro no agrupamento: {e}")
            comparativo, comparativo_tipo = pd.DataFrame(), pd.DataFrame()
        
        st.subheader(f"Comparativo por Marca e {group_col}")
        if comparativo.empty:
            st.info("Não há dados disponíveis para o comparativo.")
        else:
            st.dataframe(comparativo.fillna(''))
        
        st.subheader(f"Comparativo por Marca, Tipo e {group_col}")
        if comparativo_tipo.empty:
            st.info("Não há dados disponíveis para o comparativo por marca, tipo e período.")
        else:
            st.dataframe(comparativo_tipo.fillna(''))
    
    with tabs[1]:
        st.subheader("Gráficos Interativos de Métricas")
        st.subheader("Média de Respostas por Marca")
        visualizer.gerar_grafico_interativo(df_filtered, "Média de Respostas por Marca", "Respostas", "Média de Respostas")
        st.subheader("Média de Engajamento por Marca")
        visualizer.gerar_grafico_interativo(df_filtered, "Média de Engajamento por Marca", "Engajamento Total", "Média de Engajamento")
    
    with tabs[2]:
        st.subheader("Relatórios e Downloads")
        relatorio_html = visualizer.gerar_relatorio_html(comparativo, comparativo_tipo)
        st.components.v1.html(relatorio_html, height=600, scrolling=True)
        st.download_button(
            label="Baixar Relatório HTML",
            data=relatorio_html,
            file_name="relatorio_stories.html",
            mime="text/html"
        )
        if st.button("Exportar Relatório para Excel"):
            processed_data = visualizer.exportar_excel(comparativo, comparativo_tipo)
            if processed_data:
                st.download_button("Download Excel", processed_data, "relatorio_stories.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    main()
