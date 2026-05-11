# 📁 Dados Brutos - Spotify Weekly Top 200

## 📌 Sobre esta pasta

Esta pasta contém os **dados brutos** do projeto Spotify Américas. Os arquivos aqui são os originais, **sem nenhum processamento ou limpeza**.

⚠️ **ATENÇÃO:** Devido ao tamanho dos arquivos, eles NÃO estão versionados no GitHub. Siga as instruções abaixo para baixar os dados.

## 📊 Dataset Original

| Propriedade | Descrição |
|-------------|-----------|
| **Nome** | Spotify Weekly Top 200 Songs Streaming Data |
| **Fonte** | Kaggle |
| **Tamanho** | ~2.5 GB (CSV) |
| **Registros** | 1.787.999 linhas |
| **Colunas** | 36 colunas |
| **Período** | 2016-12-29 a 2022-07-14 |
| **Licença** | Uso educacional/pessoal |

## 📥 Como Baixar os Dados

### Opção 1: Kaggle (Recomendado)

1. Acesse o dataset no Kaggle:
   🔗 [Spotify Weekly Top 200 Songs Streaming Data](https://www.kaggle.com/datasets/spotify-weekly-top-200)

2. Faça login/registre-se no Kaggle

3. Clique em **"Download"**

4. Extraia o arquivo `final.csv` para esta pasta

### Opção 2: Google Drive (Se já tiver acesso)

```python
# Se o arquivo já estiver no seu Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Copiar para a pasta atual
!cp /content/drive/MyDrive/final.csv ./data/raw/
```

### Opção 3: Download via Python (Kaggle API)

```python
# Instalar Kaggle API
!pip install kaggle

# Configurar API (necessário token do Kaggle)
!mkdir -p ~/.kaggle
!cp /content/drive/MyDrive/kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

# Baixar dataset
!kaggle datasets download -d spotify-weekly-top-200
!unzip spotify-weekly-top-200.zip -d data/raw/
```

## 📋 Estrutura esperada

Após o download, a estrutura deve ficar assim:

```
data/
└── raw/
    └── final.csv          # Dataset principal (~2.5 GB)
```

## 📊 Descrição do Dataset

O arquivo `final.csv` contém os seguintes campos:

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `uri` | string | Spotify URI da música |
| `rank` | int | Posição no ranking (1-200) |
| `artist_names` | string | Nome(s) do(s) artista(s) |
| `artists_num` | int | Número de artistas na música |
| `artist_individual` | string | Artista individual (para splits) |
| `artist_id` | string | Spotify ID do artista |
| `artist_genre` | string | Gênero musical do artista |
| `artist_img` | string | URL da imagem do artista |
| `collab` | int | 1 = colaboração, 0 = solo |
| `track_name` | string | Nome da música |
| `release_date` | date | Data de lançamento |
| `album_num_tracks` | int | Total de faixas no álbum |
| `album_cover` | string | URL da capa do álbum |
| `source` | string | Gravadora |
| `peak_rank` | int | Melhor posição alcançada |
| `previous_rank` | int | Posição na semana anterior |
| `weeks_on_chart` | int | Semanas no chart |
| `streams` | float | Streams na semana |
| `week` | date | Semana da coleta |
| `danceability` | float | Dançabilidade (0-1) |
| `energy` | float | Energia (0-1) |
| `key` | int | Tom da música |
| `mode` | int | Modo (maior/menor) |
| `loudness` | float | Loudness (dB) |
| `speechiness` | float | Speechiness (0-1) |
| `acousticness` | float | Acousticness (0-1) |
| `instrumentalness` | float | Instrumentalness (0-1) |
| `liveness` | float | Liveness (0-1) |
| `valence` | float | Valence/positividade (0-1) |
| `tempo` | float | Tempo (BPM) |
| `duration` | float | Duração (ms) |
| `country` | string | País do chart |
| `region` | string | Região do país |
| `language` | string | Idioma do país |
| `pivot` | int | Indicador de split de artistas |

## 🎯 Países da América no Dataset

O dataset contém dados dos seguintes países do continente americano:

### América do Norte
- United States / USA
- Canada
- Mexico

### América Central
- Guatemala
- Belize
- Honduras
- El Salvador
- Nicaragua
- Costa Rica
- Panama

### Caribe
- Cuba
- Jamaica
- Haiti
- Dominican Republic
- Puerto Rico
- Bahamas
- Trinidad and Tobago
- Barbados

### América do Sul
- Brazil / Brasil
- Argentina
- Chile
- Peru
- Colombia
- Venezuela
- Ecuador
- Bolivia
- Paraguay
- Uruguay
- Guyana
- Suriname

## ⚠️ Avisos importantes

1. **Arquivo grande:** O CSV tem ~2.5 GB. Certifique-se de ter espaço em disco suficiente.

2. **Memória:** Processar o arquivo completo pode exigir 8-16 GB de RAM.

3. **Não versionar:** Este arquivo NÃO deve ser commitado no GitHub.

4. **Git ignore:** O arquivo já está incluído no `.gitignore`:

```gitignore
# Ignorar dados brutos
data/raw/*.csv
data/raw/*.zip
*.csv
```

## 🔍 Verificação rápida

Após baixar o arquivo, execute este código para verificar se está correto:

```python
import pandas as pd

# Verificar se o arquivo existe
import os
if os.path.exists('data/raw/final.csv'):
    print("✅ Arquivo encontrado!")
    
    # Verificar tamanho
    tamanho_mb = os.path.getsize('data/raw/final.csv') / 1024**2
    print(f"📊 Tamanho: {tamanho_mb:.1f} MB")
    
    # Verificar primeiras linhas
    df_sample = pd.read_csv('data/raw/final.csv', nrows=5)
    print(f"\n📋 Shape esperado: ~1.8M linhas")
    print(f"\n🔍 Primeiras linhas:")
    print(df_sample.head())
else:
    print("❌ Arquivo não encontrado! Baixe os dados primeiro.")
```

## 📚 Referências

- [Dataset no Kaggle](https://www.kaggle.com/datasets/spotify-weekly-top-200)
- [Spotify API Documentation](https://developer.spotify.com/documentation/web-api/)
- [Spotify Audio Features](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)

---

**Após baixar os dados, prossiga para o notebook `01_ETL_limpeza_americas.ipynb` para iniciar o processamento!** 🚀
