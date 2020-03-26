# relationships between territories. Look into observer pattern
from . import decisions


class Territory:
    is_complex = False
    is_coastal = False

    def __init__(self, id, name, neighbour_ids):
        self.id = id
        self.name = name
        self.neighbour_ids = neighbour_ids

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.name} - {self.__class__.__name__}'

    @property
    def hold_strength(self):
        return decisions.HoldStrength(self)()




class LandTerritory(Territory):

    def __init__(self, id, name, nationality, neighbour_ids, supply_center=False):
        super().__init__(id, name, neighbour_ids)
        self.nationality = nationality
        self.supply_center = supply_center


class CoastalTerritory(LandTerritory):

    is_coastal = True

    def __init__(self, id, name, nationality, neighbour_ids, shared_coast_ids):
        super().__init__(id, name, nationality, neighbour_ids)
        self.shared_coast_ids = shared_coast_ids

    @staticmethod
    def accessible_by_piece_type(piece):
        return True


class InlandTerritory(LandTerritory):

    @staticmethod
    def accessible_by_piece_type(piece):
        return piece.__class__.__name__ == 'Army'


class SeaTerritory(Territory):

    @staticmethod
    def accessible_by_piece_type(piece):
        return piece.__class__.__name__ == 'Fleet'


def get_neighbours(state, territory):
    """
    Gets the shared_coasts of the given territory.

    Returns:
        * A list of `Territory` instances.
    """
    neighbours = []
    for t in state.territories:
        if t.id in territory.neighbour_ids:
            neighbours.append(t)
    return neighbours


def get_piece(state, territory):
    """
    Gets the `Piece` instance which exists in the territory or `None` if
    there is no piece in the territory.

    Returns:
        * `Piece` or `None`
    """
    for p in state.pieces:
        if p.territory == territory:
            return p
    return None


def get_shared_coasts(state, territory):
    """
    Gets the shared_coasts of the given territory.

    Returns:
        * A list of `Territory` instances.
    """
    shared_coasts = []
    for t in state.territories:
        if t.id in territory.shared_coast_ids:
            shared_coasts.append(t)
    return shared_coasts


def get_named_coasts(state, territory):
    """
    Gets the named coasts of the given territory.

    Returns:
        * A list of `Named_Coast` instances.
    """
    named_coasts = []
    for n in state.named_coasts:
        if n.parent == territory:
            named_coasts.append(n)
    return named_coasts


def get_attacking_pieces(state, territory):
    """
    Gets all pieces which are moving into the given territory.

    Returns:
        * `list` of `Piece` instances
    """
    attacking_pieces = []
    for p in state.pieces:
        if p.order.__class__.__name__ == 'Move':
            if p.order.target == territory:
                attacking_pieces.append(p)
    return attacking_pieces


def get_other_attacking_pieces(state, territory, piece):
    """
    Gets all pieces which are moving into this territory excluding the
    given piece.

    Returns:
        * `list` of `Piece` instances.
    """
    other_attacking_pieces = get_attacking_pieces(state, territory)
    for p in other_attacking_pieces:
        if p == piece:
            other_attacking_pieces.remove(p)
    return other_attacking_pieces


def get_foreign_attacking_pieces(state, territory, nation):
    """
    Gets all pieces which are moving into this territory
    who do not belong to the given nation.

    Returns:
         * `list` of `piece` instances.
    """
    foreign_attacking_pieces = get_attacking_pieces(state, territory)
    for p in foreign_attacking_pieces:
        if p.nation == nation:
            foreign_attacking_pieces.remove(p)
    return foreign_attacking_pieces


def friendly_piece_exists(state, territory, nation):
    """
    Determine whether a piece belonging to the given nation exists in the
    territory.

    Returns:
        * `bool`
    """
    piece = get_piece(state, territory)
    if piece:
        return piece.nation == nation
    return False

def adjacent(state, territory):
    return territory in self.neighbours
