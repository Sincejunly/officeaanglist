#!/bin/bash
has_sudo=$(command -v sudo)
source_params='qinghua'
# 遍历所有参数
while [ $# -gt 0 ]; do
  case "$1" in
    --apt)
      shift
      apt_params="$@"
      break
      ;;
    --yum)
      shift
      yum_params="$@"
      break
      ;;
    --dnf)
      shift
      dnf_params="$@"
      break
      ;;
    --source)
      shift
      source_params="$@"
      break
      ;;
    *)
      echo "Unknown parameter: $1"
      shift
      ;;
  esac
done

# Check system distribution
OS='unknown'
if [ -f "/etc/apt/sources.list" ]; then
  # 如果存在 /etc/apt/sources.list 文件，则读取其内容
  sources_list=$(cat /etc/apt/sources.list)
  cp /etc/apt/sources.list /etc/apt/sources.list.bak
  if [ -n "$has_sudo" ]; then
    sed_cmd="sudo sed"
    apt_cmd="sudo apt-get"
  else
    sed_cmd="sed"
    apt_cmd="apt-get"
  fi
  # 判断是否包含 'ubuntu.com' 字符串
  if echo "$sources_list" | grep -q 'ubuntu.com'; then
    $sed_cmd -i 's/archive.ubuntu.com/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
    $sed_cmd -i 's#http://security.ubuntu.com/ubuntu#http://mirrors.tuna.tsinghua.edu.cn/ubuntu#g' /etc/apt/sources.list
    $apt_cmd update
    OS='Ubuntu'
  else
    $sed_cmd -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
    $sed_cmd -i 's/security.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
    $apt_cmd update
    OS='Debian'
  fi
else
  # 如果不存在 /etc/apt/sources.list 文件，则判断是否为 CentOS
  if [ -f "/etc/centos-release" ]; then
      if grep -q "CentOS Linux release 7" /etc/centos-release; then
          if [ -n "$has_sudo" ]; then
            sed_cmd="sudo sed"
            yum_cmd="sudo yum"
          else
            sed_cmd="sed"
            yum_cmd="yum"
          fi
          echo "This is a CentOS 7 system."
          $sed_cmd -e 's|^mirrorlist=|#mirrorlist=|g' \
          -e 's|^#baseurl=http://mirror.centos.org/centos|baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos|g' \
          -i.bak \
          /etc/yum.repos.d/CentOS-*.repo
          $yum_cmd makecache
          OS='CentOS 7'
      elif grep -q "CentOS Linux release 8" /etc/centos-release; then
          if [ -n "$has_sudo" ]; then
            sed_cmd="sudo sed"
            dnf_cmd="sudo dnf"
          else
            sed_cmd="sed"
            dnf_cmd="dnf"
          fi      
          echo "This is a CentOS 8 system."
          $sed_cmd -e 's|^mirrorlist=|#mirrorlist=|g' \
          -e 's|^#baseurl=http://mirror.centos.org/$contentdir|baseurl=https://mirrors.tuna.tsinghua.edu.cn/centos|g' \
          -i.bak \
          /etc/yum.repos.d/CentOS-*.repo
          $dnf_cmd makecache
          OS='CentOS 8'
      else
          echo "Unknown CentOS system version."
      fi
  else
      echo "Unknown system."
  fi

fi

if [[ $OS == *"CentOS 7"* && -n $yum_params ]]; then
  if [ -n "$has_sudo" ]; then
    sudo ./install_packages.sh --yum $yum_params
  else
    ./install_packages.sh --yum $yum_params
  fi      
elif [[ $OS == *"CentOS 8"* && -n $dnf_params ]]; then
  if [ -n "$has_sudo" ]; then
    sudo ./install_packages.sh --dnf $dnf_params
  else
    ./install_packages.sh --dnf $dnf_params
  fi      
elif [[ $OS == *"Ubuntu"* && -n $apt_params ]]; then
  if [ -n "$has_sudo" ]; then
    sudo ./install_packages.sh --apt $apt_params
  else
    ./install_packages.sh --apt $apt_params
  fi      
elif [[ $OS == *"Debian"* && -n $apt_params ]]; then
  if [ -n "$has_sudo" ]; then
    sudo ./install_packages.sh --apt $apt_params
  else
    ./install_packages.sh --apt $apt_params
  fi
else
  echo "Unknown system."
fi


if command -v python3 &>/dev/null; then
  echo "Python 3 is installed"
  # Set the pip source to Tsinghua University
  python3 -m pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
fi

# 判断是否存在npm环境
if $(command -v npm &> /dev/null); then
    # 判断系统版本并设置npm源
    npm config set registry https://registry.npm.taobao.org
    npm install -g yarn
    yarn config set registry https://registry.npm.taobao.org/
fi