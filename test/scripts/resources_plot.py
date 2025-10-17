import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
import glob
import matplotlib as mpl
from datetime import datetime, timedelta
import argparse

def process_series_data(file_pattern, smooth=False):
    # (Função para dados de workers, sem alterações)
    all_runs = []
    files = glob.glob(file_pattern)
    if not files: return None
    for file_path in files:
        try:
            df = pd.read_csv(file_path)
            if 'timestamp' in df.columns and 'value' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                df.dropna(subset=['value'], inplace=True)
                all_runs.append(df)
        except Exception as e:
            print(f"Erro ao processar {file_path}: {e}")
            continue
    if not all_runs: return None
    concatenated_df = pd.concat(all_runs).sort_values('timestamp')
    if 'labels' in concatenated_df.columns:
        all_pod_data = [
            pod_series.set_index('timestamp')['value'].resample('S').mean()
            for _, pod_series in concatenated_df.groupby('labels')
        ]
        aligned_df = pd.concat(all_pod_data, axis=1)
        mean_df = aligned_df.mean(axis=1).reset_index()
    else:
        mean_df = concatenated_df.set_index('timestamp')['value'].resample('S').mean().reset_index()
    mean_df.columns = ['timestamp', 'value']
    if smooth:
        mean_df['value'] = mean_df['value'].rolling(window=10).mean()
    return mean_df

def process_pivoted_data(file_pattern):
    """
    -- FUNÇÃO CORRIGIDA --
    Mantém a separação entre broker/manager pelo nome do arquivo, mas, para os brokers,
    usa o IP extraído da coluna 'labels' como o identificador para a agregação.
    """
    all_runs = []
    files = sorted(glob.glob(file_pattern))
    
    if not files:
        print(f"Aviso: Nenhum arquivo encontrado para o padrão pivot: {file_pattern}")
        return None
    
    for file_path in files:
        try:
            df = pd.read_csv(file_path)
            
            # Decide como criar a coluna 'instance' com base no nome do arquivo
            if 'kafkaBroker' in file_path:
                # Para arquivos de broker, o identificador é o IP extraído da coluna 'labels'
                #ip = df['labels'].str.extract(r'instance=([^:]+)')
                df['instance'] = 'Broker ' + df['labels'].str.extract(r'instance=([^:]+)')
                
            
            elif 'manager' in file_path:
                # Para o manager, o identificador é um nome fixo
                df['instance'] = 'Manager'
            
            else:
                # Fallback para qualquer outro tipo de arquivo
                df['instance'] = os.path.basename(file_path)

            # Adiciona os dados já com a coluna 'instance' correta
            all_runs.append(df[['timestamp', 'value', 'instance']])
        except Exception as e:
            print(f"Erro ao processar o arquivo pivot {file_path}: {e}")
            continue

    if not all_runs: return None

    # Consolida todos os DataFrames em um só
    concatenated_df = pd.concat(all_runs)
    
    # Converte o timestamp
    concatenated_df['timestamp'] = pd.to_datetime(concatenated_df['timestamp'], unit='s')
    
    # Pivota a tabela usando a coluna 'instance', que agora contém os IPs únicos e 'Manager'
    pivoted_df = concatenated_df.pivot_table(
        index='timestamp', 
        columns='instance', 
        values='value',
        aggfunc='mean'
    )
    
    # Reamostra e preenche lacunas para garantir linhas contínuas no gráfico
    pivoted_df = pivoted_df.resample('S').mean().ffill()
    pivoted_df.sort_index(inplace=True)
    
    return pivoted_df

def create_subplot(ax_obj, definition, start_time, duration):
    # (Função de plotagem, sem alterações)
    ax_obj.set_title(definition['title'], pad=20)
    ax_obj.set_ylabel(definition['ylabel'])
    if definition.get('ylim'): ax_obj.set_ylim(definition['ylim'])
    if definition.get('yticks') is not None: ax_obj.set_yticks(definition['yticks'])
    ax_obj.plot([0, 1], [1, 1], color='black', linewidth=0.75, clip_on=False, transform=ax_obj.transAxes)

    for series in definition['series']:
        is_pivot = series.get('pivot', False)
        processor = process_pivoted_data if is_pivot else process_series_data
        series_df = processor(series['pattern'])
        
        if series_df is not None:
            if is_pivot:
                series_df['elapsed_minutes'] = (series_df.index - start_time).total_seconds() / 60.0
                value_columns = series_df.columns.drop('elapsed_minutes', errors='ignore')
                for col_name in value_columns:
                    ax_obj.plot(series_df['elapsed_minutes'], series_df[col_name], label=col_name)
            else:
                series_df['elapsed_minutes'] = (series_df['timestamp'] - start_time).dt.total_seconds() / 60.0
                ax_obj.plot(series_df['elapsed_minutes'], series_df['value'], label=series['label'])

    ax_obj.set_xlim(0, duration) 
    ax_obj.xaxis.set_major_locator(mticker.MultipleLocator(10)) 
    ax_obj.grid(True, which='major', linestyle='--', linewidth=0.5)
    
    ax_obj.legend(loc='upper right')
    ax_obj.set_xlabel('Time (Minutes)')

def main():
    # (O resto do script permanece o mesmo)
    parser = argparse.ArgumentParser(description='Generate resource consumption plots from experiment data.')
    parser.add_argument('--kafka-exp', type=str, required=True, help='Experiment ID for Kafka.')
    parser.add_argument('--spark-exp', type=str, required=True, help='Experiment ID for Spark.')
    parser.add_argument('--registers', type=str, default='5000', help='Number of registers per second.')
    parser.add_argument('--instances', type=str, default='3', help='Number of instances.')
    parser.add_argument('--spark-path', type=str, required=True, help='Path to the Spark results directory.')
    parser.add_argument('--kafka-path', type=str, required=True, help='Path to the Kafka Streams results directory.')
    parser.add_argument('--broker-cpu-pattern', type=str, 
                        default='generic_kafkaBrokerNodesCPUsPercentageUtilization_60s_*.csv',
                        help='Filename pattern for Kafka brokers, use *.')
    parser.add_argument('--manager-cpu-pattern', type=str,
                        default='generic_managerNodesCPUsPercentageUtilization_60s_*.csv',
                        help='Filename pattern for the manager node CPU usage.')
    parser.add_argument('--duration', type=int, default=64, 
                        help='Experiment duration in minutes for the x-axis limit.')
    
    args = parser.parse_args()

    plt.rc("text", usetex=False)
    mpl.rcParams.update({'font.size': 18})

    fig, ax = plt.subplots(4, 2, figsize=(20, 20), sharex=False)

    def get_pattern(base_path, framework_exp, metric):
        return f'{base_path}/exp{framework_exp}_{args.registers}_{args.instances}_{metric}'

    plot_definitions = {
        'spark_cpu_worker': {
            'ax': ax[0][0], 'title': 'Spark - Worker CPUs Usage', 'ylabel': 'CPUs Usage (%)', 'ylim': (0, 100),
            'series': [{'label': 'Workers', 'pattern': get_pattern(args.spark_path, args.spark_exp, 'generic_workerNodesCPUsPercentageUtilization_60s_*.csv'), 'smooth': True}]
        },
        'spark_mem_worker': {
            'ax': ax[1][0], 'title': 'Spark - Worker Memory Usage', 'ylabel': 'Memory (GB)', 'ylim': (0, 4.5),
            'series': [{'label': 'Workers', 'pattern': get_pattern(args.spark_path, args.spark_exp, 'generic_workerNodesTotalMemoryUsageWithoutConsidBufferedandCachedGB_*.csv')}]
        },
        'spark_net_worker': {
            'ax': ax[2][0], 'title': 'Spark - Worker Network Traffic', 'ylabel': 'MB/s', 'ylim': (-5, 60),
            'series': [{'label': 'Workers', 'pattern': get_pattern(args.spark_path, args.spark_exp, 'generic_workerNodesNetworkReceiveMB_60s_*.csv'), 'smooth': True}]
        },
        'spark_cpu_additional': {
            'ax': ax[3][0], 'title': 'Spark - Additional nodes CPUs usage', 'ylabel': 'CPUs Usage (%)', 'ylim': (0, 100),
            'series': [
                {'pattern': get_pattern(args.spark_path, args.spark_exp, args.broker_cpu_pattern), 'pivot': True},
                {'pattern': get_pattern(args.spark_path, args.spark_exp, args.manager_cpu_pattern), 'pivot': True}
            ]
        },
        'kafka_cpu_worker': {
            'ax': ax[0][1], 'title': 'Kafka Streams - Worker CPUs Usage', 'ylabel': 'CPUs Usage (%)', 'ylim': (0, 100),
            'series': [{'label': 'Workers', 'pattern': get_pattern(args.kafka_path, args.kafka_exp, 'generic_workerNodesCPUsPercentageUtilization_60s_*.csv'), 'smooth': True}]
        },
        'kafka_mem_worker': {
            'ax': ax[1][1], 'title': 'Kafka Streams - Worker Memory Usage', 'ylabel': 'Memory (GB)', 'ylim': (0, 4.5),
            'series': [{'label': 'Workers', 'pattern': get_pattern(args.kafka_path, args.kafka_exp, 'generic_workerNodesTotalMemoryUsageWithoutConsidBufferedandCachedGB_*.csv')}]
        },
        'kafka_net_worker': {
            'ax': ax[2][1], 'title': 'Kafka Streams - Worker Network Traffic', 'ylabel': 'MB/s', 'ylim': (-5, 60),
            'series': [{'label': 'Workers', 'pattern': get_pattern(args.kafka_path, args.kafka_exp, 'generic_workerNodesNetworkReceiveMB_60s_*.csv'), 'smooth': True}]
        },
        'kafka_cpu_additional': {
            'ax': ax[3][1], 'title': 'Kafka Streams - Additional nodes CPUs usage', 'ylabel': 'CPUs Usage (%)', 'ylim': (0, 100),
            'series': [
                {'pattern': get_pattern(args.kafka_path, args.kafka_exp, args.broker_cpu_pattern), 'pivot': True},
                {'pattern': get_pattern(args.kafka_path, args.kafka_exp, args.manager_cpu_pattern), 'pivot': True}
            ]
        }
    }

    # Tempos de início independentes
    spark_pattern = get_pattern(args.spark_path, args.spark_exp, 'generic_workerNodesCPUsPercentageUtilization_60s_*.csv')
    spark_file = glob.glob(spark_pattern)
    if not spark_file:
        print(f"Erro: Não foi possível encontrar arquivos de dados do SPARK para determinar o tempo inicial. Saindo.\nPadrão procurado: {spark_pattern}")
        return
    df_spark_temp = pd.read_csv(spark_file[0])
    spark_start_time = pd.to_datetime(df_spark_temp['timestamp'].min(), unit='s')

    kafka_pattern = get_pattern(args.kafka_path, args.kafka_exp, 'generic_workerNodesCPUsPercentageUtilization_60s_*.csv')
    kafka_file = glob.glob(kafka_pattern)
    if not kafka_file:
        print(f"Erro: Não foi possível encontrar arquivos de dados do KAFKA para determinar o tempo inicial. Saindo.\nPadrão procurado: {kafka_pattern}")
        return
    df_kafka_temp = pd.read_csv(kafka_file[0])
    kafka_start_time = pd.to_datetime(df_kafka_temp['timestamp'].min(), unit='s')
    
    for key, definition in plot_definitions.items():
        start_time_to_use = spark_start_time if 'spark' in key.lower() else kafka_start_time
        create_subplot(definition['ax'], definition, start_time_to_use, args.duration)

    fig.suptitle(f'Average Resource Consumption for {args.registers}/s Load', fontsize=24, y=1.02)
    fig.tight_layout(pad=3.0)
    output_dir = '../plots'
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f'{output_dir}/resources-average-{args.registers}-final'
    plt.savefig(f'{output_filename}.pdf')
    plt.savefig(f'{output_filename}.png')
    print(f"Gráficos salvos em {output_filename}.(pdf/png)")

if __name__ == '__main__':
    main()
