#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import json
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime

# 跨平台兼容：固定工作目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
if not os.path.exists("log"):
    os.makedirs("log")

# 加载配置
def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        config["port"] = int(config.get("port", 5000))
        return config
    except FileNotFoundError:
        print("错误：找不到config.json配置文件，请先运行renew.py初始化")
        sys.exit(1)
    except json.JSONDecodeError:
        print("错误：config.json格式损坏，请重新运行renew.py")
        sys.exit(1)
    except (ValueError, TypeError):
        print("错误：config.json中port必须是数字，请检查配置")
        sys.exit(1)

# 加载网页内容
def load_content():
    try:
        with open("content.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# 生成HTML（和参考文件样式完全一致）
def generate_full_html(config, content):
    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem 0;
        }}
        @keyframes welcome {{
            from {{ opacity: 0; transform: translateY(-50px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .welcome-title {{
            font-size: {title_font_size};
            color: #1e293b;
            text-align: center;
            margin-bottom: 2rem;
            animation: welcome 1s ease-out;
            line-height: 1.2;
        }}
        .content-block, .resource-box {{
            width: 90%;
            max-width: 800px;
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .content-block:hover, .resource-box:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        }}
        p {{
            font-size: {text_font_size};
            line-height: 1.8;
            color: #334155;
            word-break: break-word;
        }}
        .resource-box img, .resource-box video {{
            width: 100%;
            height: auto;
            display: block;
            border-radius: 8px;
        }}
        video {{ preload: none; muted: true; controls: true; }}
        a {{ color: #2563eb; text-decoration: none; font-weight: 500; }}
        a:hover {{ color: #1d4ed8; text-decoration: underline; }}
        .link-btn {{
            display: inline-block;
            padding: 6px 16px;
            background: #2563eb;
            color: white !important;
            border-radius: 6px;
            margin: 0.5rem 0;
        }}
        .link-btn:hover {{ background: #1d4ed8; text-decoration: none; }}
    </style>
</head>
<body>
    <h1 class="welcome-title">{page_title}</h1>
    {content}
</body>
</html>"""
    return html_template.format(
        page_name=config.get('html_title', config.get('page_name', '我的分享页面')),
        page_title=config.get('page_title', '欢迎来到我的页面'),
        title_font_size=f"{config.get('title_font_size', 36)}pt",
        text_font_size=f"{config.get('text_font_size', 16)}pt",
        content=content
    )

# 自定义处理器
class StaticHTMLHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, html_content=None, **kwargs):
        self.html_content = html_content
        super().__init__(*args, **kwargs)
    def do_GET(self):
        if self.path in ['/', '/index.html']:
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.html_content.encode('utf-8'))
        else:
            super().do_GET()
    def log_message(self, format, *args):
        return

# 查找可用端口
def find_free_port(start_port, max_port=65535):
    for port in range(start_port, max_port + 1):
        try:
            with HTTPServer(("", port), StaticHTMLHandler):
                return port
        except OSError:
            continue
    print(f"错误：{start_port}-{max_port}无可用端口")
    sys.exit(1)

def main():
    print("=== 生成完成，启动本地服务 ===")
    config = load_config()
    content = load_content()
    full_html = generate_full_html(config, content)

    # 保存日志
    log_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = os.path.join("log", f"log_{log_time}.html")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"网页已保存到日志文件：{log_file}")

    # 启动服务
    start_port = start_port = config['port']
    port = find_free_port(start_port)
    server_url = f"http://127.0.0.1:{port}"
    server_address = ("", port)
    handler = lambda *args, **kwargs: StaticHTMLHandler(*args, html_content=full_html, **kwargs)
    httpd = HTTPServer(server_address, handler)

    print(f"\n已运行!请在浏览器访问 {server_url} 进行查看。")
    print("按 Ctrl+C 停止服务")
    # 调起浏览器
    try:
        webbrowser.open(server_url)
        print("已尝试调起浏览器访问页面\n")
    except Exception as e:
        print(f"调起浏览器失败：{str(e)}\n")
    # 运行服务：无额外捕获，交给startup.py统一处理
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()  
        sys.exit(0)  


if __name__ == "__main__":
    main()
