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

if not os.path.exists("logs"):
    os.makedirs("logs")

# 加载配置
def load_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("错误：找不到config.json配置文件，请先运行renew.py初始化")
        sys.exit(1)
    except json.JSONDecodeError:
        print("错误：config.json格式损坏，请重新运行renew.py")
        sys.exit(1)

# 加载网页内容
def load_content():
    try:
        with open("content.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

# 生成HTML（调用外部config.css + 动态字体）
def generate_full_html(config, content):
    custom_font = config.get("custom_font")
    font_style = ""
    if custom_font and os.path.isfile(custom_font):
        font_style = f'''
<style>
@font-face {{
    font-family: 'CustomFont';
    src: url('{custom_font}') format('truetype');
}}
* {{
    font-family: 'CustomFont', sans-serif !important;
}}
</style>
'''

    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_name}</title>
    <link rel="stylesheet" href="config.css">
    {font_style}
</head>
<body>
    <h1 class="welcome-title">{page_title}</h1>
    {content}
</body>
</html>"""
    return html_template.format(
        page_name=config.get('html_title', config.get('page_name', '我的分享页面')),
        page_title=config.get('page_title', '欢迎来到我的页面'),
        font_style=font_style,
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
    logs_file = os.path.join("logs", f"log_{log_time}.html")
    with open(logs_file, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"网页已保存到日志文件：{logs_file}")

    # 启动服务
    start_port = config.get('server_port', config.get('port', 5000))
    port = find_free_port(start_port)
    server_url = f"http://127.0.0.1:{port}"
    server_address = ("", port)
    handler = lambda *args, **kwargs: StaticHTMLHandler(*args, html_content=full_html, **kwargs)
    httpd = HTTPServer(server_address, handler)

    print(f"\n已运行!请在浏览器访问 {server_url} 进行查看。")
    print("按 Ctrl+C 停止服务")

    # 调起浏览器（Termux自动支持）
    try:
        if os.path.exists('/data/data/com.termux/files/usr/bin/termux-open'):
            os.system(f'termux-open {server_url}')
        else:
            webbrowser.open(server_url)
    except Exception as e:
        print(f"调起浏览器失败：{str(e)}\n")

    # 运行服务
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        sys.exit(0)

if __name__ == "__main__":
    main()
