#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ===================================================================
# ETL PIPELINE - Spotify Américas
# ===================================================================
# Objetivo: Pipeline completo de ETL para dados do Spotify
# Uso: python scripts/etl_americas.py
# ===================================================================

import pandas as pd
import numpy as np
import os
import sys
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# Configurações
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', '{:.2f}'.format)

# ===================================================================
# CONFIGURAÇÕES
# ===================================================================

# Lista de países da América
PAISES_AMERICA = [
    # América do Norte
    'United States', 'USA', 'Canada', 'Mexico',
    # América Central
    'Guatemala', 'Belize', 'Honduras', 'El Salvador', 'Nicaragua',
    'Costa Rica', 'Panama',
    # Caribe
    'Cuba', 'Jamaica', 'Haiti', 'Dominican Republic', 'Puerto Rico',
    'Bahamas', 'Trinidad and Tobago', 'Barbados',
    # América do Sul
    'Brazil', 'Brasil', 'Argentina', 'Chile', 'Peru', 'Colombia',
    'Venezuela', 'Ecuador', 'Bolivia', 'Paraguay', 'Uruguay', 'Guyana'
]

# Colunas selecionadas
COLUNAS_SELECIONADAS = [
    'rank', 'artist_names', 'track_name', 'release_date',
    'streams', 'week', 'country', 'region', 'language',
    'danceability', 'valence', 'energy'
]

# ===================================================================
# FUNÇÕES DE LIMPEZA
# ===================================================================

def convert_types(df):
    """Converte tipos de dados das colunas"""
    print("🔄 Convertendo tipos de dados...")
    
    # Converter colunas numéricas
    numeric_cols = ['rank', 'streams', 'danceability', 'energy', 'valence']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Converter datas
    if 'week' in df.columns:
        df['week'] = pd.to_datetime(df['week'], errors='coerce')
    if 'release_date' in df.columns:
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    
    print("✅ Tipos convertidos")
    return df


def handle_nulls(df):
    """Trata valores nulos"""
    print("🔧 Tratando valores nulos...")
    
    # Remover linhas sem data
    before = len(df)
    df = df.dropna(subset=['week'])
    print(f"   Removidas {before - len(df):,} linhas com week nula")
    
    # Preencher nulos numéricos com mediana
    numeric_cols = ['rank', 'streams', 'danceability', 'energy', 'valence']
    for col in numeric_cols:
        if col in df.columns and df[col].isnull().sum() > 0:
            mediana = df[col].median()
            df[col].fillna(mediana, inplace=True)
            print(f"   {col}: preenchidos com mediana={mediana:.3f}")
    
    # Preencher release_date com a data mais comum
    if 'release_date' in df.columns and df['release_date'].isnull().sum() > 0:
        data_comum = df['release_date'].mode()[0]
        df['release_date'].fillna(data_comum, inplace=True)
    
    print("✅ Nulos tratados")
    return df


def remove_duplicates(df):
    """Remove registros duplicados"""
    print("🔄 Removendo duplicatas...")
    
    before = len(df)
    df = df.drop_duplicates(subset=['track_name', 'artist_names', 'country', 'week'])
    print(f"   Removidas {before - len(df):,} duplicatas")
    
    return df


def remove_outliers(df):
    """Remove outliers de streams"""
    print("📊 Tratando outliers...")
    
    if 'streams' in df.columns:
        # Remover apenas os 0.5% mais extremos
        percentil_995 = df['streams'].quantile(0.995)
        before = len(df)
        df = df[df['streams'] <= percentil_995]
        print(f"   Removidas {before - len(df):,} linhas com streams > {percentil_995:,.0f}")
    
    # Corrigir características musicais
    for col in ['danceability', 'energy', 'valence']:
        if col in df.columns:
            df[col] = df[col].clip(0, 1)
    
    print("✅ Outliers tratados")
    return df

# ===================================================================
# FUNÇÕES DE FEATURE ENGINEERING
# ===================================================================

def create_streams_millions(df):
    """Cria coluna de streams em milhões"""
    if 'streams' in df.columns:
        df['streams_millions'] = (df['streams'] / 1_000_000).round(2)
    return df


def create_date_features(df):
    """Cria features a partir das datas"""
    if 'week' in df.columns:
        df['year'] = df['week'].dt.year
        df['month'] = df['week'].dt.month
        df['month_name'] = df['week'].dt.strftime('%B')
        df['day_of_week'] = df['week'].dt.dayofweek
        df['day_name'] = df['week'].dt.day_name()
        df['week_number'] = df['week'].dt.isocalendar().week
    return df


def create_success_score(df):
    """Cria score de sucesso baseado em rank e streams"""
    if 'rank' in df.columns and 'streams_millions' in df.columns:
        df['success_score'] = (201 - df['rank']) * np.log1p(df['streams_millions'])
    return df


def create_music_profile(df):
    """Classifica músicas por perfil musical"""
    if all(col in df.columns for col in ['danceability', 'energy', 'valence']):
        def classify(row):
            if row['danceability'] > 0.7 and row['energy'] > 0.7:
                return '🔥 Ritmo Latino/Alta Energia'
            elif row['danceability'] > 0.7:
                return '💃 Dançante'
            elif row['energy'] > 0.7:
                return '⚡ Energética'
            elif row['valence'] > 0.7:
                return '😊 Feliz/Positiva'
            elif row['valence'] < 0.3:
                return '😢 Melancólica/Triste'
            else:
                return '🎵 Neutra/Equilibrada'
        
        df['music_profile'] = df.apply(classify, axis=1)
    return df


def create_sub_region(df):
    """Cria coluna de sub-região das Américas"""
    if 'country' in df.columns:
        def get_subregion(country):
            if country in ['United States', 'USA', 'Canada', 'Mexico']:
                return '🌎 América do Norte'
            elif country in ['Brazil', 'Brasil', 'Argentina', 'Chile', 'Peru', 
                           'Colombia', 'Venezuela', 'Ecuador', 'Bolivia', 
                           'Paraguay', 'Uruguay']:
                return '🗺️ América do Sul'
            elif country in ['Costa Rica', 'Panama', 'Guatemala', 'El Salvador', 
                           'Honduras', 'Nicaragua']:
                return '🌏 América Central'
            else:
                return '🏝️ Caribe'
        
        df['sub_region'] = df['country'].apply(get_subregion)
    return df


def create_rank_group(df):
    """Cria grupos de rank"""
    if 'rank' in df.columns:
        df['rank_group'] = pd.cut(
            df['rank'], 
            bins=[0, 10, 50, 100, 200], 
            labels=['🏆 Top 10', '📊 Top 11-50', '📈 Top 51-100', '📉 Top 101-200']
        )
    return df


def create_latin_style(df):
    """Cria indicador de estilo latino"""
    if all(col in df.columns for col in ['danceability', 'energy', 'valence']):
        df['is_latin_style'] = ((df['danceability'] > 0.7) & 
                                 (df['energy'] > 0.6) & 
                                 (df['valence'] > 0.5)).astype(int)
    return df


def create_popularity_category(df):
    """Cria categorias de popularidade baseadas em streams"""
    if 'streams_millions' in df.columns:
        def get_category(streams):
            if streams >= 100:
                return '🌟 Mega Hit (>100M)'
            elif streams >= 50:
                return '💎 Super Hit (50-100M)'
            elif streams >= 10:
                return '⭐ Hit (10-50M)'
            elif streams >= 1:
                return '📈 Sucesso (1-10M)'
            else:
                return '🆕 Novo (<1M)'
        
        df['popularity_category'] = df['streams_millions'].apply(get_category)
    return df

# ===================================================================
# PIPELINE PRINCIPAL
# ===================================================================

def run_etl_pipeline(input_path, output_path=None, chunk_size=100000, max_rows=None):
    """
    Executa o pipeline completo de ETL
    
    Parâmetros:
    -----------
    input_path : str
        Caminho do arquivo CSV de entrada
    output_path : str
        Caminho para salvar o arquivo processado
    chunk_size : int
        Tamanho do chunk para processamento
    max_rows : int
        Número máximo de linhas a processar (para testes)
    
    Retorna:
    --------
    df : DataFrame
        Dados processados
    """
    
    print("=" * 70)
    print("🚀 INICIANDO PIPELINE ETL - SPOTIFY AMÉRICAS")
    print("=" * 70)
    print(f"\n📂 Arquivo entrada: {input_path}")
    print(f"📁 Arquivo saída: {output_path}")
    print(f"📦 Chunk size: {chunk_size:,}")
    
    # Verificar se arquivo existe
    if not os.path.exists(input_path):
        print(f"\n❌ Arquivo não encontrado: {input_path}")
        return None
    
    # Processar em chunks
    print("\n📊 Processando dados em chunks...")
    chunks = []
    total_registros = 0
    
    for i, chunk in enumerate(pd.read_csv(input_path, chunksize=chunk_size, low_memory=False)):
        print(f"\n--- Chunk {i+1} ---")
        print(f"   Registros no chunk: {len(chunk):,}")
        
        # Filtrar países da América
        chunk = chunk[chunk['country'].isin(PAISES_AMERICA)]
        if len(chunk) == 0:
            print(f"   ⏭️ Nenhum registro da América, pulando...")
            continue
        
        # Aplicar transformações
        chunk = convert_types(chunk)
        chunk = handle_nulls(chunk)
        chunk = remove_duplicates(chunk)
        chunk = remove_outliers(chunk)
        
        # Feature engineering
        chunk = create_streams_millions(chunk)
        chunk = create_date_features(chunk)
        chunk = create_success_score(chunk)
        chunk = create_music_profile(chunk)
        chunk = create_sub_region(chunk)
        chunk = create_rank_group(chunk)
        chunk = create_latin_style(chunk)
        chunk = create_popularity_category(chunk)
        
        chunks.append(chunk)
        total_registros += len(chunk)
        print(f"   ✅ Processado: {len(chunk):,} registros (total: {total_registros:,})")
        
        # Limitar para testes
        if max_rows and total_registros >= max_rows:
            print(f"\n⚠️ Limite de {max_rows:,} registros atingido")
            break
    
    # Concatenar todos os chunks
    if not chunks:
        print("\n❌ Nenhum dado encontrado!")
        return None
    
    df = pd.concat(chunks, ignore_index=True)
    
    print("\n" + "=" * 70)
    print("✅ ETL CONCLUÍDO!")
    print("=" * 70)
    print(f"\n📊 Shape final: {df.shape[0]:,} linhas × {df.shape[1]} colunas")
    print(f"💾 Memória: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Salvar se output_path foi fornecido
    if output_path:
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Salvar em Parquet (recomendado)
        if output_path.endswith('.parquet'):
            df.to_parquet(output_path, compression='snappy')
            print(f"\n💾 Arquivo salvo: {output_path}")
        else:
            df.to_csv(output_path, index=False)
            print(f"\n💾 Arquivo salvo: {output_path}")
    
    return df


# ===================================================================
# MAIN
# ===================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ETL Pipeline para Spotify Américas')
    parser.add_argument('--input', type=str, required=True, help='Caminho do arquivo de entrada')
    parser.add_argument('--output', type=str, default='data/processed/spotify_americas_clean.parquet', 
                        help='Caminho do arquivo de saída')
    parser.add_argument('--chunk-size', type=int, default=100000, help='Tamanho do chunk')
    parser.add_argument('--max-rows', type=int, default=None, help='Máximo de linhas para processar')
    
    args = parser.parse_args()
    
    # Executar pipeline
    df = run_etl_pipeline(
        input_path=args.input,
        output_path=args.output,
        chunk_size=args.chunk_size,
        max_rows=args.max_rows
    )
    
    if df is not None:
        print("\n✅ Pipeline executado com sucesso!")
    else:
        print("\n❌ Falha na execução do pipeline!")
        sys.exit(1)
