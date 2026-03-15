#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import socket

# 跨平台兼容：固定工作目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# 配置文件路径
CONFIG_FILE = "config.json"

def load_config():
    """加载配置文件，增加容错处理"""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # 确保配置项存在且类型正确
        config.setdefault("host", "127.0.0.1")
        # 统一端口为整数类型（兼容原有字符串格式）
        config["port"] = int(config.get("port", 5000))
        
        return config
    except FileNotFoundError:
        print(f"警告：配置文件 {CONFIG_FILE} 不存在，使用默认配置")
        return {"host": "127.0.0.1", "port": 5000}
    except json.JSONDecodeError:
        print(f"警告：配置文件 {CONFIG_FILE} 格式错误，使用默认配置")
        return {"host": "127.0.0.1", "port": 5000}
    except Exception as e:
        print(f"加载配置时发生错误：{e}，使用默认配置")
        return {"host": "127.0.0.1", "port": 5000}

def save_config(config):
    """保存配置文件，增加异常处理"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存配置失败：{e}")
        return False

def is_port_available(host, port):
    """检测端口是否可用（可选功能）"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0
    except Exception:
        return True  # 检测失败时默认认为端口可用

def main():
    print("=== 端口配置工具 ===")
    
    config = load_config()
    default_host = config['host']
    default_port = config['port']
    default_addr = f"{default_host}:{default_port}"

    while True:
        user_input = input(f"\n请输入端口地址 (default={default_addr}): ").strip()
        
        # 未输入，使用默认值
        if not user_input:
            print(f"\n使用默认端口地址：{default_addr}")
            
            # 可选：检测默认端口是否可用
            if not is_port_available(default_host, default_port):
                print(f"警告：端口 {default_port} 可能已被占用！")
            
            break
        
        # 校验输入格式，仅可修改冒号后部分
        if not user_input.startswith(f"{default_host}:"):
            print(f"❌ 错误：地址必须以 {default_host}: 开头，仅可修改冒号后的端口部分")
            continue
        
        # 提取端口并校验
        try:
            port_str = user_input.split(":", 1)[1].strip()
            if not port_str.isdigit():
                print("❌ 错误：端口必须为纯数字，请重新输入")
                continue
            
            port = int(port_str)
            if port < 1 or port > 65535:
                print("❌ 错误：端口必须在1-65535之间，请重新输入")
                continue
            
            # 可选：检测端口是否可用
            if not is_port_available(default_host, port):
                choice = input(f"⚠️  警告：端口 {port} 已被占用，是否继续使用？(y/N) ").strip().lower()
                if choice != 'y':
                    continue
            
            # 校验通过，更新配置
            config['port'] = port
            
            # 保存配置
            if save_config(config):
                print(f"\n✅ 端口配置成功！")
                print(f"当前配置：{config['host']}:{config['port']}")
            else:
                print("\n❌ 端口配置失败，配置文件未更新")
            
            break
        
        except Exception as e:
            print(f"❌ 输入处理错误：{e}，请重新输入")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n程序运行出错：{e}")
        sys.exit(1)

