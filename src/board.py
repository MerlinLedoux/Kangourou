class Board:
    """
    Plateau de jeu a forme arbitraire.
    valid_cells : frozenset de (row, col) definissant les cases jouables.
    """

    def __init__(self, valid_cells):
        self.valid_cells = frozenset(valid_cells)
        # Dictionnaire (row, col) -> nom de piece ou None
        self.grid = {cell: None for cell in self.valid_cells}

        # Bornes precalculees pour le rendu
        self.min_row = min(r for r, _ in self.valid_cells)
        self.max_row = max(r for r, _ in self.valid_cells)
        self.min_col = min(c for _, c in self.valid_cells)
        self.max_col = max(c for _, c in self.valid_cells)

    # Dimensions de la boite englobante
    @property
    def rows(self):
        return self.max_row - self.min_row + 1

    @property
    def cols(self):
        return self.max_col - self.min_col + 1

    def can_place(self, cells, anchor_row: int, anchor_col: int) -> bool:
        for dr, dc in cells:
            cell = (anchor_row + dr, anchor_col + dc)
            if cell not in self.valid_cells:
                return False
            if self.grid[cell] is not None:
                return False
        return True

    def place(self, cells, anchor_row: int, anchor_col: int, piece_name: str):
        for dr, dc in cells:
            self.grid[(anchor_row + dr, anchor_col + dc)] = piece_name

    def remove_piece(self, piece_name: str):
        for cell in self.valid_cells:
            if self.grid[cell] == piece_name:
                self.grid[cell] = None

    def get_piece_at(self, row: int, col: int):
        return self.grid.get((row, col))

    def is_complete(self) -> bool:
        return all(v is not None for v in self.grid.values())

    def reset(self):
        self.grid = {cell: None for cell in self.valid_cells}
