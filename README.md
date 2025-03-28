# 📊 Instagram Stories Analytics Dashboard

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-239120?style=for-the-badge&logo=plotly&logoColor=white)

Aplicativo web para análise comparativa de métricas de Stories do Instagram com visualizações interativas e relatórios personalizáveis.

## 🚀 Funcionalidades Principais

- **Upload de CSVs** para ano atual e anterior
- **Dashboard Interativo** com 3 abas:
  - Dados consolidados com KPIs
  - Gráficos dinâmicos de engajamento
  - Geração de relatórios em HTML/Excel
- **Filtros Avançados** por:
  - Marcas específicas
  - Tipo de conteúdo
  - Período temporal
- **Sistema de Análise** com:
  - Cálculo automático de engajamento
  - Comparativo temporal (Mensal/Trimestral)
  - Detecção automática de marcas

## ⚙️ Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/InstaStories-Dashboard.git
cd instagram-analytics
```
2. Clone o repositório:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/MacOS
source venv/bin/activate
```
3. Instale as dependências:
```bash
pip install -r requirements.txt
```
4. ▶️ Como Executar
```bash
streamlit run app_streamlit_instagram_stories.py
```
📂 Estrutura de Arquivos

app.py - Código principal da aplicação

requirements.txt - Dependências do projeto

.gitignore - Arquivos ignorados no versionamento

/data - Pasta para armazenar CSVs de exemplo

📄 Licença

MIT License - Veja o arquivo [LICENSE](https://github.com/dencode7/InstaStories-Dashboard/blame/main/LICENSE) para detalhes.

🤝 Como Contribuir

Faça um Fork do projeto

Crie sua Branch (git checkout -b feature/nova-feature)

Commit suas mudanças (git commit -m 'Adiciona nova feature')

Push para a Branch (git push origin feature/nova-feature)
