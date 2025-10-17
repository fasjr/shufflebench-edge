# Atualiza a lista de pacotes e instala pré-requisitos
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg apt-transport-https gnupg2 software-properties-common

# Adiciona a chave GPG oficial do Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Adiciona o repositório oficial do Docker ao Apt
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Instala o Containerd.io
sudo apt-get install -y containerd.io

# Gera a configuração padrão do Containerd e define o cgroup driver como systemd (compatível com kubelet)
sudo containerd config default | sudo tee /etc/containerd/config.toml
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml

# Reinicia e habilita o Containerd
sudo systemctl enable containerd
sudo systemctl restart containerd

sudo swapoff -a
sudo sed -i ‘/swap/d’ /etc/fstab

# VERIFIQUE AQUI: O Containerd DEVE estar "active (running)"
sudo systemctl status containerd

#instalar k8s

#Configure Sysctl Settings for Kubernetes Networking
sudo modprobe br_netfilter
ls /proc/sys/net/bridge/bridge-nf-call-iptables

#edite o arquivo k8s.conf
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF>>

sudo sysctl --system

#Add Kubernetes Repository

echo deb https://pkgs.k8s.io/core:/stable:/v1.27/deb/ / | sudo tee /etc/apt/sources.list.d/kubernetes.list
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
sudo chmod 755 /etc/apt/keyrings
sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg

#Install Kubernetes Components
sudo apt-get update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

sudo systemctl enable kubelet

mkdir -p $HOME/.kube

sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config

sudo chown $(id -u):$(id -g) $HOME/.kube/config

###iniciando o master
### Finalizar o processo (substitua <PID> pelo número que você encontrou)
PID=$(sudo lsof -t -i :10250)
sudo lsof -t -i :6443
if [ -n "$PID" ]; then
    sudo kill -9 "$PID"
    echo "Processo $PID finalizado."
else
    echo "Nenhum processo encontrado na porta 10250 para finalizar."
fi
sudo kubeadm init --config config.yaml --upload-certs --v=5 --ignore-preflight-errors=all

#nodes
cat ~/.kube/config
# OU, se estiver no nó master:
sudo cat /etc/kubernetes/admin.conf

#Se estiver apontando para localhost:8080
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config


#iniciando os nodos
sudo kubeadm join 192.168.20.214:6443 \
    --token $token \
	--discovery-token-ca-cert-hash sha256: $cert
    --cri-socket unix:///var/run/containerd/containerd.sock
    
#sudo nano kubeadm-join-config.yaml
#sudo kubeadm join --config kubeadm-join-config.yaml

#arquivo kubeadm-join-config.yaml
#apiVersion: kubeadm.k8s.io/v1beta3
#kind: JoinConfiguration
#nodeRegistration:
#  criSocket: unix:///var/run/containerd/containerd.sock
#discovery:
#  bootstrapToken:
#    token: $token
#    apiServerEndpoint: 192.168.20.214:6443
#    caCertHashes: 
#    - sha256:$cert

