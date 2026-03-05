# Les 12 pentaminos, chacun defini par ses cellules (ligne, colonne) relatives
PIECE_SHAPES = {
    'F': [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)],
    'I': [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
    'L': [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1)],
    'N': [(0, 1), (1, 0), (1, 1), (2, 0), (3, 0)],
    'P': [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)],
    'T': [(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)],
    'U': [(0, 0), (0, 2), (1, 0), (1, 1), (1, 2)],
    'V': [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],
    'W': [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)],
    'X': [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],
    'Y': [(0, 1), (1, 0), (1, 1), (2, 1), (3, 1)],
    'Z': [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)],
}

PIECE_COLORS = {
    'F': (220, 80,  80),
    'I': (80,  180, 255),
    'L': (255, 155, 40),
    'N': (80,  210, 80),
    'P': (240, 80,  200),
    'T': (110, 110, 255),
    'U': (255, 210, 40),
    'V': (170, 60,  255),
    'W': (60,  200, 170),
    'X': (255, 130, 60),
    'Y': (60,  160, 255),
    'Z': (190, 190, 60),
}


def _normalize(cells):
    """Retourne les cellules normalisees (min_r=0, min_c=0) triees."""
    cells = list(cells)  # consomme le generateur une seule fois
    min_r = min(r for r, c in cells)
    min_c = min(c for r, c in cells)
    return tuple(sorted((r - min_r, c - min_c) for r, c in cells))


def _rotate_90(cells):
    """Rotation 90 degres dans le sens horaire : (r, c) -> (c, -r)."""
    return _normalize((c, -r) for r, c in cells)


def _reflect(cells):
    """Reflexion horizontale : (r, c) -> (r, -c)."""
    return _normalize((r, -c) for r, c in cells)


def get_all_orientations(base_cells):
    """
    Retourne la liste de toutes les orientations uniques d'une piece.
    Ordre : 4 rotations, puis reflexion + 4 rotations.
    Chaque orientation est un tuple de (r, c) tries.
    """
    seen = set()
    result = []

    current = _normalize(base_cells)
    for _ in range(4):
        if current not in seen:
            seen.add(current)
            result.append(current)
        current = _rotate_90(current)

    current = _reflect(_normalize(base_cells))
    for _ in range(4):
        if current not in seen:
            seen.add(current)
            result.append(current)
        current = _rotate_90(current)

    return result


# Toutes les orientations precalculees pour chaque piece
PIECE_ORIENTATIONS = {
    name: get_all_orientations(cells)
    for name, cells in PIECE_SHAPES.items()
}
