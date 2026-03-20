#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import shutil
import base64

# 跨平台兼容：固定工作目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
PYTHON_EXEC = sys.executable

# 系统检测函数
def is_windows():
    return sys.platform == "win32"
def is_macos():
    return sys.platform == "darwin"
def is_linux():
    return sys.platform == "linux"
def is_termux():
    return is_linux() and (os.environ.get("ANDROID_ROOT") is not None or "android" in open("/proc/version", "r").read().lower())

# 追加内容到网页
def append_to_content(html_content):
    with open("content.html", "a", encoding="utf-8") as f:
        f.write(f"\n{html_content}")

# 优先级1：tkinter文件选择对话框
def select_file_with_tkinter(file_type="image"):
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        # 设置文件类型过滤
        if file_type == "image":
            file_types = [
                ("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("所有文件", "*.*")
            ]
            title = "选择要添加的图片文件"
        elif file_type == "video":
            file_types = [
                ("视频文件", "*.mp4 *.webm *.ogg *.mov"),
                ("所有文件", "*.*")
            ]
            title = "选择要添加的视频文件"
        else:
            file_types = [("所有文件", "*.*")]
            title = "选择文件"
        
        file_path = filedialog.askopenfilename(title=title, filetypes=file_types)
        root.destroy()
        if file_path and os.path.exists(file_path):
            return file_path
        return None
    except Exception as e:
        print(f"文件选择器不可用：{str(e)}")
        return None

# 优先级2：调起系统文件管理器
def open_file_manager():
    try:
        assets_dir = os.path.join(SCRIPT_DIR, "assets")
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)
        
        if is_windows():
            subprocess.run(["explorer.exe", assets_dir], check=False)
        elif is_macos():
            subprocess.run(["open", assets_dir], check=False)
        elif is_termux():
            subprocess.run(["termux-open", assets_dir], check=False)
        elif is_linux():
            subprocess.run(["xdg-open", assets_dir], check=False)
        else:
            return False
        print(f"已调起文件管理器，请将文件复制到assets目录中")
        return True
    except Exception as e:
        print(f"调起文件管理器失败：{str(e)}")
        return False

# 优先级3：手动输入文件路径
def manual_input_path(file_type="image"):
    print(f"\n请手动输入{file_type}文件的绝对路径:")
    while True:
        file_path = input("文件路径: ").strip()
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return file_path
        else:
            print("文件不存在或不是有效文件，请重新输入")

# 统一获取文件路径
# 统一获取文件路径
def get_file_path(file_type="image"):
    print(f"\n正在尝试打开文件选择对话框...")
    file_path = select_file_with_tkinter(file_type)
    if file_path:
        print(f"已选择文件：{file_path}")
        return file_path
    
    # ================== 新增：tk不可用时，从assets按类型选择 ==================
    print("\ntkinter不可用，将从 assets 目录选择文件...")
    assets_dir = os.path.join(SCRIPT_DIR, "assets")
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)

    # 按类型筛选后缀
    if file_type == "image":
        exts = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
        desc = "图片"
    elif file_type == "video":
        exts = [".mp4", ".webm", ".ogg", ".mov"]
        desc = "视频"
    else:
        exts = []
        desc = "文件"

    # 只扫 assets
    files = []
    for f in os.listdir(assets_dir):
        fp = os.path.join(assets_dir, f)
        if os.path.isfile(fp) and os.path.splitext(f)[1].lower() in exts:
            files.append(fp)

    if files:
        print(f"\nassets 中的 {desc} 文件：")
        for i, p in enumerate(files):
            print(f"{i+1}. {os.path.basename(p)}")
        while True:
            try:
                c = input(f"请选择 {desc}（数字）：").strip()
                if not c:
                    break
                idx = int(c)-1
                if 0 <= idx < len(files):
                    return files[idx]
            except ValueError:
                print("输入无效")
    # ========================================================================

    print("\n正在尝试调起系统文件管理器...")
    fm_success = open_file_manager()
    if fm_success:
        file_name = input("请输入复制到assets目录中的文件名（带后缀）: ").strip()
        if file_name:
            file_path = os.path.join(SCRIPT_DIR, "assets", file_name)
            if os.path.exists(file_path):
                return file_path
            else:
                print(f"错误：assets目录中找不到文件 {file_name}")
    
    return manual_input_path(file_type)

# 图片转base64
def image_to_base64(image_path):
    # 自动识别图片格式
    ext = os.path.splitext(image_path)[1].lower()
    if ext in ['.jpg', '.jpeg']:
        mime_type = 'image/jpeg'
    elif ext == '.png':
        mime_type = 'image/png'
    elif ext == '.gif':
        mime_type = 'image/gif'
    elif ext == '.webp':
        mime_type = 'image/webp'
    elif ext == '.bmp':
        mime_type = 'image/bmp'
    else:
        mime_type = 'image/jpeg'
    
    with open(image_path, "rb") as f:
        base64_data = base64.b64encode(f.read()).decode('utf-8').replace('\n', '')
    
    return f'data:{mime_type};base64,{base64_data}'

def main():
    print("=== 添加资源文件 ===")
    # 确保assets目录存在
    if not os.path.exists("assets"):
        os.makedirs("assets")

    while True:
        # 选择资源类型
        print("\n请选择要添加的资源类型：")
        print("1、图片（自动转base64嵌入）")
        print("2、视频（HTML播放器，默认不播放）")
        print("3、超链接")
        type_choice = input("[1/2/3]: ").strip()

        if type_choice == '1':
            # 图片处理
            file_path = get_file_path("image")
            print("\n加载中，请勿操作...")
            try:
                base64_src = image_to_base64(file_path)
                html_img = f'<div class="resource-box"><img src="{base64_src}" alt="{os.path.basename(file_path)}"></div>'
                append_to_content(html_img)
                print("图片已添加到页面，base64嵌入完成")
            except Exception as e:
                print(f"图片处理失败：{str(e)}")

        elif type_choice == '2':
            # 视频处理
            file_path = get_file_path("video")
            try:
                # 复制视频到assets目录
                file_name = os.path.basename(file_path)
                target_path = os.path.join("assets", file_name)
                if not os.path.samefile(file_path, target_path):
                    shutil.copy2(file_path, target_path)
                # 生成video标签，默认不播放
                html_video = f'<div class="resource-box"><video controls preload="none" src="assets/{file_name}"></video></div>'
                append_to_content(html_video)
                print("视频已添加到页面，默认不自动播放")
            except Exception as e:
                print(f"视频处理失败：{str(e)}")

        elif type_choice == '3':
            # 链接处理
            print("\n请输入链接，格式为：链接名 链接地址")
            print("示例：百度 https://www.baidu.com")
            link_input = input("链接: ").strip()
            if ' ' in link_input:
                link_name, link_url = link_input.split(' ', 1)
                html_link = f'<p><a href="{link_url}" target="_blank" class="link-btn">{link_name}</a></p>'
                append_to_content(html_link)
                print("链接已添加到页面")
            else:
                print("输入格式错误，请按照「链接名 链接地址」格式输入")

        else:
            print("无效选择，请重新输入")
            continue

        # 末尾判定，严格按照要求优化
        print("\n请选择接下来操作:")
        print("1、继续添加文本")
        print("2、继续添加资源")
        print("n、不添加，进入启动步骤")
        choice = input("[1/2/n] (默认: n): ").strip().lower()

        if choice == '1':
            # 跳转到text.py
            print("跳转到文本添加页面...")
            subprocess.run([PYTHON_EXEC, "text.py"], cwd=SCRIPT_DIR)
            sys.exit(0)
        elif choice == '2':
            # 回到资源添加步骤，继续循环
            continue
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
