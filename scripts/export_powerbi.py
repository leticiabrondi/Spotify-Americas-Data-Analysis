#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ===================================================================
# EXPORTAÇÃO PARA POWER BI - Spotify Américas
# ===================================================================
# Objetivo: Exportar dados tratados para dashboard no Power BI
# Uso: python scripts/export_powerbi.py --input data/processed/spotify_americas_clean.parquet
# ===================================================================

import pandas as pd
import numpy as np
import os
import json
import argparse
import sys

# ===================================================================
# FUNÇÕES DE EXPORTAÇÃO
# ===================================================================

def load_data(input_path):
    """Carrega os dados limpos"""
    print(f"📂 Carregando dados de: {input_path}")
    
    if input_path.endswith('.parquet'):
        df = pd.read_parquet(input_path)
    else:
        df = pd.read_csv(input_path)
    
    print(f"✅ Dados carregados: {len(df):,} registros")
    return df


def export_fact_table(df, output_dir):
    """Exporta tabela fato (dados completos)"""
    print("\n📊 Exportando tabela fato...")
    
    colunas_fato = [
        'track_name', 'artist_names', 'country', 'sub_region' if 'sub_region' in df.columns else 'region',
        'rank', 'streams_millions', 'week', 'year', 'month', 'month_name',
        'danceability', 'energy', 'valence', 'success_score',
        'music_profile' if 'music_profile' in df.columns else 'rank_group',
        'popularity_category' if 'popularity_category' in df.columns else None,
        'is_latin_style' if 'is_latin_style' in df.columns else None
    ]
    
    # Filtrar colunas existentes
    colunas_exist = [c for c in colunas_fato if c is not None and c in df.columns]
    df_fato = df[colunas_exist].copy()
    
    # Renomear para português
    rename_map = {
        'track_name': 'musica',
        'artist_names': 'artista',
        'country': 'pais',
        'sub_region': 'sub_regiao',
        'streams_millions': 'streams_milhoes',
        'week': 'data',
        'danceability': 'dancabilidade',
        'success_score': 'score_sucesso',
        'music_profile': 'perfil_musical',
        'popularity_category': 'categoria_popularidade',
        'is_latin_style': 'estilo_latino'
    }
    
    df_fato = df_fato.rename(columns={k: v for k, v in rename_map.items() if k in df_fato.columns})
    
    # Salvar
    output_path = f"{output_dir}/01_tabela_fato_musicas.csv"
    df_fato.to_csv(output_path, index=False)
    print(f"   ✅ {output_path} - {len(df_fato):,} registros")
    
    return df_fato


def export_country_dimension(df, output_dir):
    """Exporta dimensão país"""
    print("\n📊 Exportando dimensão país...")
    
    pais_agg = df.groupby('country').agg({
        'streams_millions': ['sum', 'mean', 'std'],
        'danceability': 'mean',
        'energy': 'mean',
        'valence': 'mean',
        'rank': 'mean',
        'track_name': 'count',
        'artist_names': 'nunique'
    }).round(3)
    
    pais_agg.columns = ['total_streams_m', 'media_streams_m', 'std_streams_m',
                        'media_dancabilidade', 'media_energia', 'media_valence',
                        'rank_medio', 'total_musicas', 'total_artistas']
    pais_agg = pais_agg.reset_index()
    
    # Adicionar sub-região
    if 'sub_region' in df.columns:
        sub_map = df.groupby('country')['sub_region'].first()
        pais_agg['sub_regiao'] = pais_agg['country'].map(sub_map)
    
    output_path = f"{output_dir}/02_dimensao_paises.csv"
    pais_agg.to_csv(output_path, index=False)
    print(f"   ✅ {output_path} - {len(pais_agg)} países")
    
    return pais_agg


def export_top_musics(df, output_dir, top_n=100):
    """Exporta top músicas"""
    print(f"\n📊 Exportando top {top_n} músicas...")
    
    top_musicas = (df.groupby(['track_name', 'artist_names'])
                   .agg({
                       'streams_millions': 'sum',
                       'rank': 'min',
                       'country': 'nunique'
                   })
                   .rename(columns={'country': 'paises_alcancados'})
                   .sort_values('streams_millions', ascending=False)
                   .head(top_n)
                   .reset_index())
    
    output_path = f"{output_dir}/03_top_{top_n}_musicas.csv"
    top_musicas.to_csv(output_path, index=False)
    print(f"   ✅ {output_path}")
    
    return top_musicas


def export_top_artists(df, output_dir, top_n=50):
    """Exporta top artistas"""
    print(f"\n📊 Exportando top {top_n} artistas...")
    
    top_artistas = (df.groupby('artist_names')
                    .agg({
                        'streams_millions': 'sum',
                        'track_name': 'nunique',
                        'country': 'nunique'
                    })
                    .rename(columns={'track_name': 'musicas_distintas', 'country': 'paises_alcancados'})
                    .sort_values('streams_millions', ascending=False)
                    .head(top_n)
                    .reset_index())
    
    output_path = f"{output_dir}/04_top_{top_n}_artistas.csv"
    top_artistas.to_csv(output_path, index=False)
    print(f"   ✅ {output_path}")
    
    return top_artistas


def export_time_series(df, output_dir):
    """Exporta série temporal"""
    print("\n📊 Exportando série temporal...")
    
    # Por semana
    temporal_semanal = df.groupby(['week', 'year', 'month']).agg({
        'streams_millions': 'sum',
        'rank': 'mean'
    }).reset_index()
    
    output_path = f"{output_dir}/05_serie_temporal.csv"
    temporal_semanal.to_csv(output_path, index=False)
    print(f"   ✅ {output_path} - {len(temporal_semanal)} semanas")
    
    return temporal_semanal


def export_music_profile(df, output_dir):
    """Exporta análise de perfil musical"""
    print("\n📊 Exportando análise de perfil musical...")
    
    if 'music_profile' in df.columns:
        perfil_agg = df.groupby('music_profile').agg({
            'streams_millions': ['sum', 'mean'],
            'track_name': 'count'
        }).round(2)
        
        perfil_agg.columns = ['total_streams_m', 'media_streams_m', 'total_musicas']
        perfil_agg = perfil_agg.reset_index()
        perfil_agg.columns = ['perfil_musical', 'total_streams_m', 'media_streams_m', 'total_musicas']
        
        output_path = f"{output_dir}/06_perfil_musical.csv"
        perfil_agg.to_csv(output_path, index=False)
        print(f"   ✅ {output_path}")
        
        return perfil_agg
    else:
        print("   ⚠️ Coluna 'music_profile' não encontrada")
        return None


def export_subregion_analysis(df, output_dir):
    """Exporta análise por sub-região"""
    print("\n📊 Exportando análise por sub-região...")
    
    if 'sub_region' in df.columns:
        regiao_agg = df.groupby('sub_region').agg({
            'streams_millions': 'sum',
            'danceability': 'mean',
            'energy': 'mean',
            'valence': 'mean',
            'country': 'nunique',
            'track_name': 'count',
            'artist_names': 'nunique'
        }).round(3).reset_index()
        
        regiao_agg.columns = ['sub_regiao', 'total_streams_m', 'media_dancabilidade', 
                              'media_energia', 'media_valence', 'total_paises', 
                              'total_musicas', 'total_artistas']
        
        output_path = f"{output_dir}/07_analise_sub_regioes.csv"
        regiao_agg.to_csv(output_path, index=False)
        print(f"   ✅ {output_path}")
        
        return regiao_agg
    else:
        print("   ⚠️ Coluna 'sub_region' não encontrada")
        return None


def export_correlation_matrix(df, output_dir):
    """Exporta matriz de correlação"""
    print("\n📊 Exportando matriz de correlação...")
    
    colunas_corr = ['rank', 'streams_millions', 'danceability', 'energy', 'valence']
    colunas_exist = [c for c in colunas_corr if c in df.columns]
    
    if len(colunas_exist) >= 2:
        corr_matrix = df[colunas_exist].corr().round(3)
        
        output_path = f"{output_dir}/08_matriz_correlacao.csv"
        corr_matrix.to_csv(output_path)
        print(f"   ✅ {output_path}")
        
        return corr_matrix
    else:
        print("   ⚠️ Colunas insuficientes para correlação")
        return None


def export_metadata(df, output_dir, files_exported):
    """Exporta metadados em JSON"""
    print("\n📊 Exportando metadados...")
    
    metadados = {
        'projeto': 'Spotify Weekly Top 200 - Análise das Américas',
        'data_exportacao': pd.Timestamp.now().isoformat(),
        'total_registros': len(df),
        'total_paises': int(df['country'].nunique()),
        'total_musicas': int(df['track_name'].nunique()),
        'total_artistas': int(df['artist_names'].nunique()),
        'periodo_inicio': df['week'].min().isoformat(),
        'periodo_fim': df['week'].max().isoformat(),
        'total_streams_milhoes': float(df['streams_millions'].sum()),
        'media_dancabilidade': float(df['danceability'].mean()),
        'media_energia': float(df['energy'].mean()),
        'media_valence': float(df['valence'].mean()),
        'arquivos_exportados': files_exported
    }
    
    output_path = f"{output_dir}/metadados.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metadados, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ {output_path}")
    
    return metadados

# ===================================================================
# PIPELINE PRINCIPAL
# ===================================================================

def export_to_powerbi(input_path, output_dir='data/powerbi'):
    """
    Exporta todos os dados necessários para o Power BI
    
    Parâmetros:
    -----------
    input_path : str
        Caminho do arquivo de dados limpos
    output_dir : str
        Diretório de saída para os arquivos do Power BI
    """
    
    print("=" * 70)
    print("📊 EXPORTAÇÃO PARA POWER BI - SPOTIFY AMÉRICAS")
    print("=" * 70)
    
    # Criar diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n📁 Diretório de saída: {output_dir}")
    
    # Carregar dados
    df = load_data(input_path)
    
    # Exportar todos os arquivos
    files_exported = []
    
    # 1. Tabela fato
    export_fact_table(df, output_dir)
    files_exported.append('01_tabela_fato_musicas.csv')
    
    # 2. Dimensão país
    export_country_dimension(df, output_dir)
    files_exported.append('02_dimensao_paises.csv')
    
    # 3. Top músicas
    export_top_musics(df, output_dir)
    files_exported.append('03_top_100_musicas.csv')
    
    # 4. Top artistas
    export_top_artists(df, output_dir)
    files_exported.append('04_top_50_artistas.csv')
    
    # 5. Série temporal
    export_time_series(df, output_dir)
    files_exported.append('05_serie_temporal.csv')
    
    # 6. Perfil musical
    export_music_profile(df, output_dir)
    files_exported.append('06_perfil_musical.csv')
    
    # 7. Análise sub-região
    export_subregion_analysis(df, output_dir)
    files_exported.append('07_analise_sub_regioes.csv')
    
    # 8. Matriz correlação
    export_correlation_matrix(df, output_dir)
    files_exported.append('08_matriz_correlacao.csv')
    
    # 9. Metadados
    export_metadata(df, output_dir, files_exported)
    files_exported.append('metadados.json')
    
    # Resumo final
    print("\n" + "=" * 70)
    print("✅ EXPORTAÇÃO CONCLUÍDA!")
    print("=" * 70)
    print(f"\n📁 Arquivos salvos em: {output_dir}")
    print(f"\n📋 Arquivos gerados ({len(files_exported)}):")
    for f in files_exported:
        print(f"   • {f}")
    
    return True


# ===================================================================
# MAIN
# ===================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Exportar dados para Power BI')
    parser.add_argument('--input', type=str, 
                        default='data/processed/spotify_americas_clean.parquet',
                        help='Caminho do arquivo de dados limpos')
    parser.add_argument('--output', type=str, default='data/powerbi',
                        help='Diretório de saída para os arquivos do Power BI')
    
    args = parser.parse_args()
    
    # Executar exportação
    success = export_to_powerbi(args.input, args.output)
    
    if success:
        print("\n🎉 Pronto para importar no Power BI!")
    else:
        print("\n❌ Falha na exportação!")
        sys.exit(1)
