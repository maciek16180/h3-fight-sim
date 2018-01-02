from unit import make_unit, Stack
from combat import fight as fight_orig
from combat import find_balance as find_balance_orig


def fight(nameA, countA, nameB, countB, num_fights):
    A = Stack(make_unit(nameA), countA)
    B = Stack(make_unit(nameB), countB)
    result = fight_orig(A, B, num_fights)
    return result[A.name][0], result[B.name][0]


def find_balance(nameA, countA, nameB, countB, num_fights):
    count1 = countA or countB
    idxA = 1 if countB else 0
    idxB = (idxA + 1) % 2
    name1 = nameA if count1 == countA else nameB
    name2 = nameB if count1 == countA else nameA
    result = find_balance_orig(name1, name2, num_fights, count1)
    return result[idxA], result[idxB], idxA == 0
