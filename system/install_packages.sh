#!/bin/bash

# 判断是否安装了sudo
if command -v sudo >/dev/null 2>&1; then
  SUDO_CMD="sudo"
else
  SUDO_CMD=""
fi

# 安装软件包
install_package() {
  package=$1
  install_command=$2
  requirements_file=$3

  echo "正在安装 $package ..."
  case "$install_command" in
    --apt)
      $SUDO_CMD apt-get install -y "$package"
      ;;
    --npm)
      npm install "$package" -g
      ;;
    --pip)
      if [[ -n "$requirements_file" ]]; then
        $SUDO_CMD pip install -r "$requirements_file" --index-url=https://homura:glpat-o-b638z3PY5R6_RVs3Bb@gitlab.homura.top:86/api/v4/projects/11/packages/pypi 
      else
        $SUDO_CMD pip install "$package"
      fi
      ;;
    --pip3)
      if [[ -n "$requirements_file" ]]; then
        $SUDO_CMD pip3 install -r "$requirements_file"
      else
        $SUDO_CMD pip3 install "$package"
      fi
      ;;
    *)
      echo "未知的安装命令: $install_command"
      ;;
  esac

  echo "安装完成 $package"
  echo
}

# 从配置文件安装软件包
install_from_config_file() {
  config_file=$1

  # 读取配置文件
  while IFS= read -r line; do
    # 跳过空行和注释行
    if [[ $line =~ ^[[:space:]]*$ || $line =~ ^[[:space:]]*# ]]; then
      continue
    fi

    # 解析配置行
    packages=($line)

    # 安装软件包
    install_command=""
    for package in "${packages[@]}"; do
      if [[ "$package" == "--apt" || "$package" == "--npm" || "$package" == "--pip" || "$package" == "--pip3" ]]; then
        install_command="$package"
      elif [[ "$install_command" != "" ]]; then
        install_package "$package" "$install_command"
      else
        echo "未知的安装命令: $install_command"
      fi
    done
  done < "$config_file"
}

# 安装软件包从命令行参数
install_from_command_line() {
  while (( "$#" )); do
    if [[ "$1" == "--apt" ]]; then
      shift
      while [[ "$1" != "" && "$1" != "--"* ]]; do
        install_package "$1" --apt
        shift
      done
    elif [[ "$1" == "--npm" ]]; then
      shift
      while [[ "$1" != "" && "$1" != "--"* ]]; do
        install_package "$1" --npm
        shift
      done
    elif [[ "$1" == "--pip" ]]; then
      shift
      while [[ "$1" != "" && "$1" != "--"* ]]; do
        install_package "$1" --pip
        shift
      done
    elif [[ "$1" == "--pip3" ]]; then
      shift
      while [[ "$1" != "" && "$1" != "--"* ]]; do
        install_package "$1" --pip3
        shift
      done
    else
      echo "未知的命令参数: $1"
      shift
    fi
  done
}

# 主函数

# 判断是从配置文件安装还是从命令行参数安装
if [[ -f "$1" ]]; then
  install_from_config_file "$1"
else
  install_from_command_line "$@"
fi
