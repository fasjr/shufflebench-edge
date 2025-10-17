# Pacote para Reprodução para: MEDINDO O DESEMPENHO DE DISTRIBUTED STREAM PROCESSING EM EDGE COMPUTING

Nossa dissertação de mestrado, *Medindo o Desempenho de Distributed Stream Processing em Edge Computing*, utiliza o *ShuffleBench* para medir o comportamento de frameworks de DSP como o Kafka Streams e o Spark Structured Streaming em ambientes de computação de borda com recursos escassos. Usando o ShuffleBench, o estudo visa identificar otimizações de desempenho para essas tecnologias.

Este documento descreve como replicar a avaliação experimental do nosso estudo, bem como executar os experimentos.

## Shufflebench

Utilizamos a branch "ShuffleBench-Fault-tolerance-DEBS24" do shufflebench, devido a mesma conter várias definições de métricas de uso de recursos extendidas. (https://github.com/dynatrace-research/ShuffleBench/blob/ShuffleBench-Fault-tolerance-DEBS24/evaluation/fault-tolerance/kstreams-baseline-ft.yaml)

Instruções de implementação do ambiente a partir desta branch está localizada em https://zenodo.org/records/11348948/README.md 

# Executando o ShuffleBench em Kubernetes

Instalar o Theodolite [Theodolite](https://www.theodolite.rocks/) um framework para execução de benckmarks de forma escalável em Kubernetes.

Utilizar o Theodolite a partir da branch ShuffleBench-Fault-tolerance-DEBS24 do ShuffleBench.
```sh 
  helm dependencies update theodolite/helm
  helm install theodolite ./theodolite/helm -f https://raw.githubusercontent.com/cau-se/theodolite/main/helm/preconfigs/extended-metrics.yaml -f values.yaml -f values-aws-nodegroups.yaml
   
```
## Instalar Theodolite Benchmarks

Os arquivos de deploy dos benchmarks e do executions dos experimentos estão localizados em "ShuffleBench"

Baixar o deploy deste repositório "ShuffleBench\Kubernetes" e a partir da pasta, execute:
```sh
# Delete configmaps if already created before
kubectl delete configmaps --ignore-not-found=true shufflebench-resources-load-generator shufflebench-resources-latency-exporter shufflebench-resources-kstreams shufflebench-resources-spark 
kubectl create configmap shufflebench-resources-load-generator --from-file ./shuffle-load-generator/
kubectl create configmap shufflebench-resources-latency-exporter --from-file ./shuffle-latency-exporter/
kubectl create configmap shufflebench-resources-kstreams --from-file ./shuffle-kstreams/
kubectl create configmap shufflebench-resources-spark --from-file ./shuffle-sparkStructuredStreaming/

kubectl apply -f theodolite-benchmark-kstreams.yaml
kubectl apply -f theodolite-benchmark-spark.yaml
```
Execute esse comando, para verificar se os benchmarks estão prontos para execução:

```sh 
kubectl get benchmarks
```
#Executar os Experimentos:

Os arquivos YAML de deploy dos experimentos estão localizados em:`ShuffleBench\evaluation\edge\`

Execute:
```sh
kubectl apply -f kstreams-baseline-ft.yaml
kubectl apply -f spark-baseline-ft.yaml
# ...
```

#acompanhar a execucao
   
```sh
   kubectl logs -l app=theodolite -c theodolite -f --tail 10 
```
Depois do tempo de experimento definido, então execute o comando abaixo para avaliar o status da execução do benchmark:

```sh
   kubectl get executions
```
### Coletando os Resultados dos Benchmarks

```sh
mkdir -p results-local
kubectl cp $(kubectl get pod -l app=theodolite -o jsonpath="{.items[0].metadata.name}"):results results-local -c results-access
```
Depois copie essa pasta de resultados `/results-local` para a sua maquina local.

### Analisar os Resultados de Benchmark e Replicar a Análise

A seguir, descrevemos a análise dos resultados dos experimentos do nosso estudo, que estão disponíveis no caminho `test/results/`.

Para analisar e visualizar os resultados de benchmark, nós fornecemos os resultados coletados dos experimentos (formato CSV) e o script Python para gerar as visualizações, que pode ser personalizado para outros experimentos. É necessária uma instalação do Python 3 com algumas bibliotecas.

Dentro do diretório `test/results` existem subpastas para os diferentes experimentos e sua respectiva pasta `plot`, que contém a visualização gerada em formato PDF e PNG. A pasta TLI contém os experimentos relacionados à Throughput, Latência e Input Lag, enquanto a pasta Recursos contém os experimentos preliminares relacionados à consumo de recursos como Uso de CPU, Memória e Tráfego de Rede.

Para o Script resources_plot temos os seguintes parâmetros de entrada para execução:

1. kafka-exp: ID do experimento do Kafka Streams

2. spark-exp: ID do experimento do Spark Structured Streaming

3. registers: Quantidade de registros de entrada que foi usado no experimento.

4. instances: Quantidade de Instancias que foram usadas.

5. path: Caminho com os arquivos de coleta dos experimentos.


Para o Script resources_plot temos os seguintes parâmetros de entrada para execução:

1. kafka-exp: ID do experimento do Kafka Streams

2. spark-exp: ID do experimento do Spark Structured Streaming
 
3. exp-id: ID do experimento

4. registers: Quantidade de registros de entrada que foi usado no experimento.

5. instances: Quantidade de Instancias que foram usadas.

6. spark-exp: ID do experimento do Spark Structured Streaming

7. input-path: Caminho com os arquivos de coleta dos experimentos.

8. output-path: Caminho com os arquivos de plot dos resultados.

9. output-name: Nome do arquivo com os arquivos de plot dos resultados.

10. duration: Tempo de execução dos experimentos.

11. ylim-input-tp: Define o limite do eixo Y para o throughput de entrada.

12. ylim-output-tp: Define o limite do eixo Y para o throughput de saída.

13. ylim-latency: Define o limite do eixo Y para a latência.

14. ylim-lag: Define o limite do eixo Y para o lag.


## Replicação da Avaliação Experimental

A melhor forma de replicar a avaliação experimental do nosso estudo é seguir o repositório do GitHub e na branch master, criada para nossos experimentos do  [ShuffleBench Fault tolerant implementation folder](ShuffleBench) para edge computing. Lá, fornecemos um guia sobre como instalar, implantar e executar experimentos com o ShuffleBench para edge computing.



## Avaliações de Desempenho Personalizadas com o ShuffleBench


ShuffleBench é mantido como um projeto de código aberto no GitHub (https://github.com/dynatrace-research/ShuffleBench). Ele fornece implementações de benchmark para diferentes frameworks de processamento de fluxo (stream processing) de última geração, bem como ferramentas associadas para automatizar a execução de benchmarks em ambientes de nuvem baseados em Kubernetes. A documentação sobre como compilar e empacotar as implementações a partir do código-fonte ((https://github.com/dynatrace-research/ShuffleBench/blob/main/README.md) e como executar implementações personalizadas é fornecida no projeto do GitHub (https://github.com/dynatrace-research/ShuffleBench/tree/main/kubernetes) .



