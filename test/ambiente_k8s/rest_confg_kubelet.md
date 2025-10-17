# Redefine o estado do kubeadm, desfazendo configurações anteriores
sudo kubeadm reset -f

# Para e desabilita o serviço kubelet (se estiver ativo)
sudo systemctl stop snap.kubelet.daemon || sudo systemctl stop kubelet.service
sudo systemctl disable snap.kubelet.daemon || sudo systemctl disable kubelet.service

# Remove pacotes APT relacionados ao Kubernetes (se instalados por apt)
sudo apt-get purge -y kubelet kubeadm kubectl kubernetes-cni
sudo apt-get autoremove -y

# Remove os Snaps do Kubernetes e seus dados
sudo snap remove --purge kubelet
sudo snap remove --purge kubeadm
sudo snap remove --purge kubectl
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

#edite o hostname sudo hostnamectl set-hostname
#inclua o ip da vm na lista de hosts sudo nano /etc/hosts
# REINICIA A MÁQUINA VIRTUAL - ESSENCIAL para limpar o estado do kernel e processos
#sudo reboot
