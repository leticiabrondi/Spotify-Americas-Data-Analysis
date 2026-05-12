#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ===================================================================
# AGREGAÇÕES OTIMIZADAS COM PySpark - Spotify Américas
# ===================================================================
# Objetivo: Demonstração de agregações avançadas e otimizações
# Uso: python pyspark/03_agregacoes_pyspark.py
# ===================================================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window
import time

start_time = time.time()

print("=" * 70)
print("⚡ AGREGAÇÕES OTIMIZADAS - PySPARK")
print("=" * 70)

# ===================================================================
# INICIAR SPARK SESSION
# ===================================================================

spark = SparkSession.builder \
    .appName("Spotify Americas Aggregations") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("✅ Spark Session iniciada!")

# ===================================================================
# CARREGAR DADOS
# ===================================================================

print("\n📌 Carregando dados...")

# Simular dados (em produção, carregar do arquivo)
# df = spark.read.parquet("caminho/para/dados.parquet")

# Para demonstração, vamos criar um DataFrame de exemplo
print("⚠️ Modo demonstração - criando dados de exemplo")

data = [
    (1, "Stay", "The Kid LAROI", "United States", 150.5, 0.75, 0.70, 0.65),
    (2, "Heat Waves", "Glass Animals", "United States", 120.3, 0.68, 0.72, 0.60),
    (3, "Bad Habits", "Ed Sheeran", "Canada", 110.2, 0.70, 0.68, 0.62),
    (4, "Levitating", "Dua Lipa", "Mexico", 105.8, 0.78, 0.75, 0.70),
    (5, "Montero", "Lil Nas X", "Brazil", 98.5, 0.72, 0.69, 0.58),
    (6, "Yonaguni", "Bad Bunny", "Argentina", 95.2, 0.80, 0.65, 0.72),
    (7, "Peaches", "Justin Bieber", "Colombia", 92.1, 0.74, 0.71, 0.68),
    (8, "Save Your Tears", "The Weeknd", "Canada", 88.7, 0.66, 0.64, 0.55),
    (9, "Kiss Me More", "Doja Cat", "United States", 85.3, 0.82, 0.73, 0.75),
    (10, "Good 4 U", "Olivia Rodrigo", "Brazil", 82.9, 0.64, 0.80, 0.48),
]

columns = ["rank", "track_name", "artist_names", "country", "streams_millions", 
           "danceability", "energy", "valence"]

df = spark.createDataFrame(data, columns)

print(f"✅ DataFrame criado: {df.count()} registros")

# ===================================================================
# 1. AGREGAÇÕES BÁSICAS
# ===================================================================

print("\n📌 1. Agregações Básicas")
print("-" * 40)

# Múltiplas agregações de uma vez
agregacoes = df.agg(
    count("*").alias("total_registros"),
    sum("streams_millions").alias("total_streams"),
    avg("streams_millions").alias("media_streams"),
    avg("danceability").alias("media_danceability"),
    avg("energy").alias("media_energy"),
    avg("valence").alias("media_valence"),
    min("streams_millions").alias("min_streams"),
    max("streams_millions").alias("max_streams")
)

print("📊 Estatísticas gerais:")
agregacoes.show()

# ===================================================================
# 2. GROUP BY COM MÚLTIPLAS COLUNAS
# ===================================================================

print("\n📌 2. Group By com Múltiplas Colunas")
print("-" * 40)

# Agrupar por país
stats_pais = df.groupBy("country") \
    .agg(
        sum("streams_millions").alias("total_streams"),
        avg("danceability").alias("media_danceability"),
        count("track_name").alias("total_musicas")
    ) \
    .orderBy(col("total_streams").desc())

print("🏆 Estatísticas por país:")
stats_pais.show()

# ===================================================================
# 3. PIVOT TABLES (Tabelas Dinâmicas)
# ===================================================================

print("\n📌 3. Pivot Tables")
print("-" * 40)

# Criar tabela dinâmica: países vs características
pivot_table = df.groupBy("country") \
    .pivot("rank") \
    .agg(first("streams_millions"))

print("📊 Tabela Dinâmica (Rank por País):")
pivot_table.show()

# ===================================================================
# 4. ROLLUP E CUBE (Hierarquias)
# ===================================================================

print("\n📌 4. ROLLUP - Agregação Hierárquica")
print("-" * 40)

# ROLLUP: soma em múltiplos níveis (país -> total geral)
rollup_result = df.rollup("country").agg(
    sum("streams_millions").alias("total_streams"),
    avg("danceability").alias("media_danceability")
).orderBy("country")

print("Resultado do ROLLUP (com totais):")
rollup_result.show()

# ===================================================================
# 5. WINDOW FUNCTIONS AVANÇADAS
# ===================================================================

print("\n📌 5. Window Functions - Rankings e Lags")
print("-" * 40)

# Ranking dentro de cada país
window_spec = Window.partitionBy("country").orderBy(col("streams_millions").desc())

df_with_rank = df.withColumn("rank_in_country", row_number().over(window_spec))
df_with_rank = df_with_rank.withColumn("lag_streams", lag("streams_millions").over(window_spec))

print("Ranking por país (com lag):")
df_with_rank.select("country", "track_name", "streams_millions", "rank_in_country", "lag_streams") \
    .orderBy("country", "rank_in_country") \
    .show()

# ===================================================================
# 6. AGREGAÇÕES COM FILTROS (FILTER AGGREGATIONS)
# ===================================================================

print("\n📌 6. Agregações Condicionais")
print("-" * 40)

# Média de streams para músicas dançantes vs não dançantes
stats_dance = df.agg(
    avg(when(col("danceability") > 0.7, col("streams_millions"))).alias("media_dancantes"),
    avg(when(col("danceability") <= 0.7, col("streams_millions"))).alias("media_nao_dancantes")
)

print("📊 Comparação: Dançantes vs Não Dançantes")
stats_dance.show()

# ===================================================================
# 7. AGREGAÇÕES COMPLEXAS (ARRAYS E STRUCTS)
# ===================================================================

print("\n📌 7. Agregações com Listas (Collect List)")
print("-" * 40)

# Coletar todas as músicas de cada país como lista
musicas_por_pais = df.groupBy("country") \
    .agg(
        collect_list("track_name").alias("musicas"),
        sum("streams_millions").alias("total_streams")
    )

print("Músicas agrupadas por país:")
musicas_por_pais.show(truncate=False)

# ===================================================================
# 8. OTIMIZAÇÕES - PARTITIONING E CACHING
# ===================================================================

print("\n📌 8. Otimizações para Performance")
print("-" * 40)

# Verificar partições antes
print(f"Partições antes: {df.rdd.getNumPartitions()}")

# Reparticionar para melhor performance
df_optimized = df.repartition(4)
print(f"Partições depois: {df_optimized.rdd.getNumPartitions()}")

# Cache para reuso
df_cached = df.cache()
df_cached.count()  # Forçar cache
print("✅ DataFrame cacheado na memória")

# ===================================================================
# 9. JOIN OPERATIONS (Demonstração)
# ===================================================================

print("\n📌 9. Join Operations")
print("-" * 40)

# Criar tabela de metadados de países
paises_metadata = [
    ("United States", "🌎 América do Norte", "US"),
    ("Canada", "🌎 América do Norte", "CA"),
    ("Mexico", "🌎 América do Norte", "MX"),
    ("Brazil", "🗺️ América do Sul", "BR"),
    ("Argentina", "🗺️ América do Sul", "AR"),
    ("Colombia", "🗺️ América do Sul", "CO"),
]

df_paises = spark.createDataFrame(paises_metadata, ["country", "sub_region", "code"])

# Join com os dados principais
df_completo = df.join(df_paises, on="country", how="left")

print("Dados com join de sub-região:")
df_completo.select("country", "sub_region", "track_name", "streams_millions").show()

# ===================================================================
# 10. RESUMO DAS AGREGAÇÕES
# ===================================================================

print("\n" + "=" * 70)
print("📊 RESUMO DAS DEMONSTRAÇÕES")
print("=" * 70)

print("""
✅ OPERAÇÕES DEMONSTRADAS:

   1. Agregações básicas (count, sum, avg, min, max)
   2. Group By com múltiplas colunas
   3. Pivot Tables (tabelas dinâmicas)
   4. ROLLUP e CUBE (agregações hierárquicas)
   5. Window Functions (rank, lag, lead)
   6. Agregações condicionais com when/otherwise
   7. Collect List (agrupar em listas)
   8. Otimizações: repartition e cache
   9. Join operations
   
🎯 PRÓXIMOS PASSOS:
   • Aplicar estas técnicas ao dataset completo
   • Usar broadcast joins para tabelas pequenas
   • Ajustar número de partições conforme necessidade
""")

# ===================================================================
# TEMPO DE EXECUÇÃO
# ===================================================================

end_time = time.time()
execution_time = end_time - start_time

print(f"⏱️ Tempo de execução: {execution_time:.2f} segundos")

# ===================================================================
# ENCERRAR
# ===================================================================

spark.stop()
print("\n🎉 Agregações PySpark concluídas!")
