# 📁 Dados Processados - Spotify Américas

## 📌 Sobre esta pasta

Esta pasta contém os **dados já processados e limpos** do projeto Spotify Américas. Os arquivos aqui são o resultado da execução do notebook `01_ETL_limpeza_americas.ipynb` e estão prontos para análise, visualização e importação no Power BI.

## 📊 Arquivos Disponíveis

| Arquivo | Descrição | Registros | Tamanho |
|---------|-----------|-----------|---------|
| `spotify_americas_clean.csv` | Dados completos limpos | ~500k linhas | ~200 MB |
| `spotify_americas_clean.parquet` | Dados completos (formato otimizado) | ~500k linhas | ~50 MB |
| `spotify_americas_top_musicas.csv` | Top 100 músicas | 100 | ~10 KB |
| `spotify_americas_top_artistas.csv` | Top 50 artistas | 50 | ~5 KB |
| `spotify_americas_analise_paises.csv` | Métricas por país | ~20 países | ~5 KB |
| `spotify_americas_series_temporal.csv` | Série temporal semanal | ~70 semanas | ~15 KB |

## 📋 Detalhamento dos Arquivos

### 1. `spotify_americas_clean.csv` / `.parquet`

**Dados principais do projeto** - todas as músicas das Américas após limpeza e feature engineering.

| Coluna | Descrição | Tipo |
|--------|-----------|------|
| `rank` | Posição no ranking (1-200) | int |
| `artist_names` | Nome(s) do(s) artista(s) | string |
| `track_name` | Nome da música | string |
| `release_date` | Data de lançamento | date |
| `streams` | Streams na semana | float |
| `streams_millions` | Streams em milhões | float |
| `week` | Semana da coleta | date |
| `country` | País | string |
| `sub_region` | Sub-região das Américas | string |
| `danceability` | Dançabilidade (0-1) | float |
| `energy` | Energia (0-1) | float |
| `valence` | Positividade (0-1) | float |
| `year` | Ano | int |
| `month` | Mês | int |
| `month_name` | Nome do mês | string |
| `success_score` | Score de sucesso | float |
| `music_profile` | Perfil musical categorizado | string |
| `rank_group` | Grupo do ranking | string |
| `is_latin_style` | Indicador de estilo latino (0/1) | int |

### 2. `spotify_americas_top_musicas.csv`

**Top 100 músicas mais ouvidas** nas Américas.

| Coluna | Descrição |
|--------|-----------|
| `track_name` | Nome da música |
| `artist_names` | Nome(s) do(s) artista(s) |
| `total_streams_millions` | Total de streams em milhões |
| `min_rank` | Melhor posição no ranking |
| `countries_reached` | Número de países onde apareceu |

### 3. `spotify_americas_top_artistas.csv`

**Top 50 artistas mais ouvidos** nas Américas.

| Coluna | Descrição |
|--------|-----------|
| `artist_names` | Nome do artista |
| `total_streams_millions` | Total de streams em milhões |
| `distinct_tracks` | Número de músicas distintas |
| `countries_reached` | Número de países onde apareceu |
| `primary_sub_region` | Sub-região principal do artista |

### 4. `spotify_americas_analise_paises.csv`

**Métricas agregadas por país** das Américas.

| Coluna | Descrição |
|--------|-----------|
| `country` | País |
| `sub_region` | Sub-região |
| `total_streams_millions` | Total de streams |
| `avg_streams_per_track` | Média de streams por música |
| `avg_danceability` | Dançabilidade média |
| `avg_energy` | Energia média |
| `avg_valence` | Positividade média |
| `avg_rank` | Rank médio |
| `total_tracks` | Total de músicas |
| `total_artists` | Total de artistas únicos |

### 5. `spotify_americas_series_temporal.csv`

**Série temporal semanal** para análise de evolução.

| Coluna | Descrição |
|--------|-----------|
| `week` | Semana (data) |
| `year` | Ano |
| `month` | Mês |
| `total_streams_millions` | Total de streams na semana |
| `avg_rank` | Rank médio na semana |
| `unique_tracks` | Número de músicas distintas |
| `unique_artists` | Número de artistas distintos |

## 🚀 Como Usar Estes Dados

### Em Python/Pandas

```python
import pandas as pd

# Carregar dados completos (recomendado usar Parquet)
df = pd.read_parquet('data/processed/spotify_americas_clean.parquet')

# Ou carregar CSV
df = pd.read_csv('data/processed/spotify_americas_clean.csv')

# Carregar arquivos específicos
top_musicas = pd.read_csv('data/processed/spotify_americas_top_musicas.csv')
top_artistas = pd.read_csv('data/processed/spotify_americas_top_artistas.csv')
analise_paises = pd.read_csv('data/processed/spotify_americas_analise_paises.csv')
```

### Em Power BI

1. Abra o Power BI Desktop
2. Clique em **"Obter Dados"** → **"Texto/CSV"**
3. Selecione os arquivos desejados
4. Configure os relacionamentos entre as tabelas:

```
tabela_fato (spotify_americas_clean)
    ├── país → dimensão_paises (country)
    ├── música → top_musicas (track_name)
    └── artista → top_artistas (artist_names)
```

### Em Excel / Google Sheets

1. Abra o arquivo CSV diretamente
2. Use **"Dados"** → **"De texto/CSV"** para importar

## 📊 Estatísticas dos Dados Processados

```python
# Código para verificar as estatísticas
import pandas as pd

df = pd.read_parquet('data/processed/spotify_americas_clean.parquet')

print(f"📊 Total de registros: {len(df):,}")
print(f"🌍 Países: {df['country'].nunique()}")
print(f"🎵 Músicas: {df['track_name'].nunique():,}")
print(f"🎤 Artistas: {df['artist_names'].nunique():,}")
print(f"📅 Período: {df['week'].min()} a {df['week'].max()}")
print(f"💰 Total streams: {df['streams_millions'].sum():.1f}M")
```

## 🔄 Regenerar os Dados

Se precisar regenerar estes arquivos, execute o notebook:

```bash
jupyter notebook notebooks/01_ETL_limpeza_americas.ipynb
```

Ou execute o script Python:

```bash
python scripts/etl_americas.py
```

## 💾 Otimização de Memória

### Por que usar Parquet?

| Formato | Tamanho | Velocidade de Leitura | Compatibilidade |
|---------|---------|----------------------|-----------------|
| **CSV** | ~200 MB | Lento | Universal |
| **Parquet** | ~50 MB | Rápido | Python/Pandas/Spark |

**Recomendação:** Use o arquivo `.parquet` para análises em Python e o `.csv` para Power BI/Excel.

### Carregamento Otimizado

```python
# Carregar apenas colunas necessárias
colunas = ['track_name', 'artist_names', 'country', 'streams_millions']
df = pd.read_parquet('data/processed/spotify_americas_clean.parquet', columns=colunas)

# Carregar em chunks (para memória limitada)
chunks = pd.read_csv('data/processed/spotify_americas_clean.csv', chunksize=50000)
```

## ✅ Validação dos Dados

Execute este código para validar a integridade dos dados:

```python
import pandas as pd

def validar_dados():
    """Verifica a integridade dos dados processados"""
    
    df = pd.read_parquet('data/processed/spotify_americas_clean.parquet')
    
    checks = {
        "Sem valores nulos": df.isnull().sum().sum() == 0,
        "Rank entre 1 e 200": df['rank'].between(1, 200).all(),
        "Streams positivos": (df['streams'] > 0).all(),
        "Dançabilidade entre 0 e 1": df['danceability'].between(0, 1).all(),
    }
    
    print("🔍 VALIDAÇÃO DOS DADOS:")
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}")
    
    return all(checks.values())

valido = validar_dados()
print(f"\n📊 Dados válidos: {valido}")
```

## 📁 Estrutura Esperada

```
data/
└── processed/
    ├── spotify_americas_clean.parquet     # Dados completos (recomendado)
    ├── spotify_americas_clean.csv         # Dados completos (backup)
    ├── spotify_americas_top_musicas.csv   # Top 100 músicas
    ├── spotify_americas_top_artistas.csv  # Top 50 artistas
    ├── spotify_americas_analise_paises.csv # Análise por país
    └── spotify_americas_series_temporal.csv # Série temporal
```

## 🔗 Relacionamento com Outras Pastas

| Pasta | Relação |
|-------|---------|
| `data/raw/` | Dados brutos de origem |
| `notebooks/` | Notebooks que geraram estes dados |
| `powerbi_dashboard/` | Dashboard que utiliza estes dados |

## ⚠️ Importante

- Estes arquivos são **gerados automaticamente** pelos notebooks
- Não edite manualmente - execute o ETL novamente para atualizar
- Os arquivos `.parquet` são mais eficientes para Python
- Os arquivos `.csv` são mais compatíveis com outras ferramentas

---

**Os dados estão prontos para análise! Prossiga para os notebooks de visualização.** 📊🚀
