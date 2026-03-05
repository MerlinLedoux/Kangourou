from .pieces import PIECE_SHAPES, PIECE_ORIENTATIONS
from .board import Board


class Game:
    """
    Etat complet d'une partie de pentaminos.
    Gere les pieces, le plateau et les interactions logiques.
    """

    def __init__(self, rows: int = 6, cols: int = 10):
        self.rows = rows
        self.cols = cols
        self.board = Board(rows, cols)

        # Index de l'orientation courante pour chaque piece (0 = orientation de base)
        self.orientation_idx = {name: 0 for name in PIECE_SHAPES}

        # Pieces deja posees : nom -> (cells, anchor_row, anchor_col)
        self.placed_pieces: dict = {}

        # Pieces encore disponibles (pas sur le plateau)
        self.available_pieces: list = list(PIECE_SHAPES.keys())

    # ------------------------------------------------------------------
    # Lecture
    # ------------------------------------------------------------------

    def get_orientation(self, piece_name: str) -> tuple:
        """Retourne les cellules de l'orientation courante d'une piece."""
        idx = self.orientation_idx[piece_name]
        return PIECE_ORIENTATIONS[piece_name][idx]

    def num_orientations(self, piece_name: str) -> int:
        return len(PIECE_ORIENTATIONS[piece_name])

    def is_won(self) -> bool:
        return self.board.is_complete()

    # ------------------------------------------------------------------
    # Rotations
    # ------------------------------------------------------------------

    def rotate(self, piece_name: str):
        """Passe a l'orientation suivante (rotation + reflexion incluses)."""
        n = self.num_orientations(piece_name)
        self.orientation_idx[piece_name] = (self.orientation_idx[piece_name] + 1) % n

    def rotate_back(self, piece_name: str):
        """Revient a l'orientation precedente."""
        n = self.num_orientations(piece_name)
        self.orientation_idx[piece_name] = (self.orientation_idx[piece_name] - 1) % n

    # ------------------------------------------------------------------
    # Placement
    # ------------------------------------------------------------------

    def try_place(self, piece_name: str, anchor_row: int, anchor_col: int) -> bool:
        """
        Tente de placer la piece a la position d'ancrage.
        Retourne True si le placement a reussi.
        """
        cells = self.get_orientation(piece_name)
        if not self.board.can_place(cells, anchor_row, anchor_col):
            return False

        self.board.place(cells, anchor_row, anchor_col, piece_name)
        self.placed_pieces[piece_name] = (cells, anchor_row, anchor_col)
        if piece_name in self.available_pieces:
            self.available_pieces.remove(piece_name)
        return True

    def pick_up(self, piece_name: str):
        """
        Retire la piece du plateau et la remet dans les pieces disponibles.
        L'orientation courante est conservee (le joueur peut la faire tourner).
        """
        if piece_name in self.placed_pieces:
            self.board.remove_piece(piece_name)
            del self.placed_pieces[piece_name]
        if piece_name not in self.available_pieces:
            self.available_pieces.append(piece_name)

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self):
        """Remet le jeu dans son etat initial."""
        self.__init__(self.rows, self.cols)
