from math import ceil, pi, cos, log
from random import random, randint

from crtraits import data, haters, elementals


data = dict(data)

keywords = {
    'DOUBLE_WIDE',
    'SHOOTING_ARMY',
    'const_free_attack',
    'const_jousting',
    'const_no_melee_penalty',
    'const_two_attacks',
    'IS_UNDEAD',
    'cusELEMENTAL',
    'cusGOLEM'
}


# Box-Muller transform
def my_gauss(mu, sigma):
    return sigma * ((-2*log(random()))**.5 * cos(2*pi*random())) + mu


# for sufficiently large n we can use much faster normal approximation
def my_binomial(n, p):
    if n < 100:
        return sum(random() < p for _ in range(int(n)))
    return int(my_gauss(n*p, (n*p*(1-p))**.5))


def my_divmod(n, m):
    div = n // m
    mod = n - m * div
    return div, mod


def make_unit(name):
    assert name in data
    # return UnitType(*([name] + data[name]))
    d = data[name]
    return UnitType(name, d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8])


class UnitType(object):

    def __init__(self, name, aiv, hp, spd, att, df,
                 dmlow, dmhi, shots, abi):
        self.name = name
        self.ai_value = aiv
        self.hp = hp
        self.speed = spd
        self.attack = att
        self.defense = df
        self.dmg_min = dmlow
        self.dmg_max = dmhi
        self.shots = shots
        self.attributes = [x for x in abi if x in keywords]
        self.hates = [v for (k, v) in haters if k == self.name]
        self.opp_elem = [v for (k, v) in elementals if k == self.name]


class Stack(object):

    def __init__(self, unit, count):
        # these values can't change during combat:
        self.unit = unit
        self.cap = count
        self.name = unit.name
        self.speed = unit.speed
        self.true_hp = unit.hp
        self.true_attack = unit.attack
        self.true_defense = unit.defense
        self.dmg_min = unit.dmg_min
        self.dmg_max = unit.dmg_max
        self.hates = unit.hates
        self.opp_elem = unit.opp_elem
        self.attributes = unit.attributes

        if self.name == 'Battle Dwarf':
            self.magic_resist = .4
        elif self.name in ['Dwarf', 'Crystal Dragon']:
            self.magic_resist = .2
        else:
            self.magic_resist = 0.

        if self.name == 'Gold Dragon':
            self.spell_immunity = 4
        elif self.name in ['Black Dragon', 'Magic Elemental']:
            self.spell_immunity = 5
        elif self.name in ['Green Dragon', 'Red Dragon', 'Azure Dragon']:
            self.spell_immunity = 3
        else:
            self.spell_immunity = 0

        # these can:
        self.reset_state()

    def reset_state(self):
        self.count = self.cap
        self.hp = self.true_hp
        self.hp_left = self.hp
        self.attack = self.true_attack
        self.defense = self.true_defense
        self.shots = self.unit.shots

        self.aged = -1
        self.poisoned = -1
        self.times_poisoned = 0
        self.cursed = 0
        self.weakened = 0
        self.diseased = 0

        self.petrified = 0
        self.blinded = 0
        self.paralyzed = 0
        self.stunned_from_retaliation = False

        self.rebirth_available = self.name == 'Phoenix' or False

    def take_dmg(self, dmg):
        if dmg < self.hp_left:
            self.hp_left -= dmg
        else:
            dmg -= self.hp_left
            num_killed, rem = my_divmod(dmg, self.hp)
            self.count -= num_killed + 1
            self.hp_left = self.hp - rem
            self.count = max(self.count, 0)
        if self.name == 'Phoenix' and not self.is_alive() \
                and self.rebirth_available:
            self.rebirth()

    def __calc_base_damage(self, other):
        real_dmg_max = self.dmg_min if self.cursed > 0 else self.dmg_max
        if self.count < 10:
            base_dmg = sum([randint(self.dmg_min, real_dmg_max)
                            for _ in range(int(self.count))])
        else:
            base_dmg = sum([randint(self.dmg_min, real_dmg_max)
                            for _ in range(10)]) * self.count // 10

        defense = other.defense
        if self.name == 'Behemoth':
            defense = int(.6 * defense)
        elif self.name == 'Ancient Behemoth':
            defense = int(.2 * defense)

        att_to_def = self.attack - defense
        base_dmg_reduction = 0.
        base_dmg_bonus = 0.
        if att_to_def > 0:
            base_dmg_bonus = min(.05 * att_to_def, 3.)
        else:
            base_dmg_reduction = min(.025 * -att_to_def, .7)

        return base_dmg, base_dmg_bonus, base_dmg_reduction

    # __pragma__('kwargs')

    def attack_melee(self, other, dmg_reductions=None, melee_penalty=False,
                     retaliation=False):
        dmg_bonus = 0.
        if dmg_reductions is None:
            dmg_reductions = []
        base_dmg, base_dmg_bonus, base_dmg_reduction = \
            self.__calc_base_damage(other)
        dmg_bonus += base_dmg_bonus
        dmg_reductions.append(base_dmg_reduction)

        if melee_penalty:
            dmg_reductions.append(.5)

        if self.name == 'Dread Knight' and random() < .2:
            dmg_bonus += 1.
        elif other.name in self.hates:
            dmg_bonus += .5
        elif other.name in self.opp_elem:
            dmg_bonus += 1.

        if self.name == 'Magic Elemental' and other.spell_immunity == 5:
            dmg_reductions.append(.5)
        elif self.name == 'Psychic Elemental' and (
                other.is_nonliving() or other.name in
                ['Giant', 'Titan', 'Black Dragon']):
            dmg_reductions.append(.5)

        damage = base_dmg * (1. + dmg_bonus)
        # fire shield looks at damage before reductions
        # damage dealt is at most 20% of total HP of Efreet stack
        fire_shield_damage = .2 * \
            min(damage, (other.count - 1) * other.hp + other.hp_left)

        for reduction in dmg_reductions:
            damage *= 1. - reduction

        damage = int(damage)
        other.take_dmg(damage)

        other.petrified = 0
        other.blinded = 0
        other.paralyzed = 0
        other.stunned_from_retaliation = False

        if (self.name == 'Vampire Lord' and
                not other.is_nonliving()):
            self.drain_life(damage)
        elif (self.name == 'Mighty Gorgon' and
                not other.is_nonliving()):
            self.death_stare(other)
        elif (self.name == 'Thunderbird' and
              other.spell_immunity < 2 and
              other.name not in ['Earth Elemental', 'Magma Elemental'] and
              random() < .2 and
              random() > other.magic_resist):
            self.thunderbolt(other)
        elif self.name == 'Rust Dragon':
            self.acid_breath(other)
        elif (self.name == 'Ghost Dragon' and
              not other.is_nonliving() and
              random() < .2):
            other.start_aging()
        elif (self.name == 'Wyvern Monarch' and
                other.times_poisoned < 5 and
                not other.is_nonliving() and
                random() < .2):
            other.start_poison()
        elif (self.name in ['Black Knight', 'Dread Knight', 'Mummy'] and
              other.spell_immunity < 1 and
              not other.is_undead() and
              other.name not in [
                  'Efreet', 'Efreet Sultan', 'Fire Elemental',
                  'Energy Elemental', 'Firebird', 'Phoenix'] and
              random() > other.magic_resist):
            if ((self.name == 'Mummy' and random() < .5) or
                    (self.name != 'Mummy' and random() < .2)):
                self.start_curse(other)
        elif (self.name == 'Dragon Fly' and
              other.spell_immunity < 2 and
              random() > other.magic_resist):
            self.start_weakness(other)
        elif (self.name == 'Zombie' and
              not other.is_nonliving() and
              random() < .2):
            self.start_disease(other)
        elif (self.name in ['Medusa', 'Medusa Queen', 'Basilisk',
                            'Greater Basilisk'] and
              other.spell_immunity == 0 and
              other.name not in ['Troglodyte', 'Infernal Troglodyte'] and
              random() < .2):
            self.start_petrification(other)
            other.stunned_from_retaliation = retaliation
        elif (self.name in ['Unicorn', 'War Unicorn'] and
              other.spell_immunity < 2 and
              not other.is_nonliving() and
              other.name not in [
                  'Troglodyte', 'Infernal Troglodyte', 'Giant', 'Titan',
                  'Efreet', 'Efreet Sultan', 'Firebird', 'Phoenix'] and
              random() < .2):
            self.start_blindness(other)
            other.stunned_from_retaliation = retaliation
        elif (self.name == 'Scorpicore' and
              other.name not in ['Gold Dragon', 'Black Dragon',
                                 'Magic Elemental'] and
              random() < .2):
            self.start_paralysis(other)
            other.stunned_from_retaliation = retaliation

        if (other.name == 'Efreet Sultan' and
            self.name not in [
                'Efreet', 'Efreet Sultan', 'Fire Elemental',
                'Energy Elemental', 'Firebird', 'Phoenix']):
            self.efreet_fire_shield(fire_shield_damage)

    # __pragma__('nokwargs')

    def attack_range(self, other, range_penalty):
        assert self.is_shooter() and self.shots > 0
        dmg_bonus = 0.
        base_dmg, base_dmg_bonus, base_dmg_reduction = \
            self.__calc_base_damage(other)
        dmg_bonus += base_dmg_bonus

        damage = base_dmg * (1. + dmg_bonus) * (1. - base_dmg_reduction)
        if range_penalty:
            damage /= 2.

        other.take_dmg(int(damage))
        self.shots -= 1

    def start_weakness(self, other):
        assert self.name == 'Dragon Fly'
        if self.speed > other.speed:
            other.weakened = 3
        elif self.speed < other.speed:
            other.weakened = 2
        else:
            other.weakened = randint(2, 3)
        other.attack = max(0, other.true_attack - 6)

    def weakness(self):
        assert self.weakened > 0
        self.weakened -= 1
        if self.weakened == 0:
            self.attack = self.true_attack

    def start_curse(self, other):
        assert self.name in ['Mummy', 'Black Knight', 'Dread Knight']
        if self.speed > other.speed:
            other.cursed = 3
        elif self.speed < other.speed:
            other.cursed = 2
        else:
            other.cursed = randint(2, 3)

    def curse(self):
        assert self.cursed > 0
        self.cursed -= 1

    def start_disease(self, other):
        assert self.name == 'Zombie'
        if self.speed > other.speed:
            other.diseased = 3
        elif self.speed < other.speed:
            other.diseased = 2
        else:
            other.diseased = randint(2, 3)
        other.attack = max(0, other.true_attack - 2)
        other.defense = max(0, other.true_defense - 2)

    def disease(self):
        assert self.diseased > 0
        self.diseased -= 1
        if self.diseased == 0:
            self.attack = self.true_attack
            self.defense = self.true_defense

    def start_petrification(self, other):
        assert self.name in ['Medusa', 'Medusa Queen', 'Basilisk',
                             'Greater Basilisk']
        if self.speed > other.speed:
            other.petrified = 3
        elif self.speed < other.speed:
            other.petrified = 2
        else:
            other.petrified = randint(2, 3)

    def petrification(self):
        assert self.petrified > 0
        self.petrified -= 1

    def start_blindness(self, other):
        assert self.name in ['Unicorn', 'War Unicorn']
        if self.speed > other.speed:
            other.blinded = 3
        elif self.speed < other.speed:
            other.blinded = 2
        else:
            other.blinded = randint(2, 3)

    def blindness(self):
        assert self.blinded > 0
        self.blinded -= 1

    def start_paralysis(self, other):
        assert self.name == 'Scorpicore'
        if self.speed > other.speed:
            other.paralyzed = 3
        elif self.speed < other.speed:
            other.paralyzed = 2
        else:
            other.paralyzed = randint(2, 3)

    def paralysis(self):
        assert self.paralyzed > 0
        self.paralyzed -= 1

    def start_aging(self):
        was_already_aged = self.aged > 0
        self.aged = 3 if self.speed < 14 else 2
        if not was_already_aged:
            hp_missing = self.hp - self.hp_left
            self.hp = (self.hp + 1) // 2
            self.hp_left = max(1, self.hp - hp_missing)

    def age(self):
        assert self.aged > 0
        self.aged -= 1
        if self.aged == 0:
            self.stop_aging()

    def stop_aging(self):
        assert self.aged == 0
        self.aged = -1
        hp_missing = self.hp - self.hp_left
        self.hp = self.true_hp
        self.hp_left = self.hp - hp_missing

    def start_poison(self):
        was_already_poisoned = self.poisoned >= 0
        self.poisoned = 2
        if not was_already_poisoned:
            self.times_poisoned += 1
            hp_missing = self.hp - self.hp_left
            self.hp = int(ceil(self.true_hp *
                               (1 - .1 * self.times_poisoned)))
            self.hp_left = max(1, self.hp - hp_missing)

    def poison(self):
        assert self.poisoned >= 0
        self.poisoned -= 1
        if self.times_poisoned < 5 and self.poisoned >= 0:
            self.times_poisoned += 1
            hp_missing = self.hp - self.hp_left
            self.hp = int(ceil(self.true_hp *
                               (1 - .1 * self.times_poisoned)))
            self.hp_left = max(1, self.hp - hp_missing)

    def drain_life(self, damage_dealt):
        assert self.name == 'Vampire Lord'
        if self.hp_left + damage_dealt <= self.hp:
            self.hp_left += damage_dealt
        else:
            damage_dealt -= self.hp - self.hp_left
            self.hp_left = self.hp
            res, rem = my_divmod(damage_dealt, self.hp)
            self.count = min(self.cap, self.count + res)
            if self.count < self.cap and rem:
                self.count += 1
                self.hp_left = rem

    def acid_breath(self, other):
        other.defense = max(0, other.defense - 3)
        if random() < .3:
            other.take_dmg(25 * self.count)

    def magic_dmg_resistance(self):
        if self.name == 'Stone Golem':
            return .5
        elif self.name == 'Iron Golem':
            return .75
        elif self.name == 'Gold Golem':
            return .85
        elif self.name == 'Diamond Golem':
            return .95
        return 0.

    def efreet_fire_shield(self, damage):
        damage *= (1. - self.magic_dmg_resistance())
        if self.name in ['Water Elemental', 'Ice Elemental']:
            damage *= 2
        self.take_dmg(int(damage))

    def thunderbolt(self, other):
        assert self.name == 'Thunderbird'
        damage = 10 * self.count
        damage *= (1 - other.magic_dmg_resistance())
        if self.name in ['Air Elemental', 'Storm Elemental']:
            damage *= 2
        other.take_dmg(int(damage))

    def death_stare(self, other):
        assert self.name == 'Mighty Gorgon' and not other.is_nonliving()
        to_death_stare = min(my_binomial(self.count, .1),
                             (self.count + 9) // 10)
        if to_death_stare:
            other.count = max(0, other.count - to_death_stare)
            other.hp_left = other.hp

    def rebirth(self):
        assert (self.name == 'Phoenix' and not self.is_alive() and
                self.rebirth_available)
        certain, rem = my_divmod(self.count, 5)
        to_rebirth = certain + (random() < .2*rem)
        self.count = to_rebirth
        self.rebirth_available = False

    def regenerate(self):
        assert self.name in ['Wight', 'Wraith', 'Troll']
        self.hp_left = self.hp

    def is_alive(self):
        return self.count > 0

    def is_shooter(self):
        return 'SHOOTING_ARMY' in self.attributes

    def strikes_twice(self):
        return 'const_two_attacks' in self.attributes and not self.is_shooter()

    def shoots_twice(self):
        return 'const_two_attacks' in self.attributes and self.is_shooter()

    def is_big(self):
        return 'DOUBLE_WIDE' in self.attributes

    def melee_penalty(self):
        return (self.is_shooter() and
                not 'const_no_melee_penalty' in self.attributes)

    def no_retaliation(self):
        return 'const_free_attack' in self.attributes

    def range_penalty(self):
        return self.is_shooter() and self.name != 'Sharpshooter'

    def is_elemental(self):
        return 'cusELEMENTAL' in self.attributes

    def is_undead(self):
        return 'IS_UNDEAD' in self.attributes

    def is_golem(self):
        return 'cusGOLEM' in self.attributes

    def is_nonliving(self):
        return self.is_elemental() or self.is_undead() or self.is_golem()

    def is_stunned(self):
        return bool(self.petrified or self.blinded or self.paralyzed)

    def advance_statuses(self):
        if self.aged > 0 and self.is_alive():
            self.age()
        elif self.poisoned >= 0 and self.is_alive():
            self.poison()
        elif self.cursed:
            self.curse()
        elif self.weakened:
            self.weakness()
        elif self.diseased:
            self.disease()
        elif self.petrified:
            self.petrification()
        elif self.blinded:
            self.blindness()
        elif self.paralyzed:
            self.paralysis()
