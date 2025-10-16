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
    """
    Carrega, processa e calcula a média dos dados para uma única série de um gráfico.
    Retorna um DataFrame pronto para ser plotado.
    """
    all_runs = []
    files = glob.glob(file_pattern)
    
    if not files:
        print(f"Aviso: Nenhum arquivo encontrado para o padrão: {file_pattern}")
        return None

    for file_path in files:
        try:
            df = pd.read_csv(file_path)
            if 'timestamp' in df.columns and 'value' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                df['value'] = pd.to_numeric(df['value'], errors='coerce')
                df.dropna(subset=['value'], inplace=True)
                all_runs.append(df)
        except Exception as e:
            print(f"Erro ao processar o arquivo {file_path}: {e}")
            continue

    if not all_runs:
        return None
        
    concatenated_df = pd.concat(all_runs).sort_values('timestamp')
    
    # Se houver a coluna 'labels', calcula a média entre diferentes pods/instâncias
    if 'labels' in concatenated_df.columns:
        all_pod_data = []
        for pod_id in concatenated_df['labels'].unique():
            pod_series = concatenated_df[concatenated_df['labels'] == pod_id].set_index('timestamp')['value'].resample('S').mean()
            all_pod_data.append(pod_series)
        aligned_df = pd.concat(all_pod_data, axis=1)
        mean_df = aligned_df.mean(axis=1).reset_index()
    else:
        # Caso não haja 'labels', apenas reamostra os dados
        mean_df = concatenated_df.set_index('timestamp')['value'].resample('S').mean().reset_index()

    mean_df.columns = ['timestamp', 'value']

    if smooth:
        mean_df['value'] = mean_df['value'].rolling(window=10).mean()
        
    return mean_df

def create_subplot(ax_obj, definition, start_time):
    """
    Cria um subplot completo (título, eixos, limites e múltiplas séries de dados).
    """
    ax_obj.set_title(definition['title'], pad=20)
    ax_obj.set_ylabel(definition['ylabel'])
    if definition.get('ylim'):
        ax_obj.set_ylim(definition['ylim'])
    if definition.get('yticks') is not None:
        ax_obj.set_yticks(definition['yticks'])

    ax_obj.plot([0, 1], [1, 1], color='black', linewidth=0.75, clip_on=False, transform=ax_obj.transAxes)

    for series in definition['series']:
        series_df = process_series_data(series['pattern'], series.get('smooth', False))
        if series_df is not None:
            # Calcula os minutos decorridos para o eixo X
            series_df['elapsed_minutes'] = (series_df['timestamp'] - start_time).dt.total_seconds() / 60.0
            ax_obj.plot(series_df['elapsed_minutes'], series_df['value'], label=series['label'])
    
    ax_obj.xaxis.set_major_locator(mticker.MultipleLocator(10))
    ax_obj.legend(loc='upper right')
    ax_obj.set_xlabel('Time (Minutes)')

def main():
    parser = argparse.ArgumentParser(description='Generate resource consumption plots from experiment data.')
    parser.add_argument('--kafka-exp', type=str, default='123', help='Experiment ID for Kafka.')
    parser.add_argument('--spark-exp', type=str, default='124', help='Experiment ID for Spark.')
    parser.add_argument('--registers', type=str, default='5000', help='Number of registers per second.')
    parser.add_argument('--instances', type=str, default='3', help='Number of instances.')
    parser.add_argument('--path', type=str, default='results-local-5k', help='Path to the results directory.')
    # O {broker_id} será substituído por 1 e 2
    parser.add_argument('--kafka-broker-pattern', type=str, 
                        default='generic_kafkaBrokerNodesCPUsPercentageUtilization_60s_{broker_id}.csv',
                        help='Padrão do nome do arquivo para os brokers Kafka, use {broker_id}.')

    args = parser.parse_args()

    plt.rc("text", usetex=False)
    mpl.rcParams.update({'font.size': 18})

    fig, ax = plt.subplots(4, 2, figsize=(20, 20), sharex=False)

    # --- ESTRUTURA DE CONFIGURAÇÃO CENTRALIZADA ---
    # Define todos os 8 gráficos e suas respectivas séries de dados
    
    # Helper para criar nomes de arquivos
    def get_pattern(framework_exp, metric):
        return f'{args.path}/exp{framework_exp}_{args.registers}_{args.instances}_{metric}'

    plot_definitions = {
        'spark_cpu_worker': {
            'ax': ax[0][0], 'title': 'Spark Structured Streaming - Worker CPUs Usage', 'ylabel': 'CPUs Usage (%)', 'ylim': (0, 64),
            'series': [{'label': 'Workers', 'pattern': get_pattern(args.spark_exp, 'generic_workerNodesCPUsPercentageUtilization_60s_*.csv'), 'smooth': True}]
        },
        'spark_mem_worker': {
            'ax': ax[1][0], 'title': 'Spark Structured Streaming - Worker memory usage', 'ylabel': 'Memory usage (GB)', 'ylim': (0, 4.5),
            'series': [{'label': 'Workers', 'pattern': get_pattern(args.spark_exp, 'generic_workerNodesTotalMemoryUsageWithoutConsidBufferedandCachedGB_*.csv')}]
        },
        'spark_net_worker': {
            'ax': ax[2][0], 'title': 'Spark Structured Streaming - Worker network traffic', 'ylabel': 'MB/s', 'ylim': (-5, 150),
            'series': [{'label': 'Workers', 'pattern': get_pattern(args.spark_exp, 'generic_workerNodesNetworkReceiveMB_60s_*.csv'), 'smooth': True}]
        },
        'spark_cpu_additional': {
            'ax': ax[3][0], 'title': 'Spark Structured Streaming - Additional CPUs usage', 'ylabel': 'CPUs Usage (%)', 'ylim': (0, 64),
            'series': [
                # --- AQUI ESTÃO OS DOIS BROKERS ---
                {'label': 'Kafka Broker 1', 'pattern': get_pattern(args.spark_exp, args.kafka_broker_pattern.format(broker_id=1))},
                {'label': 'Kafka Broker 2', 'pattern': get_pattern(args.spark_exp, args.kafka_broker_pattern.format(broker_id=2))},
                {'label': 'Manager', 'pattern': get_pattern(args.spark_exp, 'generic_ManagerPodsCPUsPercentageUtilization60s_*.csv')}
            ]
        },
        'kafka_cpu_worker': {
            'ax': ax[0][1], 'title': 'Kafka Streams - Worker CPUs Usage', 'ylabel': 'CPUs Usage (%)', 'ylim': (0, 64),
            'series': [{'label': 'Workers', 'pattern': get_pattern(args.kafka_exp, 'generic_workerNodesCPUsPercentageUtilization_60s_*.csv'), 'smooth': True}]
        },
        'kafka_mem_worker': {
            'ax': ax[1][1], 'title': 'Kafka Streams - Worker memory usage', 'ylabel': 'Memory usage (GB)', 'ylim': (0, 4.5),
            'series': [{'label': 'Workers', 'pattern': get_pattern(args.kafka_exp, 'generic_workerNodesTotalMemoryUsageWithoutConsidBufferedandCachedGB_*.csv')}]
        },
        'kafka_net_worker': {
            'ax': ax[2][1], 'title': 'Kafka Streams - Worker network traffic', 'ylabel': 'MB/s', 'ylim': (-5, 150),
            'series': [{'label': 'Workers', 'pattern': get_pattern(args.kafka_exp, 'generic_workerNodesNetworkReceiveMB_60s_*.csv'), 'smooth': True}]
        },
        'kafka_cpu_additional': {
            'ax': ax[3][1], 'title': 'Kafka Streams - Additional nodes CPUs usage', 'ylabel': 'CPUs Usage (%)', 'ylim': (0, 64),
            'series': [
                # --- AQUI ESTÃO OS DOIS BROKERS ---
                {'label': 'Kafka Broker 1', 'pattern': get_pattern(args.kafka_exp, args.kafka_broker_pattern.format(broker_id=1))},
                {'label': 'Kafka Broker 2', 'pattern': get_pattern(args.kafka_exp, args.kafka_broker_pattern.format(broker_id=2))}
            ]
        }
    }

    # Determina o tempo inicial global para alinhar o eixo X de todos os gráficos
    # Usa o primeiro padrão de arquivo definido para encontrar o tempo inicial
    first_pattern = plot_definitions['spark_cpu_worker']['series'][0]['pattern']
    first_file = glob.glob(first_pattern)
    if not first_file:
        print("Erro: Não foi possível encontrar arquivos de dados para determinar o tempo inicial. Saindo.")
        return
        
    df_temp = pd.read_csv(first_file[0])
    start_time = pd.to_datetime(df_temp['timestamp'].min(), unit='s')

    # --- LOOP DE PLOTAGEM SIMPLIFICADO ---
    for key, definition in plot_definitions.items():
        create_subplot(definition['ax'], definition, start_time)

    fig.suptitle(f'Average Resource Consumption for {args.registers}/s Load', fontsize=24, y=1.02)
    fig.tight_layout(pad=3.0)

    output_filename = f'../plots/resources-average-{args.registers}-exp{args.spark_exp}'
    plt.savefig(f'{output_filename}.pdf')
    plt.savefig(f'{output_filename}.png')
    print(f"Gráficos salvos em {output_filename}.(pdf/png)")

if __name__ == '__main__':
    main()
