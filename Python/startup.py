#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import json
import signal  # 新增：信号处理

# 跨平台兼容：固定工作目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
PYTHON_EXEC = sys.executable

# 新增：全局屏蔽子进程的Ctrl+C信号（适配Linux/Termux/Windows）
def ignore_child_signals():
    if sys.platform != "win32":
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    else:
        signal.signal(signal.SIGBREAK, signal.SIG_IGN)

# 初始化环境（键名已统一为html_title，解决之前KeyError）
def init_environment():
    default_config = {
        "host": "127.0.0.1",
        "port": 5000,
        "html_title": "我的网页",
        "page_title": "欢迎来到我的页面",
        "title_font_size": "32pt",
        "text_font_size": "14pt"
    }
    if not os.path.exists("config.json"):
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
    if not os.path.exists("content.html"):
        with open("content.html", "w", encoding="utf-8") as f:
            f.write("")
    if not os.path.exists("log"):
        os.makedirs("log")

def run_script(script_name):
    print(f"\n=== 正在运行 {script_name} ===")
    try:
        # 运行前屏蔽子进程信号，移除无效的creationflags
        result = subprocess.run(
            [PYTHON_EXEC, script_name],
            check=True,
            cwd=SCRIPT_DIR,
            encoding='utf-8',
            preexec_fn=ignore_child_signals if sys.platform != "win32" else None
        )
        print(f"=== {script_name} 运行完成 ===")
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误：{script_name} 运行失败，返回码：{e.returncode}")
        return False
    except FileNotFoundError:
        print(f"错误：找不到 {script_name} 文件，请确认文件在当前目录")
        return False
    except Exception as e:
        print(f"错误：运行 {script_name} 时发生异常：{str(e)}")
        return False

def main():
    print("=== HTML生成工具启动 ===")
    init_environment()
    script_order = ["renew.py", "apichanger.py", "text.py", "resources.py"]
    for script in script_order:
        if not run_script(script):
            print(f"流程终止于 {script}")
            return
    run_script("main.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已终止")  # 仅1行提示，无回溯
    except Exception as e:
        print(f"\n程序发生异常：{str(e)}")
    finally:
        input("\n按回车键退出...")
