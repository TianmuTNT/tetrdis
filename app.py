from flask import Flask, Response, send_file, make_response, request, abort
from game import Game
from renderer import render_game
from io import BytesIO
import os
import threading

app = Flask(__name__)

# --- 缓存和并发控制 ---
# 使用一个锁来防止并发请求同时计算和写入文件
request_lock = threading.Lock()
CACHE_FILE = "cache.webp"
CACHE_INFO_FILE = "cache.txt"

@app.route('/')
def index():
    """
    提供一个简单的欢迎页面，并给出开始游戏的URL。
    """
    start_url = "/i.webp"
    html = f"""
    <h1>Discord Tetris</h1>
    <p>To start a new game, use this URL in Discord:</p>
    <p><code>YOUR_PUBLIC_URL{start_url}</code></p>
    <p>Then, use Discord's s/search/replace feature to add commands.</p>
    <p>Example: <code>s/i/li</code> to move left.</p>
    <p>Example: <code>s/i/ri</code> to move right.</p>
    <p>Example: <code>s/li/lri</code> to move left then right.</p>
    """
    return html

# 路由现在匹配 "actions" + "i.webp"，并为初始状态 /i.webp 提供默认值
@app.route('/i.webp', defaults={'actions': ''})
@app.route('/<string:actions>i.webp')
def play(actions):
    """
    核心游戏路由。
    根据URL中的actions字符串生成游戏状态并渲染为WEBP图像。
    """
    # 校验 User-Agent，只允许 Discord 机器人访问
    user_agent = request.headers.get('User-Agent')
    expected_user_agent = "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)"
    if user_agent != expected_user_agent:
        abort(403) # Forbidden

    with request_lock:
        # --- 缓存逻辑 ---
        # 1. 检查当前缓存是否为我们需要的
        cached_actions = None
        if os.path.exists(CACHE_INFO_FILE):
            with open(CACHE_INFO_FILE, "r") as f:
                cached_actions = f.read()
        
        # 2. 如果缓存有效，直接返回缓存文件
        if cached_actions == actions and os.path.exists(CACHE_FILE):
            print(f"Cache hit for actions: '{actions}'")
            return send_file(CACHE_FILE, mimetype='image/webp')

        # --- 如果缓存无效，则重新生成 ---
        print(f"Cache miss for actions: '{actions}'. Generating new image.")
        # 1. 创建一个新的游戏实例
        current_game = Game()

        # 2. 根据指令运行游戏模拟
        allowed_chars = "lrus"
        filtered_actions = "".join(filter(lambda char: char in allowed_chars, actions))
        current_game.run_actions(filtered_actions)

        # 3. 渲染游戏状态为WEBP图像
        img_data = render_game(current_game)

        # 4. 更新缓存文件和信息文件
        with open(CACHE_FILE, "wb") as f:
            f.write(img_data)
        with open(CACHE_INFO_FILE, "w") as f:
            f.write(actions)
        
        # 5. 直接从刚写入的缓存文件中读取并返回，确保一致性
        return send_file(CACHE_FILE, mimetype='image/webp')

if __name__ == '__main__':
    # 在本地运行服务器以进行测试
    # host='0.0.0.0' 使其可以被局域网内的其他设备访问
    app.run(debug=True, host='0.0.0.0', port=5000)
