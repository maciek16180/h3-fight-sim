# to jeszcze nie działa tak jak trzeba, są problemy z synchronizacją i seedami,
# więc tymczasowo wywaliłem z notebooka

def fight_multiproc(stackA, stackB, num_iter, num_proc):
    
    def units_order(s1, s2):
        temp = sorted([s1,s2], key=lambda x: x.speed, reverse=True)
        if s1.speed == s2.speed and np.random.rand() < .5:
            return reversed(temp)
        return temp    
    
    def melee_hit(current, other):
        current.attack_melee(other, melee_penalty=current.melee_penalty())
        
        if other.is_alive() and not current.no_retaliation():
            other.attack_melee(current, melee_penalty=other.melee_penalty())
            
        if current.is_alive() and current.strikes_twice():
            current.attack_melee(other)
        return other, current
    
    def range_hit(current, other, apply_penalty):
        penalty = current.range_penalty() if apply_penalty else False
        current.attack_range(other, range_penalty=penalty)
        if current.shoots_twice() and current.shots > 0:
            current.attack_range(other, range_penalty=penalty)
        return other, current
    
    def fight_to_death(current, other):
        while current.is_alive() and other.is_alive():
            current, other = melee_hit(current, other)
        return current, other
    
    def walker_vs_shooter(walker, shooter):            
        to_walk = starting_dist - 1
        first_move = to_walk % walker.speed
        if first_move == 0:
            first_move = walker.speed
        avoid_by_move = to_walk - first_move > 10
        avoid_by_wait = False
            
        if walker.speed < shooter.speed:
            num_shots = to_walk / walker.speed + (to_walk % walker.speed > 0)
        elif walker.speed > shooter.speed:
            num_shots = to_walk / walker.speed - (to_walk % walker.speed == 0)
            avoid_by_wait = True
        else:
            if np.random.rand() < .5:
                num_shots = to_walk / walker.speed + (to_walk % walker.speed > 0)
            else:
                num_shots = to_walk / walker.speed - (to_walk % walker.speed == 0)
                    
        num_full_shots = max(0, num_shots - avoid_by_move - avoid_by_wait)
        num_half_shots = num_shots - num_full_shots
            
        for j in xrange(num_half_shots):
            range_hit(shooter, walker, apply_penalty=True)
        for j in xrange(num_full_shots):
            range_hit(shooter, walker, apply_penalty=False)
            
        current, other = walker, shooter
        return fight_to_death(current, other)
    
    starting_dist = 14
    if stackA.is_big():
        starting_dist -= 1
    if stackB.is_big():
        starting_dist -= 1
        
    procs = []
    wins = [None]*num_proc
    for i in xrange(num_proc):
        stackA_wins = Value('i', 0)
        stackB_wins = Value('i', 0)
        wins[i] = [stackA_wins, stackB_wins]
        
    def proc_fun(wins_A, wins_B):
        wins = {stackA.name : np.array([0,0]),
                stackB.name : np.array([0,0])}
        
        for it in xrange(num_iter / num_proc):
            current, other = units_order(copy(stackA), copy(stackB))

            if not current.is_shooter() and not other.is_shooter():
                current, other = fight_to_death(current, other)

            elif current.is_shooter() and other.is_shooter():
                while current.is_alive() and current.shots > 0:
                    current, other = range_hit(current, other, apply_penalty=True)
                if current.is_alive():
                    if other.shots == 0:
                        current, other = units_order(current, other)
                        current, other = fight_to_death(current, other)
                    else:
                        current, other = walker_vs_shooter(walker=current, shooter=other)
                        
            else:           
                shooter = current if current.is_shooter() else other
                walker = current if not current.is_shooter() else other
                current, other = walker_vs_shooter(walker=walker, shooter=shooter)

            winner = current if current.is_alive() else other
            if winner.name == stackA.name:
                wins_A.value += 1
            else:
                wins_B.value += 1
    
        
    for i in xrange(num_proc):
        p = Process(target=proc_fun, args=wins[i])
        procs.append(p)
        p.start()
    
    for i in xrange(num_proc):        
        p.join()
    
    wins = {stackA.name : sum(x[0].value for x in wins),
            stackB.name : sum(x[1].value for x in wins)}
    
    return wins