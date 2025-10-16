import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import argparse
import os
import matplotlib as mpl

# --- FUNÇÕES DE PLOTAGEM MODULARIZADAS ---

def load_and_prepare_data(filepath):
    """Carrega um CSV e converte a coluna 'timestamp' para datetime."""
    if not os.path.exists(filepath):
        print(f"Aviso: Arquivo não encontrado: {filepath}")
        return None
    df = pd.read_csv(filepath)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    return df

def thousands_formatter(x, pos):
    """Formata o eixo Y em milhares (ex: 10000 -> 10K)."""
    return f'{x / 1e3:.0f}K'

def plot_throughput(ax, title, ylabel, filepath, ylim=None):
    """Plota um gráfico de throughput (entrada ou saída) com limite de eixo Y opcional."""
    df = load_and_prepare_data(filepath)
    if df is not None:
        ax.plot(df['timestamp'], df['value'], label='Throughput')
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(thousands_formatter))
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.legend(loc='upper right')
        if ylim:
            ax.set_ylim(ylim)

def plot_latency_bar(ax, path_template, ylim=None):
    """Plota o gráfico de barras sobrepostas para latência com limite de eixo Y opcional."""
    df_p50 = load_and_prepare_data(path_template.format(percentile='p50'))
    df_p90 = load_and_prepare_data(path_template.format(percentile='p90'))
    df_p99 = load_and_prepare_data(path_template.format(percentile='p99'))

    if df_p50 is None or df_p90 is None or df_p99 is None:
        print("Não foi possível gerar o gráfico de latência por falta de dados.")
        return

    df_p50.rename(columns={'value': 'p50'}, inplace=True)
    df_p90.rename(columns={'value': 'p90'}, inplace=True)
    df_p99.rename(columns={'value': 'p99'}, inplace=True)

    df_latency = pd.merge(df_p50, df_p90, on='timestamp', how='outer')
    df_latency = pd.merge(df_latency, df_p99, on='timestamp', how='outer').sort_values('timestamp')

    bar_width = 0.0002

    ax.bar(df_latency['timestamp'], df_latency['p99'], width=bar_width, label='p99')
    ax.bar(df_latency['timestamp'], df_latency['p90'], width=bar_width, label='p90')
    ax.bar(df_latency['timestamp'], df_latency['p50'], width=bar_width, label='p50')

    ax.set_title('Latency')
    ax.set_ylabel('Seconds')
    ax.legend(loc='upper right')
    if ylim:
        ax.set_ylim(ylim)

def plot_lag(ax, filepath, ylim=None):
    """Plota o gráfico de lag de entrada com limite de eixo Y opcional."""
    df = load_and_prepare_data(filepath)
    if df is not None:
        ax.plot(df['timestamp'], df['value'], label='Records')
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(thousands_formatter))
        ax.set_title('Input Lag')
        ax.set_ylabel('Lag')
        ax.legend(loc='upper right')
        if ylim:
            ax.set_ylim(ylim)


def main():
    """Função principal para configurar e gerar o gráfico."""
    parser = argparse.ArgumentParser(description='Gera gráficos de performance para experimentos Spark/Kafka.')
    parser.add_argument('--exp-id', type=str, default='3', help='ID do experimento (ex: 3).')
    parser.add_argument('--registers', type=str, default='10000', help='Registros por segundo (ex: 10000).')
    parser.add_argument('--instances', type=str, default='3', help='Número de instâncias (ex: 3).')
    parser.add_argument('--input-path', type=str, default='results-local', help='Diretório onde os CSVs de resultados estão.')
    parser.add_argument('--output-path', type=str, default='../plots', help='Diretório para salvar os gráficos gerados.')
    parser.add_argument('--output-name', type=str, default='spark-3podskill-final-bar', help='Nome base para os arquivos de saída.')
    parser.add_argument('--duration', type=int, default=65, help='Duração em minutos a ser exibida no eixo X.')
    
    # --- NOVOS ARGUMENTOS PARA OS LIMITES DO EIXO Y ---
    parser.add_argument('--ylim-input-tp', type=float, nargs=2, default=None, help='Define o limite do eixo Y para o throughput de entrada (ex: --ylim-input-tp 0 15000).')
    parser.add_argument('--ylim-output-tp', type=float, nargs=2, default=None, help='Define o limite do eixo Y para o throughput de saída (ex: --ylim-output-tp 0 3000).')
    parser.add_argument('--ylim-latency', type=float, nargs=2, default=None, help='Define o limite do eixo Y para a latência (ex: --ylim-latency 0 12).')
    parser.add_argument('--ylim-lag', type=float, nargs=2, default=None, help='Define o limite do eixo Y para o lag (ex: --ylim-lag 0 60000).')
    
    args = parser.parse_args()

    mpl.rcParams.update({'font.size': 11.4})

    base_pattern = f"{args.input_path}/exp{args.exp_id}_{args.registers}_{args.instances}_generic"
    
    path_input_tp = f"{base_pattern}_input_throughput_60s_1.csv"
    path_output_tp = f"{base_pattern}_outputthroughput_60s_1.csv"
    path_latency_template = f"{base_pattern}_latency_{{percentile}}_120s_1.csv"
    path_lag = f"{args.input_path}/exp{args.exp_id}_{args.registers}_{args.instances}_lag-trend_lag trend_1.csv"

    fig, ax = plt.subplots(4, 1, figsize=(10, 5.5))

    # --- PASSANDO OS ARGUMENTOS YLIM PARA AS FUNÇÕES DE PLOTAGEM ---
    plot_throughput(ax[0], 'Application input throughput (read from Kafka)', 'Input (r/s)', path_input_tp, ylim=args.ylim_input_tp)
    plot_throughput(ax[1], 'Application output throughput (written to Kafka)', 'Output (r/s)', path_output_tp, ylim=args.ylim_output_tp)
    plot_latency_bar(ax[2], path_latency_template, ylim=args.ylim_latency)
    plot_lag(ax[3], path_lag, ylim=args.ylim_lag)

    df_temp = load_and_prepare_data(path_input_tp)
    if df_temp is None:
        print("Não foi possível formatar o eixo X por falta de dados.")
        return
        
    start_time = df_temp['timestamp'].min()
    
    def minutes_formatter(x, pos=None):
        current_time = mdates.num2date(x).replace(tzinfo=None)
        minutes = (current_time - start_time).total_seconds() / 60
        return f'{int(minutes)}'

    ax[3].xaxis.set_major_formatter(ticker.FuncFormatter(minutes_formatter))

    for i in range(3):
        ax[i].xaxis.set_major_formatter(plt.NullFormatter())
    
    for axis in ax:
        axis.xaxis.set_major_locator(mdates.MinuteLocator(interval=10))
        axis.set_xlim(start_time, start_time + pd.Timedelta(minutes=args.duration))

    ax[3].set_xlabel('Time (Minutes)')
    plt.tight_layout()
    
    os.makedirs(args.output_path, exist_ok=True)
    output_filepath = os.path.join(args.output_path, args.output_name)
    
    print(f"Salvando gráficos em {output_filepath}.(pdf/png)")
    plt.savefig(f'{output_filepath}.png', bbox_inches='tight', pad_inches=0.05)
    plt.savefig(f'{output_filepath}.pdf', bbox_inches='tight', pad_inches=0.05)


if __name__ == '__main__':
    main()
