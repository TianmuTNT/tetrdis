from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import game

# --- 可配置的样式 ---

# 颜色 (R, G, B)
COLORS = [
    (20, 20, 20),      # 0: 背景色
    (0, 240, 240),      # 1: I (青色)
    (240, 240, 0),      # 2: O (黄色)
    (160, 0, 240),      # 3: T (紫色)
    (0, 0, 240),        # 4: L (蓝色) - 注意：原版L是橙色，J是蓝色，这里做了调整
    (240, 160, 0),      # 5: J (橙色)
    (0, 240, 0),        # 6: S (绿色)
    (240, 0, 0),        # 7: Z (红色)
]
GRID_COLOR = (60, 60, 60)
TEXT_COLOR = (255, 255, 255)
GAME_OVER_BG_COLOR = (0, 0, 0, 180) # 半透明黑色背景

# 尺寸
BLOCK_SIZE = 30  # 每个方块的像素大小
GRID_LINE_WIDTH = 1
INFO_PANEL_WIDTH = BLOCK_SIZE * 5 # 右侧信息面板宽度

# 计算图像总尺寸
IMG_WIDTH = game.GRID_WIDTH * BLOCK_SIZE + INFO_PANEL_WIDTH
IMG_HEIGHT = game.GRID_HEIGHT * BLOCK_SIZE

# 字体 (如果找不到默认字体，可能需要指定字体文件路径)
try:
    FONT_LARGE = ImageFont.truetype("arial.ttf", 36)  # 增大
    FONT_MEDIUM = ImageFont.truetype("arial.ttf", 28) # 增大
    FONT_SMALL = ImageFont.truetype("arial.ttf", 22)  # 增大
except IOError:
    # 如果找不到字体文件，默认字体大小可能无法调整，但我们尽力而为
    FONT_LARGE = ImageFont.load_default(size=36)
    FONT_MEDIUM = ImageFont.load_default(size=28)
    FONT_SMALL = ImageFont.load_default(size=22)

def draw_block(draw, x, y, color_index):
    """在指定坐标绘制一个方块"""
    top_left_x = x * BLOCK_SIZE
    top_left_y = y * BLOCK_SIZE
    bottom_right_x = top_left_x + BLOCK_SIZE
    bottom_right_y = top_left_y + BLOCK_SIZE
    
    draw.rectangle(
        (top_left_x, top_left_y, bottom_right_x, bottom_right_y),
        fill=COLORS[color_index],
        outline=GRID_COLOR,
        width=GRID_LINE_WIDTH
    )

def render_game(game_instance):
    """将整个游戏状态渲染成一张WEBP图片"""
    # 1. 创建画布
    image = Image.new("RGB", (IMG_WIDTH, IMG_HEIGHT), COLORS[0])
    draw = ImageDraw.Draw(image, "RGBA")

    # 2. 绘制已固定的方块
    for y, row in enumerate(game_instance.grid):
        for x, cell_value in enumerate(row):
            if cell_value != 0:
                draw_block(draw, x, y, cell_value)
            else: # 绘制网格线
                 draw_block(draw, x, y, 0)


    # 3. 绘制当前下落的方块
    if not game_instance.game_over and game_instance.current_piece:
        piece_color_index = game_instance.current_piece_shape_index + 1
        for r, row in enumerate(game_instance.current_piece):
            for c, cell in enumerate(row):
                if cell:
                    draw_block(
                        draw,
                        game_instance.current_piece_x + c,
                        game_instance.current_piece_y + r,
                        piece_color_index
                    )

    # 4. 绘制信息面板
    info_x_start = game.GRID_WIDTH * BLOCK_SIZE + 20
    draw.text((info_x_start, 30), "SCORE", font=FONT_LARGE, fill=TEXT_COLOR)
    draw.text((info_x_start, 60), str(game_instance.score), font=FONT_LARGE, fill=TEXT_COLOR)
    
    draw.text((info_x_start, 150), "HOW TO PLAY", font=FONT_MEDIUM, fill=TEXT_COLOR)
    controls_text = (
        "Use s/find/replace\n\n"
        "s/i/li  (left)\n"
        "s/i/ri  (right)\n"
        "s/i/ui  (rotate)\n"
        "s/i/si  (drop)\n\n"
        "Example:\n"
        "s/li/lri"
    )
    draw.text((info_x_start, 180), controls_text, font=FONT_SMALL, fill=TEXT_COLOR, spacing=4)


    # 5. 如果游戏结束，显示覆盖层
    if game_instance.game_over:
        overlay = Image.new("RGBA", image.size, GAME_OVER_BG_COLOR)
        overlay_draw = ImageDraw.Draw(overlay)
        
        text = "GAME OVER"
        text_bbox = overlay_draw.textbbox((0, 0), text, font=FONT_LARGE)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = (IMG_WIDTH - text_width) / 2
        text_y = (IMG_HEIGHT - text_height) / 2
        
        overlay_draw.text((text_x, text_y), text, font=FONT_LARGE, fill=TEXT_COLOR)
        image.paste(overlay, (0, 0), overlay)

    # 6. 将图像保存到内存中的字节流
    img_buffer = BytesIO()
    image.save(img_buffer, format='WEBP', quality=85)
    img_buffer.seek(0)
    
    return img_buffer.getvalue()

if __name__ == '__main__':
    # 用于本地测试渲染器
    test_game = game.Game()
    test_game.run_actions("rrdlsuudls") # 模拟一些操作
    
    img_data = render_game(test_game)
    with open("test_render.webp", "wb") as f:
        f.write(img_data)
    print("Test render saved to test_render.webp")

    test_game_over = game.Game()
    test_game_over.game_over = True
    img_data_over = render_game(test_game_over)
    with open("test_render_over.webp", "wb") as f:
        f.write(img_data_over)
    print("Test game over render saved to test_render_over.webp")
