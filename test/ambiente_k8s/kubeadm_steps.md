# Atualiza a lista de pacotes e instala pré-requisitos
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# Adiciona a chave GPG oficial do Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Adiciona o repositório Docker ao Apt sources
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Instala o Containerd
sudo apt-get install -y containerd.io

# Gera a configuração padrão do Containerd e define o cgroup driver como systemd
sudo containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml

# Reinicia e habilita o Containerd
sudo systemctl daemon-reload
sudo systemctl enable containerd
sudo systemctl restart containerd

# Verifica o status
sudo systemctl status containerd

# Finalizar o processo (substitua <PID> pelo número que você encontrou)
PID=$(sudo lsof -t -i :10250)
if [ -n "$PID" ]; then
    sudo kill -9 "$PID"
    echo "Processo $PID finalizado."
else
    echo "Nenhum processo encontrado na porta 10250 para finalizar."
fi

#Conteúdo do config.yaml (Exemplo):
# config.yaml
#apiVersion: kubeadm.k8s.io/v1beta3
#kind: InitConfiguration
#nodeRegistration:
#  criSocket: unix:///var/run/containerd/containerd.sock
#---
#apiVersion: kubeadm.k8s.io/v1beta3
#kind: ClusterConfiguration
# Não é estritamente necessário para 'images pull', mas é bom manter para o 'init'
#networking:
#  podSubnet: 10.244.0.0/16
#imageRepository: docker.io # Se você quer puxar do docker.io

sudo kubeadm config images pull --config config.yaml


# Redefine o estado do kubeadm
sudo kubeadm reset -f

# Parar e desabilitar o kubelet
sudo systemctl stop snap.kubelet.daemon || sudo systemctl stop kubelet.service
sudo systemctl disable snap.kubelet.daemon || sudo systemctl disable kubelet.service

# Remover todos os pacotes relacionados ao Kubernetes (se instalados via APT)
sudo apt-get purge -y kubelet kubeadm kubectl kubernetes-cni
sudo apt-get autoremove -y

# Remover todos os snaps do Kubernetes
sudo snap remove --purge kubelet
sudo snap remove --purge kubeadm
sudo snap remove --purge kubectl

# Remover diretórios de configuração e dados do Kubernetes que podem ter sobrado
sudo rm -rf /etc/kubernetes/
sudo rm -rf /var/lib/kubelet/
sudo rm -rf /var/lib/etcd/
sudo rm -rf ~/.kube/

# Limpar regras de iptables
sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -t raw -F
sudo iptables -X

#Desativar Firewall (UFW) Temporariamente para Teste:
sudo ufw disable

# Parar e remover completamente o Containerd (para uma instalação limpa e mais recente)
sudo systemctl stop containerd
sudo apt-get purge -y containerd.io
sudo apt-get autoremove -y
sudo rm -rf /etc/containerd/
sudo rm -rf /var/lib/containerd/

# Reiniciar a VM - ISSO É CRÍTICO
#sudo reboot


# Atualiza a lista de pacotes e instala pré-requisitos
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

# Adiciona a chave GPG oficial do Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Adiciona o repositório Docker ao Apt sources
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Instala o Containerd.io (ele puxará a versão mais recente disponível)
sudo apt-get install -y containerd.io

# Gera a configuração padrão do Containerd e define o cgroup driver como systemd
sudo containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml

# Reinicia e habilita o Containerd
sudo systemctl enable containerd
sudo systemctl restart containerd

# Verifica o status
sudo systemctl status containerd

#Instalar Kubelet, Kubeadm e Kubectl (Via Snap, que se mostrou mais estável no 24.04):
sudo snap install kubelet --classic
sudo snap install kubeadm --classic
sudo snap install kubectl --classic

#Habilitar o serviço Kubelet:
sudo systemctl enable snap.kubelet.daemon
sudo systemctl start snap.kubelet.daemon
sudo systemctl status snap.kubelet.daemon

#Tente o comando kubeadm init novamente:
# Finalizar o processo (substitua <PID> pelo número que você encontrou)
PID=$(sudo lsof -t -i :10250)
sudo lsof -t -i :6443
if [ -n "$PID" ]; then
    sudo kill -9 "$PID"
    echo "Processo $PID finalizado."
else
    echo "Nenhum processo encontrado na porta 10250 para finalizar."
fi
sudo kubeadm init --config config.yaml --upload-certs --v=5 --ignore-preflight-errors=all




sudo systemctl stop kubelet
sudo systemctl stop containerd
sudo rm -rf /var/lib/etcd/* # Apaga os dados do etcd
sudo systemctl start containerd
sudo systemctl restart kubelet




# Redefine o estado do kubeadm, desfazendo configurações anteriores
sudo kubeadm reset -f

# Para e desabilita o serviço kubelet (se estiver ativo)
sudo systemctl stop snap.kubelet.daemon || sudo systemctl stop kubelet.service
sudo systemctl disable snap.kubelet.daemon || sudo systemctl disable kubelet.service

# Remove pacotes APT relacionados ao Kubernetes (se instalados por apt)
sudo apt-get purge -y kubelet kubeadm kubectl kubernetes-cni
sudo apt-get autoremove -y

# Remove os Snaps do Kubernetes e seus dados
sudo apt remove kubelet
sudo apt remove kubeadm
sudo apt remove kubectl

# Remove diretórios de configuração e dados do Kubernetes que podem ter sobrado
sudo rm -rf /etc/kubernetes/
sudo rm -rf /var/lib/kubelet/
sudo rm -rf /var/lib/etcd/
sudo rm -rf ~/.kube/
sudo rm -rf /var/run/kubernetes/

# Limpa as regras do iptables (importante para a rede do cluster)
sudo iptables -F && sudo iptables -t nat -F && sudo iptables -t mangle -F && sudo iptables -t raw -F
sudo iptables -X

# Para e remove completamente o Containerd e seus dados
sudo systemctl stop containerd
sudo apt-get purge -y containerd.io
sudo apt-get autoremove -y
sudo rm -rf /etc/containerd/
sudo rm -rf /var/lib/containerd/

curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo tee /etc/apt/trusted.gpg.d/kubernetes.asc
sudo nano /etc/apt/sources.list.d/kubernetes.list
deb https://pkgs.k8s.io/core:/stable:/v1.33/deb/ /

sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

sudo systemctl enable kubelet
sudo systemctl start kubelet

# VERIFIQUE AQUI: O kubelet DEVE estar "active (running)"
sudo systemctl status kubelet

sudo sysctl net.ipv4.ip_forward=1

kubeadm join 192.168.20.214:6443 --token 6vhm4y.1ev30c7z4rlil507 \
	--discovery-token-ca-cert-hash sha256:9c4296d9a2a6b329bb20cc0ef86f057f5779bf87bfbb4cf5991ac64e194a3ed6 

sudo kubeadm join 192.168.20.214:6443 \
    --token 6vhm4y.1ev30c7z4rlil507 \
    --discovery-token-ca-cert-hash sha256:9c4296d9a2a6b329bb20cc0ef86f057f5779bf87bfbb4cf5991ac64e194a3ed6 \
    --cri-socket unix:///var/run/containerd/containerd.sock


Crie um arquivo YAML, por exemplo, kubeadm-join-config.yaml:
apiVersion: kubeadm.k8s.io/v1beta3
kind: JoinConfiguration
nodeRegistration:
  criSocket: unix:///var/run/containerd/containerd.sock
token: xdf5hn.cii2o4c6qr0uk8f8
discovery:
  bootstrapToken:
    apiServerEndpoint: 192.168.20.214:6443
    token: xdf5hn.cii2o4c6qr0uk8f8
    caCertHash: sha256:429fb721db39d4244862cf1fa444ed3ba06ce56051253fd3b2715202d780a10b

Execute o kubeadm join usando este arquivo:
sudo kubeadm join --config kubeadm-join-config.yaml


 # Cria o diretório .kube se ele não existir
 mkdir -p $HOME/.kube
 # Copia o arquivo de configuração do administrador gerado pelo kubeadm
 sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
 # Define as permissões corretas para o arquivo
 sudo chown $(id -u):$(id -g) $HOME/.kube/config
 # Opcional: Define a variável de ambiente KUBECONFIG (útil para sessões futuras)
 echo "export KUBECONFIG=$HOME/.kube/config" >> ~/.bashrc

curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.27/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
