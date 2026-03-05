class Board:
    """
    Grille de jeu. Chaque case contient None (vide) ou le nom de la piece placee.
    Origine (0, 0) = coin superieur gauche.
    """

    def __init__(self, rows: int = 6, cols: int = 10):
        self.rows = rows
        self.cols = cols
        self.grid = [[None] * cols for _ in range(rows)]

    def can_place(self, cells, anchor_row: int, anchor_col: int) -> bool:
        """Verifie si la piece peut etre placee a la position d'ancrage."""
        for dr, dc in cells:
            r, c = anchor_row + dr, anchor_col + dc
            if not (0 <= r < self.rows and 0 <= c < self.cols):
                return False
            if self.grid[r][c] is not None:
                return False
        return True

    def place(self, cells, anchor_row: int, anchor_col: int, piece_name: str):
        """Place la piece sur la grille (suppose can_place == True)."""
        for dr, dc in cells:
            self.grid[anchor_row + dr][anchor_col + dc] = piece_name

    def remove_piece(self, piece_name: str):
        """Retire toutes les cases d'une piece de la grille."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == piece_name:
                    self.grid[r][c] = None

    def get_piece_at(self, row: int, col: int):
        """Retourne le nom de la piece en (row, col), ou None."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None

    def is_complete(self) -> bool:
        """Vrai si toutes les cases sont occupees."""
        return all(
            self.grid[r][c] is not None
            for r in range(self.rows)
            for c in range(self.cols)
        )

    def reset(self):
        """Vide la grille."""
        self.grid = [[None] * self.cols for _ in range(self.rows)]
