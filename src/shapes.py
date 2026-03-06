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

    "U": _from_text("""
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

    # ------------------------------------------------------------------
    # Nouvelles formes thematiques (60 cases chacune)
    # ------------------------------------------------------------------

    # Maison : toit triangulaire (2+4+6+8) + base carree (4x10)
    "maison": _from_text("""
....X....
...XXX...
..XXXXX..
.XXXXXXX.
XXXXXXXXX
.XXXXXXX.
.XXXXXXX.
.XXXXXXX.
.XXXXXXX.
.XXXXXXX.
"""),

    # Avion : fuselage vertical + ailes larges + stabilisateurs
    # Nez (4) + fuselage (2x2) + ailes (3x10) + fuselage (2x2)
    # + stabilisateurs (6) + fuselage arriere (6x2) = 60
    "avion": _from_text("""
......X......
.....XXX.....
.....XXX.....
.....XXX.....
XXXXXXXXXXXXX
XXXXXXXXXXXXX
..XXXXXXXXX..
.....XXX.....
.....XXX.....
.....XXX.....
....XXXXX....
......X......
"""),

    # Coeur : deux bosses en haut, pointe en bas
    # Rang 0 : 6  + rangs 1-4 : 40  + rang 5 : 8  + rang 6 : 4  + rang 7 : 2 = 60
    "coeur": _from_text("""
.XXX.XXX..
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
XXXXXXXXXX
.XXXXXXXX.
...XXXX...
....XX....
"""),

    # Arbre de noel : deux niveaux triangulaires + tronc
    # Triangle 1 (2+4+6+8+10) + Triangle 2 (6+8+10) + tronc (2+2+2) = 60
    "arbre": _from_text("""
....XX....
...XXXX...
..XXXXXX..
.XXXXXXXX.
XXXXXXXXXX
..XXXXXX..
.XXXXXXXX.
XXXXXXXXXX
....XX....
....XX....
....XX....
"""),

    # Losange / diamant
    # Symetrie parfaite : 2+4+6+8+10+10+8+6+4+2 = 60
    "losange": _from_text("""
....XX....
...XXXX...
..XXXXXX..
.XXXXXXXX.
XXXXXXXXXX
XXXXXXXXXX
.XXXXXXXX.
..XXXXXX..
...XXXX...
....XX....
"""),

    # Kangourou stylise (vu de cote, regardant a droite)
    # Oreille fine en haut a droite, corps ovale, pattes en bas
    # 2+4+5+7+9+10+9+7+5+2 = 60
    "kangourou": _from_text("""
...........X...
...........XXX.
...........XX..
...........XX..
...........XX..
...........XX..
.........XXXXXX
.......XXXXXX.X
......XXXXXX...
.....XXXXXXX...
.....XXXXXX....
....XXX.XXX....
XXXXXX...XXXX..
"""),

}
