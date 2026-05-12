#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ===================================================================
# UTILITÁRIOS - Spotify Américas
# ===================================================================
# Objetivo: Funções utilitárias compartilhadas entre os scripts
# ===================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# ===================================================================
# CONSTANTES
# ===================================================================

PAISES_AMERICA = [
    'United States', 'USA', 'Canada', 'Mexico',
    'Brazil', 'Brasil', 'Argentina', 'Chile', 'Peru', 'Colombia',
    'Venezuela', 'Ecuador', 'Bolivia', 'Paraguay', 'Uruguay',
    'Costa Rica', 'Panama', 'Guatemala', 'Dominican Republic', 'Cuba'
]

SUB_REGIOES = {
    'North America': ['United States', 'USA', 'Canada', 'Mexico'],
    'South America': ['Brazil', 'Brasil', 'Argentina', 'Chile', 'Peru', 
                      'Colombia', 'Venezuela', 'Ecuador', 'Bolivia', 
                      'Paraguay', 'Uruguay'],
    'Central America': ['Costa Rica', 'Panama', 'Guatemala', 'El Salvador', 
                        'Honduras', 'Nicaragua'],
    'Caribbean': ['Cuba', 'Jamaica', 'Haiti', 'Dominican Republic', 
                  'Puerto Rico', 'Bahamas', 'Trinidad and Tobago']
}

CORES_REGIOES = {
    'América do Norte': '#4ECDC4',
    'América do Sul': '#45B7D1',
    'América Central': '#FFE66D',
    'Caribe': '#FF6B6B'
}

# ===================================================================
# FUNÇÕES DE VALIDAÇÃO
# ===================================================================

def validate_dataframe(df):
    """Valida a integridade do DataFrame"""
    print("🔍 Validando DataFrame...")
    
    checks = {
        "Não está vazio": len(df) > 0,
        "Sem valores nulos": df.isnull().sum().sum() == 0,
    }
    
    if 'rank' in df.columns:
        checks["Rank entre 1 e 200"] = df['rank'].between(1, 200).all()
    
    if 'streams' in df.columns:
        checks["Streams positivos"] = (df['streams'] > 0).all()
    
    if 'danceability' in df.columns:
        checks["Danceability entre 0 e 1"] = df['danceability'].between(0, 1).all()
    
    results = []
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"   {status} {check}: {result}")
        results.append(result)
    
    return all(results)


def get_data_info(df):
    """Retorna informações resumidas do DataFrame"""
    info = {
        'shape': df.shape,
        'columns': list(df.columns),
        'memory_mb': df.memory_usage(deep=True).sum() / 1024**2,
        'null_count': int(df.isnull().sum().sum()),
        'total_streams_m': float(df['streams_millions'].sum()) if 'streams_millions' in df.columns else None,
        'unique_countries': int(df['country'].nunique()) if 'country' in df.columns else None,
        'unique_tracks': int(df['track_name'].nunique()) if 'track_name' in df.columns else None,
        'unique_artists': int(df['artist_names'].nunique()) if 'artist_names' in df.columns else None,
        'date_range': {
            'min': df['week'].min() if 'week' in df.columns else None,
            'max': df['week'].max() if 'week' in df.columns else None
        }
    }
    
    return info

# ===================================================================
# FUNÇÕES DE AGREGAÇÃO
# ===================================================================

def get_top_countries(df, n=10):
    """Retorna top N países por streams"""
    return (df.groupby('country')['streams_millions']
            .sum()
            .sort_values(ascending=False)
            .head(n)
            .reset_index())


def get_top_tracks(df, n=10):
    """Retorna top N músicas por streams"""
    return (df.groupby(['track_name', 'artist_names'])['streams_millions']
            .sum()
            .sort_values(ascending=False)
            .head(n)
            .reset_index())


def get_top_artists(df, n=10):
    """Retorna top N artistas por streams"""
    return (df.groupby('artist_names')['streams_millions']
            .sum()
            .sort_values(ascending=False)
            .head(n)
            .reset_index())


def get_stats_by_region(df):
    """Retorna estatísticas agregadas por sub-região"""
    if 'sub_region' not in df.columns:
        return None
    
    return df.groupby('sub_region').agg({
        'streams_millions': ['sum', 'mean', 'count'],
        'danceability': 'mean',
        'energy': 'mean',
        'valence': 'mean',
        'country': 'nunique'
    }).round(3)

# ===================================================================
# FUNÇÕES DE FORMATAÇÃO
# ===================================================================

def format_millions(value):
    """Formata número para milhões"""
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    else:
        return str(value)


def format_percentage(value, total):
    """Formata porcentagem"""
    return f"{(value / total) * 100:.1f}%"


def format_duration(seconds):
    """Formata duração em segundos para mm:ss"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"

# ===================================================================
# FUNÇÕES DE EXPORTAÇÃO
# ===================================================================

def export_to_excel(df, output_path, sheet_name='Spotify_Americas'):
    """Exporta DataFrame para Excel com formatação"""
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Ajustar largura das colunas
            worksheet = writer.sheets[sheet_name]
            for column in df:
                column_width = max(df[column].astype(str).map(len).max(), len(column))
                worksheet.column_dimensions[column].width = min(column_width + 2, 50)
        
        print(f"✅ Exportado para: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao exportar: {e}")
        return False


def save_summary_report(df, output_path):
    """Salva um relatório resumido em texto"""
    info = get_data_info(df)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("RELATÓRIO RESUMIDO - SPOTIFY AMÉRICAS\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"Data do relatório: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("📊 ESTATÍSTICAS GERAIS:\n")
        f.write(f"   • Registros: {info['shape'][0]:,}\n")
        f.write(f"   • Colunas: {info['shape'][1]}\n")
        f.write(f"   • Memória: {info['memory_mb']:.2f} MB\n")
        f.write(f"   • Valores nulos: {info['null_count']}\n\n")
        
        if info['total_streams_m']:
            f.write("💰 STREAMS:\n")
            f.write(f"   • Total: {info['total_streams_m']:.1f}M\n\n")
        
        if info['unique_countries']:
            f.write("🌍 DIVERSIDADE:\n")
            f.write(f"   • Países: {info['unique_countries']}\n")
            f.write(f"   • Músicas: {info['unique_tracks']:,}\n")
            f.write(f"   • Artistas: {info['unique_artists']:,}\n\n")
        
        if info['date_range']['min']:
            f.write("📅 PERÍODO:\n")
            f.write(f"   • Início: {info['date_range']['min'].date()}\n")
            f.write(f"   • Fim: {info['date_range']['max'].date()}\n")
    
    print(f"✅ Relatório salvo: {output_path}")

# ===================================================================
# FUNÇÕES DE LOGGING
# ===================================================================

class Logger:
    """Classe simples para logging"""
    
    def __init__(self, log_file=None):
        self.log_file = log_file
    
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + "\n")
    
    def info(self, message):
        self.log(message, "INFO")
    
    def warning(self, message):
        self.log(message, "WARNING")
    
    def error(self, message):
        self.log(message, "ERROR")
    
    def success(self, message):
        self.log(f"✅ {message}", "SUCCESS")

# ===================================================================
# FUNÇÕES DE PERFORMANCE
# ===================================================================

def timer_decorator(func):
    """Decorator para medir tempo de execução"""
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        duration = (end - start).total_seconds()
        print(f"⏱️ {func.__name__} executado em {duration:.2f}s")
        return result
    return wrapper


def memory_usage(func):
    """Decorator para medir uso de memória"""
    import tracemalloc
    
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"💾 {func.__name__} - Memória: {current / 1024**2:.2f} MB (pico: {peak / 1024**2:.2f} MB)")
        return result
    return wrapper


# ===================================================================
# TESTE RÁPIDO
# ===================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DAS FUNÇÕES UTILITÁRIAS")
    print("=" * 60)
    
    # Criar DataFrame de exemplo
    test_df = pd.DataFrame({
        'country': ['United States', 'Brazil', 'Mexico', 'Canada'],
        'streams_millions': [100.5, 80.3, 60.2, 45.1],
        'track_name': ['Song A', 'Song B', 'Song C', 'Song D'],
        'artist_names': ['Artist 1', 'Artist 2', 'Artist 3', 'Artist 4']
    })
    
    print("\n📊 Teste de funções:")
    print(f"   Top países: {get_top_countries(test_df, 2)}")
    print(f"   Formatar milhões: {format_millions(1500000)}")
    
    print("\n✅ Teste concluído!")
