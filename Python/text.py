#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import re
import subprocess

# 跨平台兼容：固定工作目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
PYTHON_EXEC = sys.executable

# 链接处理正则
# 匹配「链接名 链接地址」格式
LINK_NAME_PATTERN = re.compile(r'(\S+)\s+(https?://\S+)')
# 匹配纯链接地址，避免已替换的链接重复匹配
PURE_LINK_PATTERN = re.compile(r'(?<!href=")(https?://\S+)')

# 处理文本中的链接
def process_text_links(text):
    # 先处理带名称的链接
    processed = LINK_NAME_PATTERN.sub(r'<a href="\2" target="_blank">\1</a>', text)
    # 再处理纯链接
    processed = PURE_LINK_PATTERN.sub(r'<a href="\1" target="_blank">\1</a>', processed)
    return processed

# 追加内容到网页
def append_to_content(html_content):
    with open("content.html", "a", encoding="utf-8") as f:
        f.write(f"\n{html_content}")

def main():
    print("=== 添加文本内容 ===")

    while True:
        # 支持空输入，空输入直接跳转到末尾判定
        text_input = input("\n请输入要添加的文本内容（直接回车跳过）: ").strip()
        
        if text_input:
            # 处理链接，生成HTML
            processed_text = process_text_links(text_input)
            html_p = f'<p>{processed_text}</p>'
            append_to_content(html_p)
            print("文本内容已添加到页面，链接已自动转换为可点击格式")
        else:
            print("输入为空，跳过本次文本添加")

        # 末尾判定，严格按照要求
        print("\n请选择接下来操作:")
        print("1、继续添加文本")
        print("2、继续添加资源")
        print("n、不添加，进入启动步骤")
        choice = input("[1/2/n] (默认: n): ").strip().lower()

        if choice == '1':
            # 回到输入文本部分，继续循环
            continue
        elif choice == '2':
            # 跳转到resources.py
            print("跳转到资源添加页面...")
            subprocess.run([PYTHON_EXEC, "resources.py"], cwd=SCRIPT_DIR)
            sys.exit(0)
        elif choice == '' or choice == 'n':
            # 跳转到main.py
            print("跳过添加操作，进入启动步骤...")
            subprocess.run([PYTHON_EXEC, "main.py"], cwd=SCRIPT_DIR)
            sys.exit(0)
        else:
            print("无效输入，使用默认选项n，进入启动步骤")
            subprocess.run([PYTHON_EXEC, "main.py"], cwd=SCRIPT_DIR)
            sys.exit(0)

if __name__ == "__main__":
    main()