from unit import make_unit, Stack
from combat import fight as fight_orig
from combat import find_balance as find_balance_orig


def fight(nameA, countA, nameB, countB, num_fights):
    A = Stack(make_unit(nameA), countA)
    B = Stack(make_unit(nameB), countB)
    result = fight_orig(A, B, num_fights)
    resA = A.name + ": {}".format(result[A.name][0])
    resB = B.name + ": {}".format(result[B.name][0])
    return resA, resB


def find_balance(nameA, countA, nameB, countB, num_fights):
    count1 = countA or countB
    idxA = 1 if countB else 0
    idxB = (idxA + 1) % 2
    name1 = nameA if count1 == countA else nameB
    name2 = nameB if count1 == countA else nameA
    result = find_balance_orig(name1, name2, num_fights, count1)
    res = u"{} {} \u2248 {} {}".format(
        result[idxA], nameA,
        result[idxB], nameB)
    return res
