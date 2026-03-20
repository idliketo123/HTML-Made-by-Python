#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def clear_all_data():
    default_config = {
        "host": "127.0.0.1",
        "port": 5000,
        "html_title": "Hello World!",
        "page_title": "Hello Sekai!",
        "title_font_size": 36,
        "text_font_size": 16,
        "custom_font": None
    }
    save_config(default_config)
    if os.path.exists("content.html"):
        with open("content.html", "w", encoding="utf-8") as f:
            f.write("")
    if os.path.exists("logs"):
        shutil.rmtree("logs")
        os.makedirs("logs")
    print("所有数据已清除，配置重置为默认值")

# 从resources.py复制的文件选择函数
def select_file(file_type_desc, extensions):
    files = []
    for root, dirs, files_in_dir in os.walk("."):
        for f in files_in_dir:
            if f.lower().endswith(extensions):
                files.append(os.path.join(root, f))
    if not files:
        print(f"未找到任何{file_type_desc}文件！")
        return None
    print(f"\n可用{file_type_desc}：")
    for i, path in enumerate(files):
        print(f"{i+1}. {path}")
    while True:
        try:
            choice = input(f"请选择{file_type_desc}（输入数字）：").strip()
            if not choice:
                return None
            choice = int(choice)
            if 1 <= choice <= len(files):
                return files[choice - 1]
            else:
                print("输入超出范围！")
        except ValueError:
            print("请输入有效数字！")

# 主函数直接执行，无任何try/except/finally
def main():
    print("=== 页面初始化配置 ===")
    # 初始化配置文件
    if not os.path.exists("config.json"):
        save_config({
            "host": "127.0.0.1",
            "port": 5000,
            "html_title": "Hello World!",
            "page_title": "Hello Sekai!",
            "title_font_size": 36,
            "text_font_size": 16,
            "custom_font": None
        })
    config = load_config()

    # 询问清除数据
    print("\n提醒：第一次使用请清除所有数据")
    clear_choice = input("是否清除所有数据？[Y/n] (默认: n): ").strip().lower()
    if clear_choice == 'y':
        clear_all_data()
        config = load_config()
    else:
        print("跳过数据清除，保留原有配置")

    # 输入配置
    page_name = input(f"\n请输入网页名(默认: {config['html_title']}): ").strip()
    if page_name:
        config['html_title'] = page_name

    page_title = input(f"请输入页面大标题(默认: {config['page_title']}): ").strip()
    if page_title:
        config['page_title'] = page_title

    # 【新增】自定义字体（在标题与字号之间，完全按你要求）
    print("\n是否自定义字体文件（ttf）")
    font_choice = input("自定义字体 [Y/n] (默认: n): ").strip().lower()
    if font_choice == "y":
        font_path = select_file("TTF字体文件", (".ttf",))
        config["custom_font"] = font_path
    else:
        config["custom_font"] = None

    print(f"\n标题字体大小默认值：{config['title_font_size']}磅")
    title_font = input("请输入标题字体大小（不输入用默认）: ").strip()
    if title_font and title_font.isdigit():
        config['title_font_size'] = int(title_font)

    print(f"\n文本字体大小默认值：{config['text_font_size']}磅")
    text_font = input("请输入文本字体大小（不输入用默认）: ").strip()
    if text_font and text_font.isdigit():
        config['text_font_size'] = int(text_font)

    # 清空内容文件
    with open("content.html", "w", encoding="utf-8") as f:
        f.write("")

    save_config(config)
    print(f"\n配置完成：网页名={config['html_title']}，标题={config['page_title']}")

if __name__ == "__main__":
    main()
