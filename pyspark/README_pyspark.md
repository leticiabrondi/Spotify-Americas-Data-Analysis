# 🚀 PySpark - Processamento Distribuído Spotify Américas

## 📌 Sobre esta pasta

Esta pasta contém a versão **PySpark** do projeto Spotify Américas, demonstrando habilidades em **processamento distribuído** e **Big Data**.

### 🎯 Objetivos

- Processar **1.8M+ registros** de forma distribuída
- Demonstrar uso de **Spark SQL e DataFrames**
- Aplicar **transformações em escala**
- Utilizar **Window Functions** para rankings
- Calcular **correlações** em big data

## 🛠️ Tecnologias

- **Apache Spark 3.x**
- **PySpark**
- **Google Colab / Databricks** (ambiente)

## 📂 Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `01_etl_pyspark.py` | ETL completo com PySpark |
| `02_analise_pyspark.py` | Análises e agregações |
| `03_agregacoes_pyspark.py` | Agregações otimizadas |
| `requirements_pyspark.txt` | Dependências |

## 🚀 Como executar

### No Google Colab

```python
# Instalar Java e Spark
!apt-get install openjdk-11-jdk-headless -qq > /dev/null
!wget -q https://archive.apache.org/dist/spark/spark-3.3.0/spark-3.3.0-bin-hadoop3.tgz
!tar xf spark-3.3.0-bin-hadoop3.tgz
!pip install -q findspark

import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-3.3.0-bin-hadoop3"

import findspark
findspark.init()
```

### Executar o script

```bash
python pyspark/01_etl_pyspark.py
```

## 📊 Vantagens do PySpark

| Operação | Pandas | PySpark |
|----------|--------|---------|
| Limite de memória | ~2-5GB | Distribuído |
| Processamento | Sequencial | Paralelo |
| Tempo (1.8M linhas) | ~5-10 min | ~1-2 min |
| Escalabilidade | Limitada | Horizontal |

## ✅ Funcionalidades Demonstradas

- [x] Leitura de dados com schema otimizado
- [x] Filtros e transformações em escala
- [x] Agregações com groupBy
- [x] Window Functions (rankings)
- [x] Cálculo de correlações
- [x] Exportação para CSV/Parquet
- [x] Otimização de partições

## 📈 Performance

```python
# Exemplo de otimização
df_optimized = df.repartition(200)  # Controlar paralelismo
df_cached = df.cache()              # Cache para reuso
df_filtered = df.filter(...)         # Push-down predicates
```

## 🔗 Links Úteis

- [Documentação PySpark](https://spark.apache.org/docs/latest/api/python/)
- [Spark SQL Guide](https://spark.apache.org/sql/)
- [Databricks - Spark Performance Tuning](https://docs.databricks.com/optimization/index.html)
