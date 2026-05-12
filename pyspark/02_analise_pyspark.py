#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ===================================================================
# ANÁLISES COM PySpark - Spotify Américas
# ===================================================================
# Objetivo: Análises avançadas usando processamento distribuído
# Uso: python pyspark/02_analise_pyspark.py
# ===================================================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window
import time

start_time = time.time()

print("=" * 70)
print("📊 SPOTIFY AMÉRICAS - ANÁLISES AVANÇADAS COM PySPARK")
print("=" * 70)

# ===================================================================
# INICIAR SPARK SESSION
# ===================================================================

print("\n📌 Iniciando Spark Session...")
print("-" * 40)

spark = SparkSession.builder \
    .appName("Spotify Americas Analysis Advanced") \
    .config("spark.sql.adaptive.enabled", "true") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

print("✅ Spark Session iniciada!")

# ===================================================================
# CARREGAR DADOS
# ===================================================================

print("\n📌 Carregando dados processados...")
print("-" * 40)

# Tentar carregar do Parquet (mais eficiente)
try:
    df = spark.read.parquet("/content/drive/MyDrive/spotify_americas_pyspark/spotify_americas_pyspark.parquet")
    print("✅ Dados carregados do Parquet!")
except:
    # Fallback para CSV
    df = spark.read.csv("/content/drive/MyDrive/spotify_americas_pyspark/spotify_americas_pyspark.csv", 
                        header=True, inferSchema=True)
    print("✅ Dados carregados do CSV!")

print(f"📊 Shape: {df.count():,} registros")

# ===================================================================
# ANÁLISE 1: CONCENTRAÇÃO DE MERCADO (PARETO)
# ===================================================================

print("\n📌 ANÁLISE 1: Concentração de Mercado (Lei de Pareto)")
print("-" * 40)

# Top 20% das músicas respondem por quantos % dos streams?
total_streams = df.agg(sum("streams_millions")).collect()[0][0]

# Ordenar por streams e calcular acumulado
df_ordenado = df.orderBy(col("streams_millions").desc())
df_ordenado = df_ordenado.withColumn("streams_acumulado", 
                                      sum("streams_millions").over(Window.orderBy(lit(1))))

# Calcular percentuais
df_percentual = df_ordenado.withColumn("percentual_streams", 
                                        col("streams_acumulado") / total_streams * 100)
df_percentual = df_percentual.withColumn("percentual_musicas", 
                                          (row_number().over(Window.orderBy(lit(1))) / df.count()) * 100)

# Encontrar ponto onde atinge 80%
df_filtered = df_percentual.filter(col("percentual_streams") >= 80).limit(1)
resultado = df_filtered.select("percentual_musicas").collect()

if resultado:
    pct_musicas = resultado[0][0]
    print(f"🎯 {pct_musicas:.1f}% das músicas respondem por 80% dos streams")
    print(f"   (Lei de Pareto no streaming musical)")

# ===================================================================
# ANÁLISE 2: SAZONALIDADE
# ===================================================================

print("\n📌 ANÁLISE 2: Sazonalidade por Mês")
print("-" * 40)

# Streams por mês
streams_mensal = df.groupBy("month", "month_name") \
    .agg(
        sum("streams_millions").alias("total_streams"),
        avg("streams_millions").alias("media_streams")
    ) \
    .orderBy("month")

streams_mensal.show(12, truncate=False)

# Mês com mais streams
mes_top = streams_mensal.orderBy(col("total_streams").desc()).first()
print(f"🏆 Mês com mais streams: {mes_top['month_name']} ({mes_top['total_streams']:.1f}M)")

# ===================================================================
# ANÁLISE 3: MELHOR DIA PARA LANÇAMENTOS
# ===================================================================

print("\n📌 ANÁLISE 3: Melhor Dia para Lançamentos")
print("-" * 40)

# Média de streams por dia da semana
media_dia = df.groupBy("day_of_week") \
    .agg(avg("streams_millions").alias("media_streams")) \
    .orderBy(col("media_streams").desc())

dias_semana = {1: "Domingo", 2: "Segunda", 3: "Terça", 4: "Quarta", 
               5: "Quinta", 6: "Sexta", 7: "Sábado"}

print("\n📊 Média de streams por dia da semana:")
for row in media_dia.collect():
    dia_nome = dias_semana.get(row['day_of_week'], "Desconhecido")
    print(f"   • {dia_nome}: {row['media_streams']:.2f}M streams")

# ===================================================================
# ANÁLISE 4: CORRELAÇÕES DETALHADAS
# ===================================================================

print("\n📌 ANÁLISE 4: Correlações Detalhadas por Sub-região")
print("-" * 40)

# Calcular correlações por sub-região
regioes = df.select("sub_region").distinct().collect()

for regiao in regioes:
    regiao_nome = regiao['sub_region']
    df_regiao = df.filter(col("sub_region") == regiao_nome)
    
    if df_regiao.count() > 0:
        corr_dance = df_regiao.stat.corr("streams_millions", "danceability")
        corr_energy = df_regiao.stat.corr("streams_millions", "energy")
        
        print(f"\n📍 {regiao_nome}:")
        print(f"   • Dançabilidade vs Sucesso: {corr_dance:.3f}")
        print(f"   • Energia vs Sucesso: {corr_energy:.3f}")

# ===================================================================
# ANÁLISE 5: ARTISTAS MAIS VERSÁTEIS
# ===================================================================

print("\n📌 ANÁLISE 5: Artistas Mais Versáteis (mais países)")
print("-" * 40)

# Artistas que aparecem em mais países
artistas_versateis = df.groupBy("artist_names") \
    .agg(countDistinct("country").alias("paises_diferentes")) \
    .orderBy(col("paises_diferentes").desc()) \
    .limit(10)

print("\n🏆 Artistas com maior alcance geográfico:")
artistas_versateis.show(10, truncate=35)

# ===================================================================
# ANÁLISE 6: MÚSICAS MAIS LONGEVAS
# ===================================================================

print("\n📌 ANÁLISE 6: Músicas Mais Longevas (mais semanas no chart)")
print("-" * 40)

# Contar semanas por música
musicas_longevas = df.groupBy("track_name", "artist_names") \
    .agg(countDistinct("week").alias("semanas_no_chart")) \
    .orderBy(col("semanas_no_chart").desc()) \
    .limit(10)

print("\n🏆 Músicas com mais semanas no Top 200:")
musicas_longevas.show(10, truncate=40)

# ===================================================================
# ANÁLISE 7: COMPARAÇÃO PAÍSES FRONTEIRA
# ===================================================================

print("\n📌 ANÁLISE 7: Comparação Países Fronteiriços")
print("-" * 40)

# Comparar EUA vs Canadá
eua = df.filter(col("country") == "United States")
canada = df.filter(col("country") == "Canada")

stats_eua = eua.agg(
    avg("danceability").alias("dance_eua"),
    avg("energy").alias("energy_eua"),
    avg("valence").alias("valence_eua"),
    avg("streams_millions").alias("streams_eua")
).collect()[0]

stats_canada = canada.agg(
    avg("danceability").alias("dance_canada"),
    avg("energy").alias("energy_canada"),
    avg("valence").alias("valence_canada"),
    avg("streams_millions").alias("streams_canada")
).collect()[0]

print("\n📊 EUA vs CANADÁ:")
print(f"   Dançabilidade: EUA {stats_eua['dance_eua']:.3f} vs Canadá {stats_canada['dance_canada']:.3f}")
print(f"   Energia: EUA {stats_eua['energy_eua']:.3f} vs Canadá {stats_canada['energy_canada']:.3f}")
print(f"   Positividade: EUA {stats_eua['valence_eua']:.3f} vs Canadá {stats_canada['valence_canada']:.3f}")
print(f"   Média streams: EUA {stats_eua['streams_eua']:.2f}M vs Canadá {stats_canada['streams_canada']:.2f}M")

# ===================================================================
# TEMPO DE EXECUÇÃO
# ===================================================================

end_time = time.time()
execution_time = end_time - start_time

print("\n" + "=" * 70)
print(f"✅ Análises concluídas em {execution_time:.2f} segundos ({execution_time/60:.2f} minutos)")
print("=" * 70)

# ===================================================================
# ENCERRAR
# ===================================================================

spark.stop()
print("\n🎉 PySpark Análises concluídas com sucesso!")
