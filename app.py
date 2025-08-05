from flask import Flask, Response, send_file, make_response, request, abort
from game import Game
from renderer import render_game
from io import BytesIO

app = Flask(__name__)

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

    # 1. 创建一个新的游戏实例
    current_game = Game()

    # 2. 根据指令运行游戏模拟
    # 只允许使用合法的操作字符
    allowed_chars = "lrus" # 'd' 已被移除
    filtered_actions = "".join(filter(lambda char: char in allowed_chars, actions))
    current_game.run_actions(filtered_actions)

    # 3. 渲染游戏状态为WEBP图像
    img_data = render_game(current_game)

    # 4. 创建并返回HTTP响应
    # 我们需要设置正确的MIME类型，并禁用缓存，以确保Discord每次都请求新的图片
    response = make_response(img_data)
    response.headers.set('Content-Type', 'image/webp')
    response.headers.set('Cache-Control', 'no-cache, no-store, must-revalidate')
    response.headers.set('Pragma', 'no-cache')
    response.headers.set('Expires', '0')
    
    return response

if __name__ == '__main__':
    # 在本地运行服务器以进行测试
    # host='0.0.0.0' 使其可以被局域网内的其他设备访问
    app.run(debug=True, host='0.0.0.0', port=5000)
