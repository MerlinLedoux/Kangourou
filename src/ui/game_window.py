import arcade

from ..game import Game
from ..pieces import PIECE_COLORS, PIECE_ORIENTATIONS

# ---------------------------------------------------------------------------
# Constantes de mise en page
# ---------------------------------------------------------------------------
WINDOW_WIDTH  = 1200
WINDOW_HEIGHT = 780
WINDOW_TITLE  = "Pentaminos"

CELL_SIZE   = 60
BOARD_ROWS  = 6
BOARD_COLS  = 10

BOARD_LEFT   = 40
BOARD_BOTTOM = 190

SIDEBAR_X     = BOARD_LEFT + BOARD_COLS * CELL_SIZE + 55
SIDEBAR_WIDTH = WINDOW_WIDTH - SIDEBAR_X - 15

PREVIEW_CELL  = 18
PREVIEW_COLS  = 3
PREVIEW_BOX_W = SIDEBAR_WIDTH // PREVIEW_COLS
PREVIEW_BOX_H = 140

COLOR_BG         = (28,  30,  42)
COLOR_BOARD_BG   = (44,  47,  64)
COLOR_GRID       = (68,  72,  100)
COLOR_SIDEBAR_BG = (36,  38,  52)
COLOR_TEXT       = (210, 212, 225)
COLOR_TEXT_DIM   = (140, 143, 165)


# ---------------------------------------------------------------------------
# Helpers : wrappers autour de la nouvelle API Arcade 3.x
# Les fonctions Arcade 3.x prennent (left, bottom, width, height)
# alors que l'ancienne API prenait (center_x, center_y, width, height).
# ---------------------------------------------------------------------------

def _fill(cx, cy, w, h, color):
    """Rectangle plein, centre sur (cx, cy)."""
    arcade.draw_lbwh_rectangle_filled(cx - w / 2, cy - h / 2, w, h, color)


def _outline(cx, cy, w, h, color, border_width=1):
    """Rectangle vide (contour), centre sur (cx, cy)."""
    arcade.draw_lbwh_rectangle_outline(cx - w / 2, cy - h / 2, w, h, color, border_width)


class GameWindow(arcade.Window):

    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, resizable=False)
        self.background_color = COLOR_BG

        self.game = Game(BOARD_ROWS, BOARD_COLS)

        self.dragging: str | None = None
        self.drag_x = 0
        self.drag_y = 0
        self.ghost_row: int | None = None
        self.ghost_col: int | None = None

        self._sidebar_pos: dict = self._compute_sidebar_positions()
        self.won = False

    # ------------------------------------------------------------------
    # Mise en page
    # ------------------------------------------------------------------

    def _compute_sidebar_positions(self) -> dict:
        names = sorted(PIECE_COLORS.keys())
        start_y = WINDOW_HEIGHT - 80
        positions = {}
        for i, name in enumerate(names):
            col_idx = i % PREVIEW_COLS
            row_idx = i // PREVIEW_COLS
            cx = SIDEBAR_X + col_idx * PREVIEW_BOX_W + PREVIEW_BOX_W // 2
            cy = start_y - row_idx * PREVIEW_BOX_H
            positions[name] = (cx, cy)
        return positions

    # ------------------------------------------------------------------
    # Conversions coordonnees
    # ------------------------------------------------------------------

    def _board_to_screen(self, row: int, col: int) -> tuple:
        x = BOARD_LEFT + col * CELL_SIZE + CELL_SIZE / 2
        y = BOARD_BOTTOM + (BOARD_ROWS - 1 - row) * CELL_SIZE + CELL_SIZE / 2
        return x, y

    def _screen_to_board(self, x: float, y: float) -> tuple:
        col = int((x - BOARD_LEFT) / CELL_SIZE)
        row = BOARD_ROWS - 1 - int((y - BOARD_BOTTOM) / CELL_SIZE)
        return row, col

    def _is_over_board(self, x: float, y: float) -> bool:
        return (BOARD_LEFT <= x < BOARD_LEFT + BOARD_COLS * CELL_SIZE and
                BOARD_BOTTOM <= y < BOARD_BOTTOM + BOARD_ROWS * CELL_SIZE)

    # ------------------------------------------------------------------
    # Primitives de dessin
    # ------------------------------------------------------------------

    def _draw_cell(self, cx: float, cy: float, color: tuple, size: int = CELL_SIZE):
        margin = 2
        s = size - margin
        _fill(cx, cy, s, s, color)
        _outline(cx, cy, s, s, (0, 0, 0, 70))

    def _draw_piece_on_board(self, cells, anchor_row: int, anchor_col: int,
                             color: tuple, alpha: int = 255):
        r, g, b = color[:3]
        c = (r, g, b, alpha)
        for dr, dc in cells:
            cx, cy = self._board_to_screen(anchor_row + dr, anchor_col + dc)
            self._draw_cell(cx, cy, c)

    def _draw_piece_preview(self, cells, center_x: float, center_y: float,
                            color: tuple, cell_size: int = PREVIEW_CELL, alpha: int = 255):
        if not cells:
            return
        rows = [r for r, c in cells]
        cols = [c for r, c in cells]
        cr = (max(rows) + min(rows)) / 2
        cc = (max(cols) + min(cols)) / 2
        r, g, b = color[:3]
        col = (r, g, b, alpha)
        m = 1
        for row, c in cells:
            px = center_x + (c - cc) * cell_size
            py = center_y - (row - cr) * cell_size
            _fill(px, py, cell_size - m, cell_size - m, col)
            _outline(px, py, cell_size - m, cell_size - m, (0, 0, 0, 50))

    # ------------------------------------------------------------------
    # on_draw
    # ------------------------------------------------------------------

    def on_draw(self):
        self.clear()
        self._draw_board()
        self._draw_placed_pieces()
        self._draw_ghost()
        self._draw_sidebar()
        self._draw_dragging()
        self._draw_hud()
        if self.won:
            self._draw_victory()

    def _draw_board(self):
        board_cx = BOARD_LEFT + BOARD_COLS * CELL_SIZE / 2
        board_cy = BOARD_BOTTOM + BOARD_ROWS * CELL_SIZE / 2
        bw = BOARD_COLS * CELL_SIZE
        bh = BOARD_ROWS * CELL_SIZE
        # Bordure
        _fill(board_cx, board_cy, bw + 4, bh + 4, (55, 58, 80))
        # Fond
        _fill(board_cx, board_cy, bw, bh, COLOR_BOARD_BG)
        # Grille
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                cx, cy = self._board_to_screen(r, c)
                _outline(cx, cy, CELL_SIZE - 1, CELL_SIZE - 1, COLOR_GRID)

    def _draw_placed_pieces(self):
        for name, (cells, row, col) in self.game.placed_pieces.items():
            self._draw_piece_on_board(cells, row, col, PIECE_COLORS[name])

    def _draw_ghost(self):
        if self.dragging is None or self.ghost_row is None:
            return
        cells = self.game.get_orientation(self.dragging)
        can = self.game.board.can_place(cells, self.ghost_row, self.ghost_col)
        ghost_color = (80, 240, 120, 150) if can else (240, 80, 80, 150)
        for dr, dc in cells:
            r, c = self.ghost_row + dr, self.ghost_col + dc
            if 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS:
                cx, cy = self._board_to_screen(r, c)
                _fill(cx, cy, CELL_SIZE - 2, CELL_SIZE - 2, ghost_color)

    def _draw_sidebar(self):
        _fill(SIDEBAR_X + SIDEBAR_WIDTH / 2, WINDOW_HEIGHT / 2,
              SIDEBAR_WIDTH, WINDOW_HEIGHT, COLOR_SIDEBAR_BG)

        arcade.draw_text("PIECES", SIDEBAR_X + SIDEBAR_WIDTH / 2,
                         WINDOW_HEIGHT - 38, COLOR_TEXT, 17, bold=True,
                         anchor_x="center", anchor_y="center")

        for name, (cx, cy) in self._sidebar_pos.items():
            cells = self.game.get_orientation(name)
            placed = name in self.game.placed_pieces

            if name == self.dragging:
                self._draw_piece_preview(cells, cx, cy, PIECE_COLORS[name], alpha=50)
            elif placed:
                self._draw_piece_preview(cells, cx, cy, (90, 93, 115), alpha=180)
                arcade.draw_text("OK", cx + 32, cy + 32,
                                 (80, 200, 100), 12, bold=True,
                                 anchor_x="center", anchor_y="center")
            else:
                self._draw_piece_preview(cells, cx, cy, PIECE_COLORS[name])

            label_color = COLOR_TEXT_DIM if placed else COLOR_TEXT
            arcade.draw_text(name, cx, cy - PREVIEW_BOX_H // 2 + 14,
                             label_color, 13, bold=True,
                             anchor_x="center", anchor_y="center")

    def _draw_dragging(self):
        if self.dragging is None:
            return
        if not self._is_over_board(self.drag_x, self.drag_y):
            cells = self.game.get_orientation(self.dragging)
            self._draw_piece_preview(cells, self.drag_x, self.drag_y,
                                     PIECE_COLORS[self.dragging], cell_size=26)

    def _draw_hud(self):
        board_top = BOARD_BOTTOM + BOARD_ROWS * CELL_SIZE
        remaining = len(self.game.available_pieces)
        if self.dragging and self.dragging in self.game.available_pieces:
            remaining -= 1
        arcade.draw_text(
            f"Plateau {BOARD_ROWS}x{BOARD_COLS}   |   "
            f"Restantes : {remaining}   |   Posees : {len(self.game.placed_pieces)}",
            BOARD_LEFT, board_top + 12, COLOR_TEXT, 14)

        instructions = [
            "R : Tourner la piece",
            "E : Rotation inverse",
            "Clic gauche : Poser / Reprendre",
            "ESC : Recommencer",
        ]
        y = BOARD_BOTTOM - 25
        for line in instructions:
            arcade.draw_text(line, BOARD_LEFT, y, COLOR_TEXT_DIM, 12)
            y -= 20

    def _draw_victory(self):
        _fill(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
              WINDOW_WIDTH, WINDOW_HEIGHT, (0, 0, 0, 160))
        arcade.draw_text("FELICITATIONS !",
                         WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 30,
                         (255, 215, 0), 52, bold=True,
                         anchor_x="center", anchor_y="center")
        arcade.draw_text("Appuyez sur ESC pour recommencer",
                         WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 40,
                         COLOR_TEXT, 22,
                         anchor_x="center", anchor_y="center")

    # ------------------------------------------------------------------
    # Evenements souris
    # ------------------------------------------------------------------

    def on_mouse_press(self, x, y, button, modifiers):
        if self.won:
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            # Clic sur une piece disponible dans la barre laterale
            for name, (cx, cy) in self._sidebar_pos.items():
                if name not in self.game.available_pieces:
                    continue
                if name == self.dragging:
                    continue
                if abs(x - cx) < PREVIEW_BOX_W // 2 and abs(y - cy) < PREVIEW_BOX_H // 2 - 10:
                    self.dragging = name
                    self.drag_x, self.drag_y = x, y
                    return

            # Clic sur une piece posee sur le plateau pour la reprendre
            if self._is_over_board(x, y):
                row, col = self._screen_to_board(x, y)
                piece_at = self.game.board.get_piece_at(row, col)
                if piece_at:
                    self.game.pick_up(piece_at)
                    self.dragging = piece_at
                    self.drag_x, self.drag_y = x, y

    def on_mouse_motion(self, x, y, dx, dy):
        if self.dragging:
            self.drag_x, self.drag_y = x, y
            if self._is_over_board(x, y):
                self.ghost_row, self.ghost_col = self._screen_to_board(x, y)
            else:
                self.ghost_row = self.ghost_col = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_release(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT or self.dragging is None:
            return

        if self._is_over_board(x, y):
            row, col = self._screen_to_board(x, y)
            self.game.try_place(self.dragging, row, col)

        self.dragging = None
        self.ghost_row = self.ghost_col = None

        if self.game.is_won():
            self.won = True

    # ------------------------------------------------------------------
    # Evenements clavier
    # ------------------------------------------------------------------

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.game.reset()
            self.dragging = None
            self.ghost_row = self.ghost_col = None
            self.won = False
        elif self.dragging:
            if key == arcade.key.R:
                self.game.rotate(self.dragging)
            elif key == arcade.key.E:
                self.game.rotate_back(self.dragging)
