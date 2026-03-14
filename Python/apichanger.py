#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json

# 跨平台兼容：固定工作目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

# 加载配置
def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

# 保存配置
def save_config(config):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def main():
    print("=== 端口配置 ===")
    config = load_config()
    default_addr = f"{config['host']}:{config['port']}"

    while True:
        user_input = input(f"请输入端口地址(default={default_addr}): ").strip()
        
        # 未输入，使用默认值
        if not user_input:
            print(f"使用默认端口地址：{default_addr}")
            break
        
        # 校验输入格式，仅可修改冒号后部分
        if not user_input.startswith(f"{config['host']}:"):
            print(f"警告：地址必须以 {config['host']}: 开头，仅可修改冒号后的端口部分")
            continue
        
        # 提取端口并校验
        port_str = user_input.split(":", 1)[1].strip()
        if not port_str.isdigit():
            print("警告：端口必须为纯数字，请重新输入")
            continue
        
        port = int(port_str)
        if port < 1 or port > 65535:
            print("警告：端口必须在1-65535之间，请重新输入")
            continue
        
        # 校验通过，保存配置
        config['port'] = port
        save_config(config)
        print(f"端口已设置为：{config['host']}:{config['port']}")
        break

if __name__ == "__main__":
    main()