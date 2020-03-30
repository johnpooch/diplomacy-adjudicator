from copy import deepcopy
"""
It is possible that during adjudication according to the given prescriptions of
making decisions, a situation occurs that no decision can be made anymore while
there are still decisions to make. At such moment the board contains a circular
movement or convoy paradox. Those situations need special treatment.

The first step in resolving a circular movement or paradox is to determine
which decisions are part of the circular movement or the paradox core. This is
achieved by listing for each decision the decisions it directly depends on.
Decisions that are fully decided are completely left out of this procedure.
When these lists are made, these lists are extended with all the indirect
decisions dependencies. This is continued until each decision has a list with
all direct and indirect (with possible multiple indirections) dependencies.
Every list forms a paradox, but the smallest dependency list is a paradox core
and only that list should be considered. Note that there are probably more than
one dependency lists with an equal and smallest number of dependencies. It is
unimportant which one of these lists is selected.

In the second step the dependency list is analyzed. If the list of decisions
contains an undecided MOVE decision of a unit that targets a fleet with a
convoy order, then there is a convoy disruption paradox. If there is no such
decision, then there is a circular movement. Note that if one of the moving
units in a circular movement moved with certainty due to a support, then the
adjudication of the circular movement would have been resolved in the normal
process adjudication.

In the final step the circular movement or paradox is enforced by special rules
and the normal decision making process can continue. In case of a circular
movement, all the MOVE decisions of the dependency list are resolved to
'moves'.

In case of convoy disruption paradox, a convoy paradox rule must be
applied on the dependency list. Note that the MOVE decision of the army that
convoys is not in the dependency list, since for the paradox only the cutting
of support is essential. Therefore only the ATTACK STRENGTH decision of the
army that convoys appears in the dependency list. This is important when
applying the Szykman rule or the 'All Hold' rule.

When the Szykman rule is applied, all ATTACK STRENGTH decisions in the
dependency list are set to zero for both minimum as maximum. The corresponding
MOVE decision is set to failed and the corresponding PREVENT STRENGTH is also
to zero for both minimum as maximum.
"""


def find_circular_movements(moves):
    copied_moves = moves
    circular_movements = []
    for node_a in copied_moves:
        # look at the target of the first move
        copied_moves.remove(node_a)
        if node_a.target.piece:
            node_b = node_a.target.piece.order
            copied_moves.remove(node_b)
            # This would be a head to head.
            if node_b.is_move and node_b.target != node_a.source:
                # go
                next_node = node_b.target.piece.order
                found_original_node = False
                nodes = [node_a, node_b]
                while not found_original_node:
                    nodes.append(next_node)
                    copied_moves.remove(next_node)
                    if next_node.is_move:
                        if next_node.target == node_a.source:
                            found_original_node = True
                            circular_movements.append(nodes)
                        else:
                            next_node = next_node.target.piece.order
    return circular_movements


