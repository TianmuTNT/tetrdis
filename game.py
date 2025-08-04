import copy

# 游戏区域尺寸
GRID_WIDTH = 10
GRID_HEIGHT = 20

# 方块形状 (Tetrominoes)
# 每个形状都是一个包含多个旋转状态的列表
# 每个旋转状态是一个2D列表，表示方块的形状
SHAPES = [
    # I
    [[[1, 1, 1, 1]], [[1], [1], [1], [1]]],
    # O
    [[[2, 2], [2, 2]]],
    # T
    [[[0, 3, 0], [3, 3, 3]], [[3, 0], [3, 3], [3, 0]], [[3, 3, 3], [0, 3, 0]], [[0, 3], [3, 3], [0, 3]]],
    # L
    [[[0, 0, 4], [4, 4, 4]], [[4, 0], [4, 0], [4, 4]], [[4, 4, 4], [4, 0, 0]], [[4, 4], [0, 4], [0, 4]]],
    # J
    [[[5, 0, 0], [5, 5, 5]], [[5, 5], [5, 0], [5, 0]], [[5, 5, 5], [0, 0, 5]], [[0, 5], [0, 5], [5, 5]]],
    # S
    [[[0, 6, 6], [6, 6, 0]], [[6, 0], [6, 6], [0, 6]]],
    # Z
    [[[7, 7, 0], [0, 7, 7]], [[0, 7], [7, 7], [7, 0]]]
]

# 固定的方块出现顺序 (保证游戏可重复)
# 使用数字索引对应 SHAPES 列表
PIECE_SEQUENCE = [0, 1, 2, 3, 4, 5, 6] * 100 # 重复多次以支持长时游戏

class Game:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.piece_index = 0
        self.score = 0
        self.game_over = False
        self.spawn_new_piece()

    def spawn_new_piece(self):
        if self.piece_index >= len(PIECE_SEQUENCE):
            self.game_over = True
            return

        self.current_piece_shape_index = PIECE_SEQUENCE[self.piece_index]
        self.current_piece_rotation = 0
        self.current_piece = SHAPES[self.current_piece_shape_index][self.current_piece_rotation]
        self.current_piece_x = GRID_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.current_piece_y = 0
        self.piece_index += 1

        if self.check_collision(self.current_piece, self.current_piece_x, self.current_piece_y):
            self.game_over = True

    def check_collision(self, piece, x, y):
        for r, row in enumerate(piece):
            for c, cell in enumerate(row):
                if cell:
                    grid_x, grid_y = x + c, y + r
                    if not (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT and self.grid[grid_y][grid_x] == 0):
                        return True
        return False

    def lock_piece(self):
        for r, row in enumerate(self.current_piece):
            for c, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece_y + r][self.current_piece_x + c] = self.current_piece_shape_index + 1
        self.clear_lines()
        self.spawn_new_piece()

    def clear_lines(self):
        lines_cleared = 0
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        lines_cleared = GRID_HEIGHT - len(new_grid)
        
        if lines_cleared > 0:
            self.score += [0, 100, 300, 500, 800][lines_cleared]
            for _ in range(lines_cleared):
                new_grid.insert(0, [0 for _ in range(GRID_WIDTH)])
            self.grid = new_grid

    def move(self, dx, dy):
        if not self.game_over and not self.check_collision(self.current_piece, self.current_piece_x + dx, self.current_piece_y + dy):
            self.current_piece_x += dx
            self.current_piece_y += dy
            return True
        return False

    def rotate(self):
        if self.game_over:
            return
        
        original_rotation = self.current_piece_rotation
        self.current_piece_rotation = (self.current_piece_rotation + 1) % len(SHAPES[self.current_piece_shape_index])
        rotated_piece = SHAPES[self.current_piece_shape_index][self.current_piece_rotation]

        if not self.check_collision(rotated_piece, self.current_piece_x, self.current_piece_y):
            self.current_piece = rotated_piece
        else:
            # 尝试"踢墙"
            for kick_x in [-1, 1, -2, 2]:
                if not self.check_collision(rotated_piece, self.current_piece_x + kick_x, self.current_piece_y):
                    self.current_piece_x += kick_x
                    self.current_piece = rotated_piece
                    return
            self.current_piece_rotation = original_rotation # 旋转失败，恢复原状

    def hard_drop(self):
        if self.game_over:
            return
        while self.move(0, 1):
            pass
        self.lock_piece()

    def step(self):
        if not self.move(0, 1):
            self.lock_piece()

    def run_actions(self, actions_string):
        """根据指令字符串模拟游戏"""
        if self.game_over:
            return

        for action in actions_string:
            if self.game_over:
                break

            if action == 'l':  # left
                self.move(-1, 0)
                self.step()  # 操作后自动下落
            elif action == 'r':  # right
                self.move(1, 0)
                self.step()  # 操作后自动下落
            elif action == 'u':  # up (rotate)
                self.rotate()
                self.step()  # 操作后自动下落
            elif action == 's':  # space (hard drop)
                self.hard_drop()
            else:
                # 对于无法识别的字符，也视为游戏时间流逝，下落一格
                self.step()
