# Pacote para Reprodução para: MEASURING THE PERFORMANCE OF DISTRIBUTED STREAM PROCESSING IN EDGE COMPUTING

Nossa dissertação de mestrado, *Medindo o Desempenho de Distributed Stream Processing em Edge Computing*, utiliza o *ShuffleBench* para medir o comportamento de frameworks de DSP como o Kafka Streams e o Spark Structured Streaming em ambientes de computação de borda com recursos escassos. Usando o ShuffleBench, o estudo visa identificar otimizações de desempenho para essas tecnologias.

Este documento descreve como replicar a avaliação experimental do nosso estudo, bem como executar os experimentos.

## Shufflebench

Utilizamos a branch "ShuffleBench-Fault-tolerance-DEBS24" do shufflebench, devido a mesma conter várias definições de métricas de uso de recursos extendidas. (https://github.com/dynatrace-research/ShuffleBench/blob/ShuffleBench-Fault-tolerance-DEBS24/evaluation/fault-tolerance/kstreams-baseline-ft.yaml)

Instruções de implementação desta branch está localizada em https://zenodo.org/records/11348948/README.md 

### Analisar os Resultados de Benchmark e Replicar a Análise

A seguir, descrevemos a análise dos resultados dos experimentos do nosso estudo, que estão disponíveis no caminho `test/results/`.

Para analisar e visualizar os resultados de benchmark, nós fornecemos os resultados coletados dos experimentos (formato CSV) e o script Python para gerar as visualizações, que pode ser personalizado para outros experimentos. É necessária uma instalação do Python 3 com algumas bibliotecas.

Dentro do diretório test/results existem subpastas para os diferentes experimentos e sua respectiva pasta `plot`, que contém a visualização gerada em formato PDF e PNG. A pasta TLI contém os experimentos relacionados à Throughput, Latência e Input Lag, enquanto a pasta Recursos contém os experimentos preliminares relacionados à consumo de recursos como Uso de CPU, Memória e Tráfego de Rede.

Para o Script resources_plot temos os seguintes parâmetros de entrada para execução:

1. kafka-exp: ID do experimento do Kafka Streams

2. spark-exp: ID do experimento do Spark Structured Streaming

3. registers: Quantidade de registros de entrada que foi usado no experimento.

4. instances: Quantidade de Instancias que foram usadas.

5. path: Caminho com os arquivos de coleta dos experimentos.


Para o Script resources_plot temos os seguintes parâmetros de entrada para execução:

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

1. exp-id: ID do experimento

2. registers: Quantidade de registros de entrada que foi usado no experimento.

4. instances: Quantidade de Instancias que foram usadas.

3. spark-exp: ID do experimento do Spark Structured Streaming

4. input-path: Caminho com os arquivos de coleta dos experimentos.

5. output-path: Caminho com os arquivos de plot dos resultados.

6. output-name: Nome do arquivo com os arquivos de plot dos resultados.

7. duration: Tempo de execução dos experimentos.

8. ylim-input-tp: Define o limite do eixo Y para o throughput de entrada.

9. ylim-output-tp: Define o limite do eixo Y para o throughput de saída.

10. ylim-latency: Define o limite do eixo Y para a latência.

11. ylim-lag: Define o limite do eixo Y para o lag.


## Replicação da Avaliação Experimental

The best way to replicate the experimental evaluation of our study is to follow the github repository and the specific branch created for our experiments:. There we provide a guide on how to install, deploy, and run experiments with ShuffleBench and failure injection using Chaos Mesh. 

## Replicação da Avaliação Experimental

A melhor forma de replicar a avaliação experimental do nosso estudo é seguir o repositório do GitHub e na branch master, criada para nossos experimentos do  [ShuffleBench Fault tolerant implementation folder](ShuffleBench) para edge computing. Lá, fornecemos um guia sobre como instalar, implantar e executar experimentos com o ShuffleBench para edge computing.



## Avaliações de Desempenho Personalizadas com o ShuffleBench


ShuffleBench é mantido como um projeto de código aberto no GitHub (https://github.com/dynatrace-research/ShuffleBench). Ele fornece implementações de benchmark para diferentes frameworks de processamento de fluxo (stream processing) de última geração, bem como ferramentas associadas para automatizar a execução de benchmarks em ambientes de nuvem baseados em Kubernetes. A documentação sobre como compilar e empacotar as implementações a partir do código-fonte ((https://github.com/dynatrace-research/ShuffleBench/blob/main/README.md) e como executar implementações personalizadas é fornecida no projeto do GitHub (https://github.com/dynatrace-research/ShuffleBench/tree/main/kubernetes) .



