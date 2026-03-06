import arcade

from ..game import Game
from ..pieces import PIECE_COLORS

# ---------------------------------------------------------------------------
# Constantes de mise en page
# ---------------------------------------------------------------------------
WINDOW_WIDTH  = 1200
WINDOW_HEIGHT = 780
WINDOW_TITLE  = "Pentaminos"

MAX_CELL_SIZE = 60   # taille max quand la forme est petite

# Coin bas-gauche du plateau sur l'ecran
BOARD_LEFT   = 40
BOARD_BOTTOM = 190

# Barre laterale (pieces disponibles)
SIDEBAR_X     = 720
SIDEBAR_WIDTH = WINDOW_WIDTH - SIDEBAR_X - 15

PREVIEW_CELL  = 18
PREVIEW_COLS  = 3
PREVIEW_BOX_W = SIDEBAR_WIDTH // PREVIEW_COLS
PREVIEW_BOX_H = 140

COLOR_BG         = (28,  30,  42)
COLOR_BOARD_BG   = (44,  47,  64)
COLOR_BOARD_VOID = (22,  24,  34)   # cases hors de la forme
COLOR_GRID       = (68,  72,  100)
COLOR_SIDEBAR_BG = (36,  38,  52)
COLOR_TEXT       = (210, 212, 225)
COLOR_TEXT_DIM   = (140, 143, 165)

DEFAULT_SHAPE = "6x10"


# ---------------------------------------------------------------------------
# Helpers de dessin (API Arcade 3.x)
# ---------------------------------------------------------------------------

def _fill(cx, cy, w, h, color):
    arcade.draw_lbwh_rectangle_filled(cx - w / 2, cy - h / 2, w, h, color)


def _outline(cx, cy, w, h, color, border_width=1):
    arcade.draw_lbwh_rectangle_outline(cx - w / 2, cy - h / 2, w, h, color, border_width)


# ---------------------------------------------------------------------------
# Fenetre principale
# ---------------------------------------------------------------------------

class GameWindow(arcade.Window):

    def __init__(self, shape_name: str = DEFAULT_SHAPE):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, resizable=False)
        self.background_color = COLOR_BG

        self.game = Game(shape_name)

        self.dragging: str | None = None
        self.drag_x = 0
        self.drag_y = 0
        self.ghost_row: int | None = None
        self.ghost_col: int | None = None

        # Taille d'une case calculee pour que le plateau tienne dans la fenetre
        available_w = SIDEBAR_X - BOARD_LEFT - 20
        available_h = WINDOW_HEIGHT - BOARD_BOTTOM - 80
        cell_by_w   = available_w // self.game.board.cols
        cell_by_h   = available_h // self.game.board.rows
        self.cell_size = min(cell_by_w, cell_by_h, MAX_CELL_SIZE)

        self._sidebar_pos: dict = self._compute_sidebar_positions()
        self.won    = False
        self.elapsed = 0.0

    # ------------------------------------------------------------------
    # Conversions coordonnees
    # ------------------------------------------------------------------

    def _board_to_screen(self, row: int, col: int) -> tuple:
        """Centre de la case (row, col) en pixels Arcade."""
        b = self.game.board
        x = BOARD_LEFT + (col - b.min_col) * self.cell_size + self.cell_size / 2
        y = BOARD_BOTTOM + (b.max_row - row) * self.cell_size + self.cell_size / 2
        return x, y

    def _screen_to_board(self, x: float, y: float) -> tuple:
        """Case du plateau sous le curseur (peut etre hors de la forme)."""
        b = self.game.board
        col = b.min_col + int((x - BOARD_LEFT) / self.cell_size)
        row = b.max_row - int((y - BOARD_BOTTOM) / self.cell_size)
        return row, col

    def _is_over_board_area(self, x: float, y: float) -> bool:
        """Vrai si le curseur est dans la zone rectangulaire du plateau."""
        b = self.game.board
        return (BOARD_LEFT <= x < BOARD_LEFT + b.cols * self.cell_size and
                BOARD_BOTTOM <= y < BOARD_BOTTOM + b.rows * self.cell_size)

    def _centered_anchor(self, x: float, y: float) -> tuple:
        """
        Calcule l'ancre (row, col) pour que le centre de la piece
        soit sous le curseur plutot que le coin (0,0).
        """
        mouse_row, mouse_col = self._screen_to_board(x, y)
        cells = self.game.get_orientation(self.dragging)
        rows_ = [r for r, _ in cells]
        cols_ = [c for _, c in cells]
        center_dr = round((max(rows_) + min(rows_)) / 2)
        center_dc = round((max(cols_) + min(cols_)) / 2)
        return mouse_row - center_dr, mouse_col - center_dc

    # ------------------------------------------------------------------
    # Mise en page de la barre laterale
    # ------------------------------------------------------------------

    def _compute_sidebar_positions(self) -> dict:
        names = sorted(PIECE_COLORS.keys())
        start_y = WINDOW_HEIGHT - 120
        positions = {}
        for i, name in enumerate(names):
            col_idx = i % PREVIEW_COLS
            row_idx = i // PREVIEW_COLS
            cx = SIDEBAR_X + col_idx * PREVIEW_BOX_W + PREVIEW_BOX_W // 2
            cy = start_y - row_idx * PREVIEW_BOX_H 
            positions[name] = (cx, cy)
        return positions

    # ------------------------------------------------------------------
    # Primitives de dessin
    # ------------------------------------------------------------------

    def _draw_cell(self, cx: float, cy: float, color: tuple, size: int = 0):
        if size == 0:
            size = self.cell_size
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
        rows_ = [r for r, _ in cells]
        cols_ = [c for _, c in cells]
        cr = (max(rows_) + min(rows_)) / 2
        cc = (max(cols_) + min(cols_)) / 2
        r, g, b = color[:3]
        col = (r, g, b, alpha)
        m = 1
        for row, c in cells:
            px = center_x + (c - cc) * cell_size
            py = center_y - (row - cr) * cell_size
            _fill(px, py, cell_size - m, cell_size - m, col)
            _outline(px, py, cell_size - m, cell_size - m, (0, 0, 0, 50))

    # ------------------------------------------------------------------
    # on_update
    # ------------------------------------------------------------------

    def on_update(self, delta_time: float):
        if not self.won:
            self.elapsed += delta_time

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
        board = self.game.board

        # Boite englobante (fond sombre pour les cases hors forme)
        bw = board.cols * self.cell_size
        bh = board.rows * self.cell_size
        bx = BOARD_LEFT + bw / 2
        by = BOARD_BOTTOM + bh / 2
        _fill(bx, by, bw + 4, bh + 4, (22, 24, 34))

        # Uniquement les cases valides
        for (r, c) in board.valid_cells:
            cx, cy = self._board_to_screen(r, c)
            _fill(cx, cy, self.cell_size, self.cell_size, COLOR_BOARD_BG)
            _outline(cx, cy, self.cell_size - 1, self.cell_size - 1, COLOR_GRID)

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
            if (r, c) in self.game.board.valid_cells:
                cx, cy = self._board_to_screen(r, c)
                _fill(cx, cy, self.cell_size - 2, self.cell_size - 2, ghost_color)

    def _draw_sidebar(self):
        _fill(SIDEBAR_X + SIDEBAR_WIDTH / 2, WINDOW_HEIGHT / 2,
              SIDEBAR_WIDTH, WINDOW_HEIGHT, COLOR_SIDEBAR_BG)

        arcade.draw_text("PIECES", SIDEBAR_X + SIDEBAR_WIDTH / 2,
                         WINDOW_HEIGHT - 38, COLOR_TEXT, 17, bold=True,
                         anchor_x="center", anchor_y="center")

        for name, (cx, cy) in self._sidebar_pos.items():
            cells  = self.game.get_orientation(name)
            placed = name in self.game.placed_pieces

            if name == self.dragging:
                self._draw_piece_preview(cells, cx, cy, PIECE_COLORS[name], alpha=50)
            elif placed:
                self._draw_piece_preview(cells, cx, cy, (90, 93, 115), alpha=180)
                arcade.draw_text("OK", cx + 32, cy + 32, (80, 200, 100), 12,
                                 bold=True, anchor_x="center", anchor_y="center")
            else:
                self._draw_piece_preview(cells, cx, cy, PIECE_COLORS[name])

            label_color = COLOR_TEXT_DIM if placed else COLOR_TEXT
            arcade.draw_text(name, cx, cy - PREVIEW_BOX_H // 2 + 14,
                             label_color, 13, bold=True,
                             anchor_x="center", anchor_y="center")

    def _draw_dragging(self):
        if self.dragging is None:
            return
        if not self._is_over_board_area(self.drag_x, self.drag_y):
            cells = self.game.get_orientation(self.dragging)
            self._draw_piece_preview(cells, self.drag_x, self.drag_y,
                                     PIECE_COLORS[self.dragging], cell_size=26)

    def _draw_hud(self):
        board = self.game.board
        board_top_y = BOARD_BOTTOM + board.rows * self.cell_size

        remaining = len(self.game.available_pieces)
        if self.dragging and self.dragging in self.game.available_pieces:
            remaining -= 1

        minutes  = int(self.elapsed) // 60
        secondes = int(self.elapsed) % 60

        arcade.draw_text(
            f"Forme : {self.game.shape_name}   |   "
            f"Restantes : {remaining}   |   "
            f"Posees : {len(self.game.placed_pieces)}   |   "
            f"{minutes:02d}:{secondes:02d}",
            BOARD_LEFT, board_top_y + 12, COLOR_TEXT, 14)

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

    def on_mouse_press(self, x, y, button, _modifiers):
        if self.won:
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            # Clic sur une piece disponible dans la barre laterale
            for name, (cx, cy) in self._sidebar_pos.items():
                if name not in self.game.available_pieces or name == self.dragging:
                    continue
                if abs(x - cx) < PREVIEW_BOX_W // 2 and abs(y - cy) < PREVIEW_BOX_H // 2 - 10:
                    self.dragging = name
                    self.drag_x, self.drag_y = x, y
                    return

            # Clic sur une piece posee sur le plateau pour la reprendre
            row, col = self._screen_to_board(x, y)
            piece_at = self.game.board.get_piece_at(row, col)
            if piece_at:
                self.game.pick_up(piece_at)
                self.dragging = piece_at
                self.drag_x, self.drag_y = x, y

    def on_mouse_motion(self, x, y, dx, dy):
        if self.dragging:
            self.drag_x, self.drag_y = x, y
            if self._is_over_board_area(x, y):
                self.ghost_row, self.ghost_col = self._centered_anchor(x, y)
            else:
                self.ghost_row = self.ghost_col = None

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_release(self, x, y, button, modifiers):
        if button != arcade.MOUSE_BUTTON_LEFT or self.dragging is None:
            return

        # Utilise le meme centrage que le ghost pour placer la piece
        row, col = self._centered_anchor(x, y)
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
            self.won    = False
            self.elapsed = 0.0
        elif self.dragging:
            if key == arcade.key.R:
                self.game.rotate(self.dragging)
            elif key == arcade.key.E:
                self.game.rotate_back(self.dragging)
