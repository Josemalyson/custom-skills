#!/bin/bash
# Auto-installer for k8s-vps-investigation tools
# This script installs missing tools to ~/.local/bin

mkdir -p ~/.local/bin
export PATH=$HOME/.local/bin:$PATH

echo "Checking and installing tools..."

if ! command -v trivy &> /dev/null; then
  echo "Installing Trivy..."
  curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b ~/.local/bin
fi

if ! command -v kubescape &> /dev/null; then
  echo "Installing Kubescape..."
  curl -sL https://github.com/kubescape/kubescape/releases/latest/download/kubescape-ubuntu-latest -o ~/.local/bin/kubescape
  chmod +x ~/.local/bin/kubescape
fi

if ! command -v popeye &> /dev/null; then
  echo "Installing Popeye..."
  curl -sL https://github.com/derailed/popeye/releases/download/v0.22.1/popeye_linux_amd64.tar.gz | tar xz -C ~/.local/bin popeye
  chmod +x ~/.local/bin/popeye
fi

if ! command -v kube-bench &> /dev/null; then
  echo "Installing Kube-bench..."
  curl -sL https://github.com/aquasecurity/kube-bench/releases/download/v0.8.0/kube-bench_0.8.0_linux_amd64.tar.gz | tar xz -C ~/.local/bin kube-bench
  chmod +x ~/.local/bin/kube-bench
fi

if ! command -v helm &> /dev/null; then
  echo "Installing Helm..."
  curl -sL https://get.helm.sh/helm-v3.15.0-linux-amd64.tar.gz | tar xz -C /tmp
  mv /tmp/linux-amd64/helm ~/.local/bin/helm
  chmod +x ~/.local/bin/helm
fi

if ! command -v k9s &> /dev/null; then
  echo "Installing K9s..."
  curl -sL https://github.com/derailed/k9s/releases/latest/download/k9s_Linux_amd64.tar.gz | tar xz -C ~/.local/bin k9s
  chmod +x ~/.local/bin/k9s
fi

if ! command -v kubeshark &> /dev/null; then
  echo "Installing Kubeshark..."
  curl -Lo ~/.local/bin/kubeshark https://github.com/kubeshark/kubeshark/releases/download/v52.3.85/kubeshark_linux_amd64
  chmod +x ~/.local/bin/kubeshark
fi

if ! command -v lynis &> /dev/null; then
  echo "Installing Lynis..."
  git clone https://github.com/CISOfy/lynis ~/.local/share/lynis 2>/dev/null || (cd ~/.local/share/lynis && git pull)
  ln -sf ~/.local/share/lynis/lynis ~/.local/bin/lynis
fi

if ! command -v glances &> /dev/null; then
  echo "Installing Glances..."
  pipx install glances || pip3 install --user glances
fi

echo "Done! Make sure ~/.local/bin is in your PATH."
