# Chaque forme est un frozenset de (row, col) representant les cases valides.
# Le total de cases doit toujours etre 60 (12 pieces x 5 cases).


def _rect(rows, cols):
    return frozenset((r, c) for r in range(rows) for c in range(cols))


def _from_text(text):
    """
    Construit une forme a partir d'un dessin ASCII.
    'X' = case valide, '.' = case vide/absente.
    Les espaces et lignes vides sont ignores.
    """
    cells = set()
    for r, line in enumerate(text.strip().splitlines()):
        for c, ch in enumerate(line):
            if ch == 'X':
                cells.add((r, c))
    return frozenset(cells)


# ------------------------------------------------------------------
# Formes predefinies — chacune contient exactement 60 cases
# ------------------------------------------------------------------

SHAPES = {
    # Rectangles classiques
    "6x10": _rect(6, 10),
    "5x12": _rect(5, 12),
    "4x15": _rect(4, 15),
    "3x20": _rect(3, 20),

    # Forme en U : 8 lignes x 8 colonnes avec un trou rectangulaire en bas au centre
    # Lignes 0-5 : 8 cases chacune = 48
    # Lignes 6-8 : 2+2 cases chacune = 12
    # Total = 60
    "U": _from_text("""
XXXXXXXX
XXXXXXXX
XXXXXXXX
XXXXXXXX
XXXXXXXX
XXXXXXXX
XX....XX
XX....XX
XX....XX
"""),

    # Croix : barre horizontale de 12 x 3 + extensions verticales de 4 x 3 (haut et bas)
    # Lignes 0-2  : 4 cases = 12
    # Lignes 3-5  : 12 cases = 36
    # Lignes 6-8  : 4 cases = 12
    # Total = 60
    "croix": _from_text("""                        
....XXXX....
....XXXX....
....XXXX....
XXXXXXXXXXXX
XXXXXXXXXXXX
XXXXXXXXXXXX
....XXXX....
....XXXX....
....XXXX....
"""),

    # T : barre du haut large (12x3) + pied central etroit (4x6)
    # Lignes 0-2 : 12 cases = 36
    # Lignes 3-8 : 4 cases = 24
    # Total = 60
    "T": _from_text("""
XXXXXXXXXXXX
XXXXXXXXXXXX
XXXXXXXXXXXX
....XXXX....
....XXXX....
....XXXX....
....XXXX....
....XXXX....
....XXXX....
"""),

    "U2": _from_text("""
XXX....XXX
XXX....XXX
XXX....XXX
XXX....XXX
XXX....XXX                     
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
"""),

    "Dino": _from_text("""
...........XXXX
...........XXX.
...........XXXX
..........XXX..                       
........XXXXX..
.......XXXXXXX.
......XXXXXX.X.
......XXXXX....
.....XXXXXX....
....XXX.XX.....
XXXXXX..XX.....
........XXX....
"""),

}
