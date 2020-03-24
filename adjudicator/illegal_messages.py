# Basic checks - applies to all order types (except build).
B001 = ('B001', 'Cannot order a piece belonging to another nation.')

# Move checks - applies to move orders.
M001 = ('M001', 'Cannot move a piece belonging to another nation.')
M002 = ('M002', 'Cannot move to territory that the piece is already in.')
M003 = ('M003', 'Army cannot move to a non-adjacent territory without convoy.')
M004 = ('M004', 'Fleet cannot move to a non-adjacent territory.')
M005 = ('M005', 'Army cannot enter a sea territory')
M006 = ('M006', 'Fleet cannot enter an inland territory')
M007 = ('M007', 'Fleet move from a coastal territory to another adjacent coastal territory if there is no shared coastline.')

# Convoy checks - applies to convoy orders.
C001 = ('C001', 'Cannot convoy a fleet.')

# Support checks - applies to support orders.
S001 = ('S001', 'A piece cannot support itself.')
S002 = ('S002', 'A piece cannot support a territory which it cannot reach.')
