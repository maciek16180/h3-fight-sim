from unit import make_unit, Stack
from combat import fight as fight_orig
from combat import find_balance as find_balance_orig


def fight(nameA, countA, nameB, countB, num_fights):
    A = Stack(make_unit(nameA), countA)
    B = Stack(make_unit(nameB), countB)
    result = fight_orig(A, B, num_fights)
    return result[A.name][0], result[B.name][0]


def find_balance(nameA, countA, nameB, countB, num_fights):
    swap = not countA
    if swap:
        count1 = countB
        name1, name2 = nameB, nameA
        idxA = 1
    else:
        count1 = countA
        name1, name2 = nameA, nameB
        idxA = 0
    result = find_balance_orig(name1, name2, num_fights, count1)
    return result[idxA], result[(idxA + 1) % 2], swap
