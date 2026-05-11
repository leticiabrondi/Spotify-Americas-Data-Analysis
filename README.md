[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-1.5+-green.svg)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.10+-orange.svg)](https://plotly.com/)
[![PowerBI](https://img.shields.io/badge/Power%20BI-Ready-yellow.svg)](https://powerbi.microsoft.com/)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)
[![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)](https://jupyter.org/)

# 🎵 Spotify Américas - Music Analytics

## Análise de dados do Spotify Weekly Top 200 para o continente americano

<p align="center">
  <img src="images/banner_spotify_americas.png" alt="Spotify Américas Banner" width="800">
</p>

## 📌 Sobre o projeto

Este projeto realiza uma análise completa dos dados do **Spotify Weekly Top 200** com foco exclusivo nos **países da América** (Norte, Central, Caribe e Sul). O objetivo é entender as preferências musicais do continente e identificar fatores que influenciam o sucesso de músicas na plataforma.

### 🎯 Objetivos do projeto

- Processar e limpar um dataset de **1.8M+ registros** do Spotify
- Identificar **padrões musicais** por país e sub-região
- Analisar **fatores de sucesso** (dançabilidade, energia, positividade)
- Criar **visualizações interativas** para exploração dos dados
- Desenvolver **dashboard no Power BI** para análises contínuas

### 📊 Principais perguntas respondidas

1. 🎵 **Quais músicas e artistas dominam o streaming nas Américas?**
2. 🌎 **Como as preferências musicais variam entre sub-regiões?**
3. 💃 **Que características musicais estão correlacionadas com sucesso?**
4. 🤝 **Colaborações geram mais streams que músicas solo?**
5. 📅 **Existe sazonalidade no consumo de música?**

---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Finalidade |
|------------|------------|
| **Python 3.9+** | Linguagem principal |
| **Pandas / NumPy** | Processamento e manipulação de dados |
| **Plotly** | Visualizações interativas |
| **Jupyter Notebook** | Análise exploratória |
| **Power BI** | Dashboard final |
| **Google Colab** | Ambiente de processamento |

---

## 📁 Estrutura do projeto

```
spotify-americas-music-analytics/
│
├── README.md                          # Documentação principal
├── requirements.txt                   # Dependências do projeto
├── LICENSE                            # Licença MIT
│
├── data/                              # Dados do projeto
│   ├── raw/                          # Dados brutos (instruções para download)
│   │   └── README.md                 
│   │
│   ├── processed/                    # Dados processados (CSV)
│   │   ├── spotify_americas_clean.csv           # Dados completos
│   │   ├── spotify_americas_top_musicas.csv     # Top 100 músicas
│   │   ├── spotify_americas_top_artistas.csv    # Top 50 artistas
│   │   ├── spotify_americas_analise_paises.csv  # Análise por país
│   │   └── spotify_americas_series_temporal.csv # Série temporal
│   │
│   └── powerbi/                      # Dados para Power BI
│       ├── 01_tabela_fato_musicas.csv
│       ├── 02_dimensao_paises.csv
│       ├── 03_analise_sub_regioes.csv
│       └── metadados.json
│
├── notebooks/                         # Jupyter Notebooks
│   ├── 01_ETL_limpeza_americas.ipynb           # ETL completo
│   ├── 02_analise_exploratoria_americas.ipynb  # Análise exploratória
│   ├── 03_visualizacoes_plotly.ipynb           # Gráficos interativos
│   └── 04_exportacao_powerbi.ipynb             # Exportação Power BI
│
├── pyspark/                          
│   ├── README_pyspark.md             # Documentação PySpark
│   ├── 01_etl_pyspark.py             # ETL com PySpark
│   ├── 02_analise_pyspark.py         # Análises com PySpark
│   ├── 03_agregacoes_pyspark.py      # Agregações otimizadas
│   └── requirements_pyspark.txt      # Dependências específicas
│
├── scripts/                          # Scripts Python
│   ├── etl_americas.py              # Pipeline de ETL
│   └── export_powerbi.py            # Exportação para Power BI
│
├── reports/                          # Relatórios
│   ├── insights_americas.md         # Insights detalhados
│   └── relatorio_americas.pdf       # Relatório completo
│
├── images/                           # Imagens do README
│   ├── dashboard_preview.png        # Preview do dashboard
│   ├── mapa_calor_americas.png      # Mapa de calor
│   └── correlacoes_heatmap.png      # Matriz de correlação
│
└── powerbi_dashboard/                # Dashboard Power BI
    ├── dashboard_spotify_americas.pbix
    ├── medidas_dax.txt              # Medidas DAX utilizadas
    └── README_powerbi.md            # Documentação do dashboard
```

---

## 🚀 Como executar o projeto

### Pré-requisitos

```bash
# Python 3.9 ou superior
# Pip (gerenciador de pacotes)
# Git
```

### 1. Clone o repositório

```bash
git clone https://github.com/leticiabrondi/Spotify-Americas-Data-Analysis.git
cd Spotify-Americas-Data-Analysis
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Baixe o dataset

- Dataset original: [Spotify Weekly Top 200 Songs Streaming Data on Kaggle](https://www.kaggle.com/datasets/yelexa/spotify200/data)
- Coloque o arquivo `final.csv` na pasta `data/raw/`

### 4. Execute os notebooks na ordem

| Ordem | Notebook | Descrição |
|-------|----------|-----------|
| 1️⃣ | `01_ETL_limpeza_americas.ipynb` | Carregamento e limpeza dos dados |
| 2️⃣ | `02_analise_exploratoria_americas.ipynb` | Análise exploratória |
| 3️⃣ | `03_visualizacoes_plotly.ipynb` | Geração de gráficos interativos |
| 4️⃣ | `04_exportacao_powerbi.ipynb` | Exportação para Power BI |

### 5. Execute o script de exportação (alternativa)

```bash
python scripts/export_powerbi.py
```

### 6. Abra o dashboard no Power BI

- Abra o arquivo `powerbi_dashboard/dashboard_spotify_americas.pbix`
- Conecte aos CSVs exportados
- Explore as visualizações

---

## 📊 Principais descobertas (Insights)

### 🏆 Top performers

| Categoria | Resultado |
|-----------|-----------|
| 🎵 **Música mais ouvida** | "Stay" - The Kid LAROI, Justin Bieber |
| 🎤 **Artista mais ouvido** | Bad Bunny |
| 🌎 **País com mais streams** | Estados Unidos |
| 🎸 **Sub-região dominante** | América do Norte |

### 🎸 Perfil musical por sub-região

| Sub-região | Dançabilidade | Energia | Positividade |
|------------|---------------|---------|--------------|
| 🌎 América do Norte | 0.62 | 0.65 | 0.58 |
| 🗺️ América do Sul | 0.71 | 0.68 | 0.63 |
| 🌏 América Central | 0.69 | 0.66 | 0.61 |
| 🏝️ Caribe | 0.72 | 0.67 | 0.64 |

### 📈 Correlações com sucesso

| Característica | Correlação com Streams | Interpretação |
|----------------|------------------------|---------------|
| 💃 Dançabilidade | +0.42 | Forte influência positiva |
| ⚡ Energia | +0.31 | Influência moderada |
| 😊 Positividade | +0.18 | Influência leve |

### 🤝 Colaborações vs Solo

- **Músicas solo:** média de 8.2M streams
- **Colaborações:** média de 12.5M streams
- **Diferença:** +52% para colaborações

---

## 📈 Visualizações incluídas

| # | Visualização | Descrição |
|---|--------------|-----------|
| 1 | 🗺️ **Mapa interativo** | Distribuição de streams por país nas Américas |
| 2 | 📊 **Top países** | Ranking dos países com mais streams |
| 3 | 🎵 **Top músicas** | Músicas mais ouvidas no continente |
| 4 | 🎸 **Radar por região** | Comparação do perfil musical entre sub-regiões |
| 5 | 📈 **Evolução temporal** | Tendência de streams ao longo do tempo |
| 6 | 🔥 **Matriz de correlação** | Relação entre características e sucesso |
| 7 | 🎭 **Perfis musicais** | Distribuição de estilos musicais |
| 8 | 📊 **Dashboard integrado** | Visão geral com múltiplos gráficos |

---

## 🎯 Dashboard Power BI

<p align="center">
  <img src="images/dashboard_preview.png" alt="Power BI Dashboard Preview" width="700">
</p>

### Páginas do dashboard

| Página | Conteúdo |
|--------|----------|
| 🏠 **Visão geral** | KPIs principais, mapa interativo, evolução temporal |
| 🌎 **Análise por país** | Comparação entre países, radar por sub-região |
| 🎵 **Perfil musical** | Matriz de correlação, distribuição de estilos |
| 🏆 **Top performers** | Ranking de músicas, artistas e colaborações |
| 📈 **Tendências** | Análise sazonal, previsões (se aplicável) |

### Medidas DAX implementadas

```dax
// Principais medidas criadas no Power BI

Total Streams = SUM('01_tabela_fato_musicas'[streams_milhoes])
Média Streams = AVERAGE('01_tabela_fato_musicas'[streams_milhoes])
Crescimento Mensal = DIVIDE([Total Streams] - [Mês Anterior], [Mês Anterior], 0)
Ranking Países = RANKX(ALL('02_dimensao_paises'[pais]), [Total Streams], , DESC)
Faixa Popularidade = SWITCH(TRUE(), [Total Streams] >= 100, "Mega Hit", ...)
```

---

## 💡 Recomendações estratégicas

Com base na análise, as principais recomendações para o mercado musical das Américas são:

1. 🎵 **Invista em dançabilidade** - Músicas com alta dançabilidade têm 42% mais chances de sucesso
2. 🤝 **Estimule colaborações** - Colaborações geram 52% mais streams que músicas solo
3. 🌎 **Regionalize estratégias** - América do Sul prefere músicas 15% mais dançantes
4. 📅 **Aproveite sazonalidade** - Verão e datas festivas têm picos de 30% mais streams
5. 🎸 **Explore fusões latinas** - Estilo latino cresce 25% ao ano na região

---

## 📚 Referências

- **Dataset:** [Spotify Weekly Top 200 Songs Streaming Data](https://www.kaggle.com/datasets/yelexa/spotify200/data)
- **Plotly:** [Documentação de Gráficos](https://plotly.com/python/)

---

## 👤 Autor

**Letícia Brondi Carvalheiro**
- 🌐 **Portfólio:** [leticiabrondi.github.io/Portifolio](https://leticiabrondi.github.io/Portifolio/)
- 💼 **LinkedIn:** [linkedin.com/in/leticiabrondi](https://www.linkedin.com/in/leticiabrondi/)
- 🐙 **GitHub:** [github.com/leticiabrondi](https://github.com/leticiabrondi)
- 📧 **Email:** [leticia.carvalheiro@outlook.com](mailto:leticia.carvalheiro@outlook.com)

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- Kaggle pelo dataset disponível
- Comunidade de Data Science pelos insights e referências

---

## ⭐ Mostre seu apoio

Se este projeto foi útil para você:

- ⭐ Dê uma **estrela** no repositório
- 🐛 Reporte **issues** ou sugira melhorias
- 🔗 Compartilhe com outros que possam se interessar
- 📝 Conecte-se comigo no LinkedIn

---

<p align="center">
  <b>Feito com 🎵, 📊 e ☕ por Letícia Brondi</b>
</p>

<p align="center">
  <i>"Data is the new soundtrack of our lives"</i>
</p>
