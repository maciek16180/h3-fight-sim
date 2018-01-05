# HoMM III monster duel simulator

**Current results of all simulations are in scores/scores.csv**

Python 3 is required.

Files:

`CRTRAITS.TXT` - creatures data. Cleaned up and slightly modified version, the format is a bit different than the original file from the game.

`report.html`, `report.ipynb` - full description of what this thing does

`combat.py`, `unit.py` - the actual code

`calculate_scores.py` - script for scores calculation. You need numpy and pandas for that.

`fight_sim.py` - essential functions, in one simple file. I created it to make the conversion to Javascript easier (http://www.transcrypt.org/).

`misc/` - crap

`scores/` - simulation results
  
Refer to `report.html` or `report.ipynb` for details. I have an browser demo for all of this, but it's not live yet.
