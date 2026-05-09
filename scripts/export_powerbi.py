# ===================================================================
# EXPORTAÇÃO DE DADOS PARA POWER BI
# ===================================================================

import pandas as pd
import os

def exportar_para_powerbi(df, output_dir='../data/powerbi/'):
    """
    Exporta dados tratados para CSV otimizados para Power BI
    
    Parâmetros:
    -----------
    df : DataFrame
        Dados limpos das Américas
    output_dir : str
        Diretório de saída
    """
    
    # Criar diretório se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    print("📊 Exportando dados para Power BI...")
    print("="*50)
    
    # ==============================================================
    # 1. DADOS COMPLETOS (Tabela Fato)
    # ==============================================================
    print("\n1️⃣ Exportando tabela fato (dados completos)...")
    
    # Selecionar colunas relevantes para o dashboard
    colunas_powerbi = [
        'track_name', 'artist_names', 'country', 'sub_region' if 'sub_region' in df.columns else 'region',
        'rank', 'streams_millions', 'week', 'year', 'month', 'month_name',
        'danceability', 'energy', 'valence', 'success_score',
        'music_profile' if 'music_profile' in df.columns else 'rank_group',
        'popularity_category' if 'popularity_category' in df.columns else None
    ]
    
    # Filtrar colunas existentes
    colunas_existentes = [col for col in colunas_powerbi if col in df.columns and col is not None]
    df_powerbi = df[colunas_existentes].copy()
    
    # Renomear colunas para português (opcional, facilita Power BI)
    rename_map = {
        'track_name': 'musica',
        'artist_names': 'artista',
        'country': 'pais',
        'sub_region': 'sub_regiao',
        'streams_millions': 'streams_milhoes',
        'danceability': 'dancabilidade',
        'success_score': 'score_sucesso',
        'music_profile': 'perfil_musical'
    }
    df_powerbi = df_powerbi.rename(columns={k: v for k, v in rename_map.items() if k in df_powerbi.columns})
    
    # Salvar
    df_powerbi.to_csv(f'{output_dir}01_tabela_fato_musicas.csv', index=False)
    print(f"   ✅ 01_tabela_fato_musicas.csv - {len(df_powerbi):,} registros")
    
    # ==============================================================
    # 2. DADOS AGREGDOS POR PAÍS (Tabela Dimensão País)
    # ==============================================================
    print("\n2️⃣ Exportando tabela dimensão país...")
    
    pais_agg = df.groupby('country').agg({
        'streams_millions': ['sum', 'mean', 'std'],
        'danceability': 'mean',
        'energy': 'mean', 
        'valence': 'mean',
        'rank': 'mean',
        'track_name': 'count',
        'artist_names': 'nunique'
    }).round(3)
    
    # Achatar colunas MultiIndex
    pais_agg.columns = ['total_streams_m', 'media_streams_m', 'std_streams_m',
                        'media_dancabilidade', 'media_energia', 'media_valence',
                        'rank_medio', 'total_musicas', 'total_artistas']
    pais_agg = pais_agg.reset_index()
    
    # Adicionar sub-região
    if 'sub_region' in df.columns:
        sub_regiao_map = df.groupby('country')['sub_region'].first()
        pais_agg['sub_regiao'] = pais_agg['country'].map(sub_regiao_map)
    
    pais_agg.to_csv(f'{output_dir}02_dimensao_paises.csv', index=False)
    print(f"   ✅ 02_dimensao_paises.csv - {len(pais_agg)} países")
    
    # ==============================================================
    # 3. DADOS AGREGDOS POR SUB-REGIÃO
    # ==============================================================
    if 'sub_region' in df.columns:
        print("\n3️⃣ Exportando análise por sub-região...")
        
        regiao_agg = df.groupby('sub_region').agg({
            'streams_millions': 'sum',
            'danceability': 'mean',
            'energy': 'mean',
            'valence': 'mean',
            'country': 'nunique',
            'artist_names': 'nunique',
            'track_name': 'count'
        }).round(3)
        
        regiao_agg.columns = ['total_streams_m', 'media_dancabilidade', 'media_energia', 
                              'media_valence', 'total_paises', 'total_artistas', 'total_musicas']
        regiao_agg = regiao_agg.reset_index()
        
        regiao_agg.to_csv(f'{output_dir}03_analise_sub_regioes.csv', index=False)
        print(f"   ✅ 03_analise_sub_regioes.csv - {len(regiao_agg)} regiões")
    
    # ==============================================================
    # 4. SÉRIE TEMPORAL (para gráficos de evolução)
    # ==============================================================
    print("\n4️⃣ Exportando série temporal...")
    
    # Por semana
    temporal_semanal = df.groupby(['week']).agg({
        'streams_millions': 'sum',
        'rank': 'mean'
    }).reset_index()
    temporal_semanal.to_csv(f'{output_dir}04_serie_temporal_semanal.csv', index=False)
    print(f"   ✅ 04_serie_temporal_semanal.csv - {len(temporal_semanal)} semanas")
    
    # Por mês
    temporal_mensal = df.groupby(['year', 'month', 'month_name']).agg({
        'streams_millions': 'sum'
    }).reset_index()
    temporal_mensal.to_csv(f'{output_dir}05_serie_temporal_mensal.csv', index=False)
    print(f"   ✅ 05_serie_temporal_mensal.csv - {len(temporal_mensal)} meses")
    
    # ==============================================================
    # 5. TOP MÚSICAS E TOP ARTISTAS
    # ==============================================================
    print("\n5️⃣ Exportando top performers...")
    
    # Top 100 músicas
    top_musicas = (df.groupby(['track_name', 'artist_names'])['streams_millions']
                   .sum()
                   .sort_values(ascending=False)
                   .head(100)
                   .reset_index())
    top_musicas.columns = ['musica', 'artista', 'streams_milhoes']
    top_musicas.to_csv(f'{output_dir}06_top_100_musicas.csv', index=False)
    print(f"   ✅ 06_top_100_musicas.csv")
    
    # Top 50 artistas
    top_artistas = (df.groupby('artist_names')['streams_millions']
                    .sum()
                    .sort_values(ascending=False)
                    .head(50)
                    .reset_index())
    top_artistas.columns = ['artista', 'streams_milhoes']
    top_artistas.to_csv(f'{output_dir}07_top_50_artistas.csv', index=False)
    print(f"   ✅ 07_top_50_artistas.csv")
    
    # ==============================================================
    # 6. PERFIL MUSICAL (para dashboard)
    # ==============================================================
    if 'music_profile' in df.columns:
        print("\n6️⃣ Exportando análise de perfil musical...")
        
        perfil_agg = df.groupby('music_profile').agg({
            'streams_millions': ['sum', 'mean'],
            'track_name': 'count'
        }).round(2)
        perfil_agg.columns = ['total_streams_m', 'media_streams_m', 'total_musicas']
        perfil_agg = perfil_agg.reset_index()
        perfil_agg.to_csv(f'{output_dir}08_perfil_musical.csv', index=False)
        print(f"   ✅ 08_perfil_musical.csv")
    
    # ==============================================================
    # 7. MATRIZ DE CORRELAÇÃO (para Power BI)
    # ==============================================================
    print("\n7️⃣ Exportando matriz de correlação...")
    
    corr_cols = ['streams_millions', 'danceability', 'energy', 'valence', 'rank']
    corr_cols_exist = [c for c in corr_cols if c in df.columns]
    corr_matrix = df[corr_cols_exist].corr().round(3)
    corr_matrix.to_csv(f'{output_dir}09_matriz_correlacao.csv')
    print(f"   ✅ 09_matriz_correlacao.csv")
    
    # ==============================================================
    # 8. METADADOS (para documentação no Power BI)
    # ==============================================================
    print("\n8️⃣ Exportando metadados...")
    
    import json
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
        'arquivos_exportados': [
            '01_tabela_fato_musicas.csv',
            '02_dimensao_paises.csv',
            '03_analise_sub_regioes.csv',
            '04_serie_temporal_semanal.csv',
            '05_serie_temporal_mensal.csv',
            '06_top_100_musicas.csv',
            '07_top_50_artistas.csv',
            '08_perfil_musical.csv',
            '09_matriz_correlacao.csv'
        ]
    }
    
    with open(f'{output_dir}metadados.json', 'w') as f:
        json.dump(metadados, f, indent=2)
    
    print(f"   ✅ metadados.json")
    
    print("\n" + "="*50)
    print("✅ EXPORTAÇÃO PARA POWER BI CONCLUÍDA!")
    print(f"📁 Arquivos salvos em: {output_dir}")
    print("="*50)
    
    return True

# Executar exportação
if __name__ == "__main__":
    # Carregar dados limpos
    df = pd.read_parquet('/content/drive/MyDrive/spotify_americas_clean.parquet')
    exportar_para_powerbi(df)
