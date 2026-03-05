from .pieces import PIECE_SHAPES, PIECE_ORIENTATIONS
from .board import Board
from .shapes import SHAPES


class Game:
    """
    Etat complet d'une partie de pentaminos.
    shape_name : cle dans SHAPES (ex: "6x10", "U", "croix"...)
    """

    def __init__(self, shape_name: str = "6x10"):
        self.shape_name = shape_name
        self.board = Board(SHAPES[shape_name])

        self.orientation_idx = {name: 0 for name in PIECE_SHAPES}
        self.placed_pieces: dict = {}
        self.available_pieces: list = list(PIECE_SHAPES.keys())

    # ------------------------------------------------------------------
    # Lecture
    # ------------------------------------------------------------------

    def get_orientation(self, piece_name: str) -> tuple:
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
        n = self.num_orientations(piece_name)
        self.orientation_idx[piece_name] = (self.orientation_idx[piece_name] + 1) % n

    def rotate_back(self, piece_name: str):
        n = self.num_orientations(piece_name)
        self.orientation_idx[piece_name] = (self.orientation_idx[piece_name] - 1) % n

    # ------------------------------------------------------------------
    # Placement
    # ------------------------------------------------------------------

    def try_place(self, piece_name: str, anchor_row: int, anchor_col: int) -> bool:
        cells = self.get_orientation(piece_name)
        if not self.board.can_place(cells, anchor_row, anchor_col):
            return False
        self.board.place(cells, anchor_row, anchor_col, piece_name)
        self.placed_pieces[piece_name] = (cells, anchor_row, anchor_col)
        if piece_name in self.available_pieces:
            self.available_pieces.remove(piece_name)
        return True

    def pick_up(self, piece_name: str):
        if piece_name in self.placed_pieces:
            self.board.remove_piece(piece_name)
            del self.placed_pieces[piece_name]
        if piece_name not in self.available_pieces:
            self.available_pieces.append(piece_name)

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self):
        self.__init__(self.shape_name)
