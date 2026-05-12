#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ===================================================================
# ETL COM PySpark - Spotify Américas
# ===================================================================
# Objetivo: Processar 1.8M+ linhas de forma distribuída
# Tecnologia: PySpark (Apache Spark)
# Uso: python pyspark/01_etl_pyspark.py
# ===================================================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
import pandas as pd
import time

# ===================================================================
# 1. MEDIR TEMPO DE EXECUÇÃO
# ===================================================================

start_time = time.time()

print("=" * 70)
print("🚀 SPOTIFY AMÉRICAS - ETL COM PySPARK")
print("=" * 70)

# ===================================================================
# 2. INICIAR SESSÃO SPARK
# ===================================================================

print("\n📌 1. Iniciando Spark Session...")
print("-" * 40)

# Criar Spark Session com otimizações
spark = SparkSession.builder \
    .appName("Spotify Americas Analysis") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.sql.autoBroadcastJoinThreshold", "-1") \
    .config("spark.sql.shuffle.partitions", "200") \
    .config("spark.executor.memory", "4g") \
    .config("spark.driver.memory", "4g") \
    .getOrCreate()

# Configurar nível de log
spark.sparkContext.setLogLevel("WARN")

print("✅ Spark Session iniciada com sucesso!")
print(f"   Versão Spark: {spark.version}")

# ===================================================================
# 3. DEFINIR SCHEMA (Otimiza leitura)
# ===================================================================

print("\n📌 2. Definindo schema dos dados...")
print("-" * 40)

schema = StructType([
    StructField("rank", IntegerType(), True),
    StructField("artist_names", StringType(), True),
    StructField("track_name", StringType(), True),
    StructField("release_date", StringType(), True),
    StructField("streams", DoubleType(), True),
    StructField("week", StringType(), True),
    StructField("country", StringType(), True),
    StructField("region", StringType(), True),
    StructField("language", StringType(), True),
    StructField("danceability", DoubleType(), True),
    StructField("valence", DoubleType(), True),
    StructField("energy", DoubleType(), True)
])

print(f"✅ Schema definido com {len(schema.fields)} colunas")

# ===================================================================
# 4. CARREGAR DADOS
# ===================================================================

print("\n📌 3. Carregando dados com PySpark...")
print("-" * 40)

# Caminho do arquivo (ajustar conforme necessário)
file_path = "/content/drive/MyDrive/final.csv"

try:
    # Carregar dados
    df_spark = spark.read \
        .option("header", "true") \
        .option("inferSchema", "false") \
        .schema(schema) \
        .csv(file_path)
    
    print(f"✅ Dados carregados!")
    print(f"   📊 Quantidade de partições: {df_spark.rdd.getNumPartitions()}")
    
    # Mostrar primeiras linhas
    print("\n📋 Exemplo de dados:")
    df_spark.show(3, truncate=50)
    
except Exception as e:
    print(f"❌ Erro ao carregar dados: {e}")
    print("   Verifique o caminho do arquivo e tente novamente.")
    spark.stop()
    exit(1)

# ===================================================================
# 5. PAÍSES DA AMÉRICA
# ===================================================================

print("\n📌 4. Filtrando países da América...")
print("-" * 40)

paises_america = [
    'United States', 'USA', 'Canada', 'Mexico',
    'Brazil', 'Brasil', 'Argentina', 'Chile', 
    'Peru', 'Colombia', 'Venezuela', 'Ecuador',
    'Bolivia', 'Paraguay', 'Uruguay', 'Costa Rica',
    'Panama', 'Guatemala', 'Dominican Republic', 'Cuba',
    'Jamaica', 'Haiti', 'Puerto Rico'
]

df_america = df_spark.filter(col("country").isin(paises_america))
total_registros = df_america.count()

print(f"✅ Registros das Américas: {total_registros:,}")

if total_registros == 0:
    print("⚠️ Nenhum registro encontrado! Verificando países disponíveis...")
    paises_disponiveis = df_spark.select("country").distinct().limit(10).collect()
    print(f"   Países disponíveis no dataset: {[row.country for row in paises_disponiveis]}")
    spark.stop()
    exit(1)

# ===================================================================
# 6. LIMPEZA E TRANSFORMAÇÕES
# ===================================================================

print("\n📌 5. Realizando limpeza e transformações...")
print("-" * 40)

# 6.1 Converter datas
df_america = df_america.withColumn("week", to_date(col("week"), "yyyy-MM-dd"))
df_america = df_america.withColumn("release_date", to_date(col("release_date"), "yyyy-MM-dd"))

# 6.2 Remover nulos em datas essenciais
before = df_america.count()
df_america = df_america.filter(col("week").isNotNull())
after = df_america.count()
print(f"   Removidas {before - after:,} linhas com week nula")

# 6.3 Remover duplicatas
before = df_america.count()
df_america = df_america.dropDuplicates(["track_name", "artist_names", "country", "week"])
after = df_america.count()
print(f"   Removidas {before - after:,} duplicatas")

# 6.4 Preencher nulos numéricos com mediana por país
print("\n   Preenchendo valores nulos...")

# Calcular medianas por país
medianas = df_america.groupBy("country").agg(
    expr("percentile_approx(streams, 0.5)").alias("median_streams"),
    expr("percentile_approx(danceability, 0.5)").alias("median_dance"),
    expr("percentile_approx(energy, 0.5)").alias("median_energy"),
    expr("percentile_approx(valence, 0.5)").alias("median_valence")
)

# Preencher nulos
df_america = df_america.join(medianas, on="country", how="left")
df_america = df_america.withColumn(
    "streams", coalesce(col("streams"), col("median_streams"))
).withColumn(
    "danceability", coalesce(col("danceability"), col("median_dance"))
).withColumn(
    "energy", coalesce(col("energy"), col("median_energy"))
).withColumn(
    "valence", coalesce(col("valence"), col("median_valence"))
)

# Remover colunas auxiliares
df_america = df_america.drop("median_streams", "median_dance", "median_energy", "median_valence")

# 6.5 Remover outliers de streams (percentil 99.5)
quantiles = df_america.approxQuantile("streams", [0.995], 0.01)
if quantiles:
    percentil_995 = quantiles[0]
    before = df_america.count()
    df_america = df_america.filter(col("streams") <= percentil_995)
    after = df_america.count()
    print(f"   Removidas {before - after:,} linhas com streams > {percentil_995:,.0f}")

print(f"\n✅ Shape após limpeza: {df_america.count():,} registros")

# ===================================================================
# 7. FEATURE ENGINEERING
# ===================================================================

print("\n📌 6. Feature Engineering...")
print("-" * 40)

# 7.1 Streams em milhões
df_america = df_america.withColumn("streams_millions", round(col("streams") / 1000000, 2))

# 7.2 Componentes da data
df_america = df_america.withColumn("year", year(col("week")))
df_america = df_america.withColumn("month", month(col("week")))
df_america = df_america.withColumn("day_of_week", dayofweek(col("week")))
df_america = df_america.withColumn("month_name", date_format(col("week"), "MMMM"))

# 7.3 Score de sucesso
df_america = df_america.withColumn(
    "success_score", 
    (lit(201) - col("rank")) * log1p(col("streams_millions"))
)

# 7.4 Perfil musical
df_america = df_america.withColumn(
    "music_profile",
    when((col("danceability") > 0.7) & (col("energy") > 0.7), "🔥 Ritmo Latino/Alta Energia")
    .when(col("danceability") > 0.7, "💃 Dançante")
    .when(col("energy") > 0.7, "⚡ Energética")
    .when(col("valence") > 0.7, "😊 Feliz/Positiva")
    .when(col("valence") < 0.3, "😢 Melancólica/Triste")
    .otherwise("🎵 Neutra/Equilibrada")
)

# 7.5 Sub-região
df_america = df_america.withColumn(
    "sub_region",
    when(col("country").isin(["United States", "USA", "Canada", "Mexico"]), "🌎 América do Norte")
    .when(col("country").isin(["Brazil", "Brasil", "Argentina", "Chile", "Peru", "Colombia", "Venezuela", "Ecuador", "Bolivia", "Paraguay", "Uruguay"]), "🗺️ América do Sul")
    .when(col("country").isin(["Costa Rica", "Panama", "Guatemala", "El Salvador", "Honduras", "Nicaragua"]), "🌏 América Central")
    .otherwise("🏝️ Caribe")
)

# 7.6 Grupo de rank
df_america = df_america.withColumn(
    "rank_group",
    when(col("rank") <= 10, "🏆 Top 10")
    .when(col("rank") <= 50, "📊 Top 11-50")
    .when(col("rank") <= 100, "📈 Top 51-100")
    .otherwise("📉 Top 101-200")
)

print(f"✅ Total de colunas: {len(df_america.columns)}")
print(f"   Novas colunas: streams_millions, year, month, success_score, music_profile, sub_region, rank_group")

# ===================================================================
# 8. AGREGAÇÕES
# ===================================================================

print("\n📌 7. Realizando agregações...")
print("-" * 40)

# 8.1 Top 10 músicas
print("\n🏆 TOP 10 MÚSICAS DAS AMÉRICAS:")
top_musicas = df_america.groupBy("track_name", "artist_names") \
    .agg(sum("streams_millions").alias("total_streams")) \
    .orderBy(col("total_streams").desc()) \
    .limit(10)

top_musicas.show(10, truncate=40)

# 8.2 Top 10 países
print("\n🌍 TOP 10 PAÍSES POR STREAMS:")
top_paises = df_america.groupBy("country") \
    .agg(
        sum("streams_millions").alias("total_streams"),
        count("track_name").alias("total_musicas")
    ) \
    .orderBy(col("total_streams").desc()) \
    .limit(10)

top_paises.show(10, truncate=False)

# 8.3 Top 10 artistas
print("\n🎤 TOP 10 ARTISTAS:")
top_artistas = df_america.groupBy("artist_names") \
    .agg(
        sum("streams_millions").alias("total_streams"),
        countDistinct("track_name").alias("musicas_distintas"),
        countDistinct("country").alias("paises_alcançados")
    ) \
    .orderBy(col("total_streams").desc()) \
    .limit(10)

top_artistas.show(10, truncate=35)

# 8.4 Análise por sub-região
print("\n🗺️ ANÁLISE POR SUB-REGIÃO:")
sub_regiao_stats = df_america.groupBy("sub_region") \
    .agg(
        sum("streams_millions").alias("total_streams"),
        avg("danceability").alias("media_danceability"),
        avg("energy").alias("media_energy"),
        avg("valence").alias("media_valence"),
        countDistinct("country").alias("total_paises")
    ) \
    .orderBy(col("total_streams").desc())

sub_regiao_stats.show(truncate=False)

# ===================================================================
# 9. CORRELAÇÕES
# ===================================================================

print("\n📌 8. Calculando correlações...")
print("-" * 40)

# Calcular correlações
corr_streams_rank = df_america.stat.corr("streams_millions", "rank")
corr_streams_dance = df_america.stat.corr("streams_millions", "danceability")
corr_streams_energy = df_america.stat.corr("streams_millions", "energy")
corr_streams_valence = df_america.stat.corr("streams_millions", "valence")

print(f"\n📊 Correlação com STREAMS:")
print(f"   • Rank: {corr_streams_rank:.3f} (negativo = melhor rank)")
print(f"   • Dançabilidade: {corr_streams_dance:.3f}")
print(f"   • Energia: {corr_streams_energy:.3f}")
print(f"   • Positividade: {corr_streams_valence:.3f}")

# ===================================================================
# 10. WINDOW FUNCTIONS - RANKING POR PAÍS
# ===================================================================

print("\n📌 9. Criando rankings por país (Window Functions)...")
print("-" * 40)

window_spec = Window.partitionBy("country").orderBy(col("streams_millions").desc())
df_with_rank = df_america.withColumn("rank_in_country", row_number().over(window_spec))

# Top 3 músicas por país
top_por_pais = df_with_rank.filter(col("rank_in_country") <= 3) \
    .select("country", "track_name", "artist_names", "streams_millions", "rank_in_country") \
    .orderBy("country", "rank_in_country")

print("Top 3 músicas por país (amostra):")
top_por_pais.show(15, truncate=40)

# ===================================================================
# 11. EXPORTAR RESULTADOS
# ===================================================================

print("\n📌 10. Exportando resultados...")
print("-" * 40)

# Criar pasta de saída
import os
output_dir = "/content/drive/MyDrive/spotify_americas_pyspark/"
os.makedirs(output_dir, exist_ok=True)

# Exportar dados limpos (limitado para memória)
df_pandas = df_america.limit(500000).toPandas()
df_pandas.to_csv(f"{output_dir}spotify_americas_pyspark.csv", index=False)
print(f"✅ spotify_americas_pyspark.csv salvo ({len(df_pandas):,} registros)")

# Exportar top músicas
top_musicas_pd = top_musicas.toPandas()
top_musicas_pd.to_csv(f"{output_dir}top_musicas_pyspark.csv", index=False)
print(f"✅ top_musicas_pyspark.csv salvo")

# Exportar top países
top_paises_pd = top_paises.toPandas()
top_paises_pd.to_csv(f"{output_dir}top_paises_pyspark.csv", index=False)
print(f"✅ top_paises_pyspark.csv salvo")

# Exportar top artistas
top_artistas_pd = top_artistas.toPandas()
top_artistas_pd.to_csv(f"{output_dir}top_artistas_pyspark.csv", index=False)
print(f"✅ top_artistas_pyspark.csv salvo")

# Exportar análise por sub-região
sub_regiao_pd = sub_regiao_stats.toPandas()
sub_regiao_pd.to_csv(f"{output_dir}analise_sub_regiao_pyspark.csv", index=False)
print(f"✅ analise_sub_regiao_pyspark.csv salvo")

# ===================================================================
# 12. ESTATÍSTICAS FINAIS
# ===================================================================

print("\n" + "=" * 70)
print("📊 ESTATÍSTICAS FINAIS - PySpark")
print("=" * 70)

# Contagens finais
total_registros = df_america.count()
total_paises = df_america.select("country").distinct().count()
total_musicas = df_america.select("track_name").distinct().count()
total_artistas = df_america.select("artist_names").distinct().count()
total_streams = df_america.agg(sum("streams_millions")).collect()[0][0]

print(f"""
✅ DATASET FINAL:
   • Total de registros: {total_registros:,}
   • Países representados: {total_paises}
   • Músicas únicas: {total_musicas:,}
   • Artistas únicos: {total_artistas:,}
   • Total de streams: {total_streams:.1f}M

📁 ARQUIVOS GERADOS:
   • spotify_americas_pyspark.csv
   • top_musicas_pyspark.csv
   • top_paises_pyspark.csv
   • top_artistas_pyspark.csv
   • analise_sub_regiao_pyspark.csv

📂 LOCALIZAÇÃO: {output_dir}
""")

# ===================================================================
# 13. TEMPO DE EXECUÇÃO
# ===================================================================

end_time = time.time()
execution_time = end_time - start_time

print(f"⏱️ Tempo total de execução: {execution_time:.2f} segundos ({execution_time/60:.2f} minutos)")

# ===================================================================
# 14. ENCERRAR SESSÃO SPARK
# ===================================================================

print("\n🛑 Encerrando Spark Session...")
spark.stop()
print("✅ Spark Session encerrada com sucesso!")

print("\n" + "=" * 70)
print("🎉 PySpark ETL concluído com sucesso!")
print("=" * 70)
