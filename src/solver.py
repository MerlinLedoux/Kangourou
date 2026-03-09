"""
Verification de faisabilite apres chaque pose de piece.

Algorithme : retour-arriere exact (backtracking).
- La premiere case vide (coin superieur-gauche) DOIT etre couverte par une
  piece restante. On essaie toutes les options, en recursant apres chaque pose.
- Elagage par connexite : si une region vide a une taille non divisible par 5,
  on abandonne cette branche immediatement (condition necessaire).

Le calcul tourne dans un thread de fond pour ne pas bloquer l'interface.
"""

import threading

from .pieces import PIECE_ORIENTATIONS


# ── Heuristique rapide (elagage ET visualisation) ──────────────────────────

def _regions_valid(grid, valid_cells):
    """Vrai si toutes les regions connexes vides ont une taille divisible par 5."""
    empty = {c for c in valid_cells if grid[c] is None}
    visited = set()
    for start in empty:
        if start in visited:
            continue
        size = 0
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell in visited or cell not in empty:
                continue
            visited.add(cell)
            size += 1
            r, c = cell
            for nb in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if nb in empty and nb not in visited:
                    stack.append(nb)
        if size % 5 != 0:
            return False
    return True


def infeasible_cells(board):
    """
    Retourne les cases appartenant a des regions bloquees par l'heuristique
    (taille non divisible par 5). Utilise pour la coloration du plateau.
    """
    empty = {c for c in board.valid_cells if board.grid[c] is None}
    visited = set()
    blocked = set()
    for start in empty:
        if start in visited:
            continue
        region = set()
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell in visited or cell not in empty:
                continue
            visited.add(cell)
            region.add(cell)
            r, c = cell
            for nb in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if nb in empty and nb not in visited:
                    stack.append(nb)
        if len(region) % 5 != 0:
            blocked.update(region)
    return blocked


# ── Solveur par retour-arriere ──────────────────────────────────────────────

def _solve(grid, sorted_cells, valid_cells, remaining, orientations, cancelled):
    """
    Retour-arriere exact.

    Parametres
    ----------
    grid         : dict (r,c) -> piece_name | None  (copie locale, modifiee en place)
    sorted_cells : liste de toutes les cases valides triees (row, col) croissant
    valid_cells  : frozenset des memes cases (pour les lookups rapides)
    remaining    : set de noms de pieces encore disponibles
    orientations : dict nom -> liste d'orientations (tuples de (dr,dc))
    cancelled    : callable qui renvoie True si on doit s'arreter

    Retourne
    --------
    True  : une solution existe
    False : aucune solution possible
    None  : calcul annule (cancelled() est devenu True)
    """
    if cancelled():
        return None

    # Elagage : connexite des regions vides
    if not _regions_valid(grid, valid_cells):
        return False

    # Premiere case vide (coin superieur-gauche grace au tri)
    target = None
    for cell in sorted_cells:
        if grid[cell] is None:
            target = cell
            break

    # Plus de cases vides
    if target is None:
        return len(remaining) == 0  # gagne si toutes les pieces sont posees

    # Il reste des cases mais plus de pieces
    if not remaining:
        return False

    tr, tc = target

    # Essayer chaque piece restante dans chaque orientation
    for piece_name in list(remaining):
        for orientation in orientations[piece_name]:
            # La piece doit couvrir `target` : on essaie chaque cellule de la piece
            # comme correspondant a target
            for dr, dc in orientation:
                ar, ac = tr - dr, tc - dc

                # Verifier si le placement est valide
                cells_to_place = []
                ok = True
                for pr, pc in orientation:
                    cell = (ar + pr, ac + pc)
                    if cell not in valid_cells or grid[cell] is not None:
                        ok = False
                        break
                    cells_to_place.append(cell)
                if not ok:
                    continue

                # Poser la piece
                for cell in cells_to_place:
                    grid[cell] = piece_name
                remaining.discard(piece_name)

                result = _solve(grid, sorted_cells, valid_cells,
                                remaining, orientations, cancelled)

                # Annuler le placement
                for cell in cells_to_place:
                    grid[cell] = None
                remaining.add(piece_name)

                if result is True:
                    return True
                if result is None:       # annule
                    return None

    return False   # aucune piece ne peut couvrir target → branche morte


# ── Verificateur asynchrone ─────────────────────────────────────────────────

class FeasibilityChecker:
    """
    Lance la verification complete en tache de fond.

    Attribut public
    ---------------
    status : str
        "ok"       → au moins une solution existe
        "checking" → calcul en cours
        "blocked"  → aucune solution possible (confirme)
    """

    def __init__(self):
        # Compteur de generation : chaque nouvelle verification incremente ce
        # compteur ; les anciens threads s'arretent quand ils voient qu'ils
        # ne sont plus la generation courante.
        self._gen = [0]
        self.status = "ok"

    def check(self, board, remaining_pieces):
        """
        Lance une verification asynchrone a partir de l'etat actuel du jeu.
        Annule automatiquement tout calcul precedent.
        """
        # Verification rapide par heuristique : si deja bloquee, inutile de
        # lancer le solveur complet.
        if not _regions_valid(board.grid, board.valid_cells):
            self._gen[0] += 1
            self.status = "blocked"
            return

        # Snapshot independant du board (le jeu peut continuer pendant le calcul)
        grid_copy      = dict(board.grid)
        valid_cells    = board.valid_cells
        sorted_cells   = sorted(valid_cells)        # tri fait une seule fois
        remaining_copy = set(remaining_pieces)

        self._gen[0] += 1
        gen = self._gen[0]
        self.status = "checking"

        def run():
            cancelled = lambda: self._gen[0] != gen
            result = _solve(grid_copy, sorted_cells, valid_cells,
                            remaining_copy, PIECE_ORIENTATIONS, cancelled)
            # Ne mettre a jour que si ce thread est toujours "courant"
            if self._gen[0] == gen:
                if result is True:
                    self.status = "ok"
                elif result is False:
                    self.status = "blocked"
                # Si None (annule), on laisse l'etat "checking" ;
                # un nouveau check aura deja ete lance.

        threading.Thread(target=run, daemon=True).start()

    def reset(self):
        """Annule tout calcul en cours et remet l'etat a 'ok'."""
        self._gen[0] += 1
        self.status = "ok"
