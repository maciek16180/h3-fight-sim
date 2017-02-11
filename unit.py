#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd


data = pd.read_csv('CRTRAITS.TXT', sep=',', encoding='utf-8')
data.Attributes.values[data.Attributes.values == u'0'] = ''

crap = ['Plural', 'Wood', 'Mercury', 'Ore', 'Sulfur', 'Crystal', 'Gems', 'Gold', 
        'Ability Text', 'Growth', 'Horde Growth', 'GuardsLow', 'GuardsHigh', 'Spells']
data.drop(crap, axis=1, inplace=True)


keywords = {'DOUBLE_WIDE', 
            'SHOOTING_ARMY', 
            'const_free_attack', 
            'const_jousting',
            'const_no_melee_penalty',
            'const_two_attacks',
            'IS_UNDEAD',
            'cusELEMENTAL',
            'cusGOLEM'}

haters = {(u'Anioł', u'Arcydiabeł'),
          (u'Anioł', u'Diabeł'),
          (u'Archanioł', u'Arcydiabeł'),
          (u'Archanioł', u'Diabeł'),
          (u'Arcydiabeł', u'Anioł'),
          (u'Arcydiabeł', u'Archanioł'),
          (u'Czarny smok', u'Gigant'),
          (u'Czarny smok', u'Tytan'),
          (u'Diabeł', u'Anioł'),
          (u'Diabeł', u'Archanioł'),
          (u'Dżinn', u'Ifryt'),
          (u'Dżinn', u'Sułtański ifryt'),
          (u'Ifryt', u'Dżinn'),
          (u'Ifryt', u'Wielki dżinn'),
          (u'Sułtański ifryt', u'Dżinn'),
          (u'Sułtański ifryt', u'Wielki dżinn'),
          (u'Tytan', u'Czarny smok'),
          (u'Wielki dżinn', u'Ifryt'),
          (u'Wielki dżinn', u'Sułtański ifryt')}

elementals = {(u'Żywiołak burzy', u'Żywiołak magmy'),
              (u'Żywiołak burzy', u'Żywiołak ziemi'),
              (u'Żywiołak energii', u'Żywiołak lodu'),
              (u'Żywiołak energii', u'Żywiołak wody'),
              (u'Żywiołak lodu', u'Żywiołak energii'),
              (u'Żywiołak lodu', u'Żywiołak ognia'),
              (u'Żywiołak magmy', u'Żywiołak burzy'),
              (u'Żywiołak magmy', u'Żywiołak powietrza'),
              (u'Żywiołak ognia', u'Żywiołak lodu'),
              (u'Żywiołak ognia', u'Żywiołak wody'),
              (u'Żywiołak powietrza', u'Żywiołak magmy'),
              (u'Żywiołak powietrza', u'Żywiołak ziemi'),
              (u'Żywiołak wody', u'Żywiołak energii'),
              (u'Żywiołak wody', u'Żywiołak ognia'),
              (u'Żywiołak ziemi', u'Żywiołak burzy'),
              (u'Żywiołak ziemi', u'Żywiołak powietrza')}


def make_unit(name):
    return unit_type(*data.values[data.Singular.values == name][0])


class unit_type(object):
    def __init__(self, name, fightv, aiv, hp, spd, att, df, dmlow, dmhi, shots, abi):
        self.name = name
        self.fight_value = fightv
        self.ai_value = aiv
        self.hp = hp
        self.speed = spd
        self.attack = att
        self.defense = df
        self.dmg_min = dmlow
        self.dmg_max = dmhi
        self.shots = shots
        self.attributes = {x for x in abi.split(' | ') if x in keywords}
        self.hates = [v for (k,v) in haters if k == self.name]
        self.opp_elem = [v for (k,v) in elementals if k == self.name]

        
class stack(object):
    def __init__(self, unit, count):
        self.count = count
        self.name = unit.name
        
        self.hp = unit.hp
        self.hp_left = self.hp
        self.true_max_hp = self.hp
        
        self.speed = unit.speed
        self.attack = unit.attack
        self.true_attack = self.attack
        self.defense = unit.defense
        self.dmg_min = unit.dmg_min
        self.dmg_max = unit.dmg_max
        self.shots = unit.shots
        self.attributes = unit.attributes      
        self.fight_value = unit.fight_value
        self.ai_value = unit.ai_value
        self.hates = unit.hates
        self.opp_elem = unit.opp_elem
        self.aged = -1
        self.poisoned = -1
        self.times_poisoned = 0
        self.cursed = 0
        self.weakened = 0
        
        self.cap = self.count
        self.rebirth_available = self.name == u'Feniks' or False
        self.magic_resist = 0.
        if self.name == u'Krasnoludzki wojownik':
            self.magic_resist == .4
        elif self.name in [u'Krasnolud', u'Kryształowy smok']:
            self.magic_resist = .2
        
        
    def take_dmg(self, dmg):
        if dmg < self.hp_left:
            self.hp_left -= dmg
        else:
            dmg -= self.hp_left
            num_killed, rem = divmod(dmg, self.hp)
            self.count -= num_killed + 1
            self.hp_left = self.hp - rem
            self.count = max(self.count, 0)
        if self.name == u'Feniks' and not self.is_alive() and self.rebirth_available:
            self.rebirth()
            
            
    def __calc_base_damage(self, other):
        real_dmg_max = self.dmg_min if self.cursed > 0 else self.dmg_max
        if self.count < 10:
            base_dmg = sum(np.random.randint(self.dmg_min, real_dmg_max+1, 
                                             size=self.count))
        else:
            base_dmg = sum(np.random.randint(self.dmg_min, real_dmg_max+1, 
                                             size=10)) * self.count / 10
        
        defense = other.defense
        if self.name == u'Behemot':
            defense = int(.6 * defense)
        elif self.name == u'Starożytny behemot':
            defense = int(.2 * defense)
        
        att_to_def = self.attack - defense
        base_dmg_reduction = 0.
        base_dmg_bonus = 0.
        if att_to_def > 0:
            base_dmg_bonus = min(.05 * att_to_def, 3.)
        else:
            base_dmg_reduction = min(.025 * -att_to_def, .7)
            
        return base_dmg, base_dmg_bonus, base_dmg_reduction
    
            
    def attack_melee(self, other, dmg_bonus=0., melee_penalty=False):
        base_dmg, base_dmg_bonus, base_dmg_reduction = self.__calc_base_damage(other)
        dmg_bonus += base_dmg_bonus
        dmg_reductions = [base_dmg_reduction]
        
        if melee_penalty:
            dmg_reductions.append(.5)
            
        if self.name == u'Upiorny rycerz' and np.random.rand() < .2:
            dmg_bonus += 1.
        elif other.name in self.hates:
            dmg_bonus += .5
        elif other.name in self.opp_elem:
            dmg_bonus += 1.
            
        if self.name == u'Żywiołak magii' and other.spell_immunity() == 5:
            dmg_reductions.append(.5)
        elif self.name == u'Żywiołak umysłu' and (other.is_nonliving() or other.name in \
                                                  [u'Gigant', u'Tytan', u'Czarny smok']):
            dmg_reductions.append(.5)

        damage = base_dmg * (1. + dmg_bonus)
        # tarcza ognia bierze pod uwagę obrażenia przed redukcjami,
        # obrażenia zadane to najwyżej 20% życia oddziału ifrytów
        fire_shield_damage = .2 * min(damage, (other.count - 1) * other.hp + other.hp_left)
        for reduction in dmg_reductions:
            damage *= 1. - reduction
        
        damage = int(damage)
        other.take_dmg(damage)
        
        if self.name == u'Wampirzy lord' and not other.is_nonliving():
            self.drain_life(damage)
        elif self.name == u'Wielka gorgona' and not other.is_nonliving():
            self.death_stare(other)
        elif self.name == u'Ptak gromu' and other.name not in [u'Żywiołak ziemi', u'Żywiołak magmy'] and \
             np.random.rand() < .2 and other.spell_immunity() < 2 and np.random.rand() > other.magic_resist:
            self.thunderbolt(other)
        elif self.name == u'Rdzawy smok':
            self.acid_breath(other)
        elif self.name == u'Upiorny smok' and not other.is_nonliving() and np.random.rand() < .2:
            other.start_aging()
        elif self.name == u'Wiwerna królewska' and not other.is_nonliving() and \
             np.random.rand() < .2 and other.times_poisoned < 5:
            other.start_poison()
        elif self.name in [u'Czarny rycerz', u'Upiorny rycerz', u'Mumia'] and not other.is_undead() and \
             other.spell_immunity < 1 and np.random.rand() > other.magic_resist and \
             other.name not in [u'Ifryt', u'Sułtański ifryt', u'Żywiołak ognia', 
                                u'Żywiołak energii', u'Ognisty ptak', u'Feniks']:
            if (self.name == u'Mumia' and np.random.rand() < .5) or \
               (self.name != u'Mumia' and np.random.rand() < .2):
                self.start_curse(other)
        elif self.name == u'Smocza ważka' and other.spell_immunity < 2 and np.random.rand() > other.magic_resist:
            self.start_weakness(other)
            
        if other.name == u'Sułtański ifryt' and self.name not in [u'Ifryt', u'Sułtański ifryt',
                                                                  u'Żywiołak ognia', u'Żywiołak energii',
                                                                  u'Ognisty ptak', u'Feniks']:
            self.efreet_fire_shield(fire_shield_damage)
        
        
    def attack_range(self, other, dmg_bonus=0., range_penalty=False):
        assert self.is_shooter() and self.shots > 0
        base_dmg, base_dmg_bonus, base_dmg_reduction = self.__calc_base_damage(other)
        dmg_bonus += base_dmg_bonus
            
        damage = base_dmg * (1. + dmg_bonus) * (1. - base_dmg_reduction)
        if range_penalty:
            damage /= 2.
            
        other.take_dmg(int(damage))
        self.shots -= 1
        
        
    def start_weakness(self, other):
        assert self.name == u'Smocza ważka' and other.weakened == 0
        if self.speed > other.speed:
            other.weakened = 3
        elif self.speed < other.speed:
            other.weakened = 2
        else:
            other.weakened = np.random.randint(2,4)
        other.attack = max(0, other.attack - 6)
    
    def weakness(self):
        assert self.weakened > 0
        self.weakened -= 1
        if self.weakened == 0:
            self.attack = self.true_attack
        
        
    def start_curse(self, other):
        assert self.name in [u'Mumia', u'Czarny rycerz', u'Upiorny rycerz']
        if self.speed > other.speed:
            other.cursed = 3
        elif self.speed < other.speed:
            other.cursed = 2
        else:
            other.cursed = np.random.randint(2,4)
            
            
    def curse(self):
        assert self.cursed > 0
        self.cursed -= 1
        
        
    def start_aging(self):
        was_already_aged = self.aged > 0
        self.aged = 3 if self.speed < 14 else 2
        if not was_already_aged:
            hp_missing = self.hp - self.hp_left
            self.hp = (self.hp + 1) / 2
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
        self.hp = self.true_max_hp
        self.hp_left = self.hp - hp_missing
        
        
    def start_poison(self):
        was_already_poisoned = self.poisoned >= 0
        self.poisoned = 2
        if not was_already_poisoned:
            self.times_poisoned += 1
            hp_missing = self.hp - self.hp_left
            self.hp = int(np.ceil(self.true_max_hp * (1 - .1 * self.times_poisoned)))
            self.hp_left = max(1, self.hp - hp_missing)
        
        
    def poison(self):
        assert self.poisoned >= 0
        self.poisoned -= 1
        if self.times_poisoned < 5 and self.poisoned >= 0:
            self.times_poisoned += 1
            hp_missing = self.hp - self.hp_left
            self.hp = int(np.ceil(self.true_max_hp * (1 - .1 * self.times_poisoned)))
            self.hp_left = max(1, self.hp - hp_missing)        
        
        
    def drain_life(self, damage_dealt):
        assert self.name == u'Wampirzy lord'
        if self.hp_left + damage_dealt <= self.hp:
            self.hp_left += damage_dealt
        else:
            damage_dealt -= self.hp - self.hp_left
            self.hp_left = self.hp
            res, rem = divmod(damage_dealt, self.hp)
            self.count = min(self.cap, self.count + res)
            if self.count < self.cap and rem:
                self.count += 1
                self.hp_left = rem
                
                
    def acid_breath(self, other):
        other.defense = max(0, other.defense - 3)
        if np.random.rand() < .3:
            other.take_dmg(25 * self.count)
                
                
    def magic_dmg_resistance(self):
        if self.name == u'Kamienny golem':
            return .5
        elif self.name == u'Żelazny golem':
            return .75
        elif self.name == u'Złoty golem':
            return .85
        elif self.name == u'Diamentowy golem':
            return .95
        return 0.
    
    
    def spell_immunity(self):
        if self.name == u'Złoty smok':
            return 4
        elif self.name in [u'Czarny smok', u'Żywiołak magii']:
            return 5
        elif self.name in [u'Zielony smok', u'Czerwony smok', u'Błękitny smok']:
            return 3
        return 0
    
                
    def efreet_fire_shield(self, damage):
        damage *= (1. - self.magic_dmg_resistance())
        if self.name in [u'Żywiołak wody', u'Żywiołak lodu']:
            damage *= 2
        self.take_dmg(int(damage))
        
    def thunderbolt(self, other):
        assert self.name == u'Ptak gromu'
        damage = 10 * self.count
        damage *= (1 - other.magic_dmg_resistance())
        if self.name in [u'Żywiołak powietrza', u'Żywiołak burzy']:
            damage *= 2
        other.take_dmg(int(damage))
                
            
    def death_stare(self, other):
        assert self.name == u'Wielka gorgona' and not other.is_nonliving()
        to_death_stare = min(np.random.binomial(n=self.count, p=.1), (self.count + 9) / 10)
        other.count = max(0, other.count - to_death_stare)
        
        
    def rebirth(self):
        assert self.name == u'Feniks' and not self.is_alive() and self.rebirth_available
        certain, rem = divmod(self.count, 5)
        to_rebirth = certain + (np.random.rand() < .2*rem)
        self.count = to_rebirth
        self.rebirth_available = False
        
        
    def regenerate(self):
        assert self.name in [u'Zjawa', u'Upiór', u'Troll']
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
        return self.is_shooter() and not 'const_no_melee_penalty' in self.attributes
    
    
    def no_retaliation(self):
        return 'const_free_attack' in self.attributes
    
    
    def range_penalty(self):
        return self.is_shooter() and self.name != 'Strzelec'
    
    
    def is_elemental(self):
        return 'cusELEMENTAL' in self.attributes
    
    
    def is_undead(self):
        return 'IS_UNDEAD' in self.attributes
    
    
    def is_golem(self):
        return 'cusGOLEM' in self.attributes
    
    
    def is_nonliving(self):
        return self.is_elemental() or self.is_undead() or self.is_golem()
    