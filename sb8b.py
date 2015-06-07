#!/usr/bin/env python

import pandas as pa
import argparse as ap
import numpy as np

INNINGS = 7
POSITION_ORDERING = np.asarray(
        ['SS', 'SB', 'LF', 'FB', 'TB', 'CF', 'RF', 'RV','CA'])

parser = ap.ArgumentParser("Generate Softball Rosters")
parser.add_argument('file', help="Today's roster file to load")
args = parser.parse_args()

#Load the data set
ranks = pa.read_csv('ranks.csv')
players = np.loadtxt(args.file)
ranks = ranks.iloc[players]

#Decide if we'll have 8 or 9 positions based on the number of female players
fp = ranks[ranks['SEX']=='F']
mp = ranks[ranks['SEX']=='M']
num_fp = len(fp.index)
num_mp = len(mp.index)

if num_fp >= 3:
    positions = 9.0
else:
    positions = 8.0
    #Get rid of RV
    POSITION_ORDERING = np.delete(POSITION_ORDERING,-2)
lineup = [None]*int(positions)

#Decide how many of each gender will play in each inning
playing_ratio = positions/(num_fp+num_mp)
num_fpp = np.ceil(playing_ratio*num_fp)
num_mpp = np.floor(playing_ratio*num_mp)
assert(num_fpp+num_mpp==positions)

#Shuffle player numbers within genders
fp.index = np.random.permutation(fp.index)
mp.index = np.random.permutation(mp.index)

#Generate the benched mask
m_mask = [True]*num_mpp+[False]*(num_mp-num_mpp)
f_mask = [True]*num_fpp+[False]*(num_fp-num_fpp)

#Let's make a lineup for every inning
for inning in range(INNINGS):
    fem_idx = fp.index[f_mask]
    mal_idx = mp.index[m_mask]
    #Let's greedily choose the best player for each position in order of
    #the positions importance. This is a terrible solution, but we'll make
    #a better one later if it's necessary.
    inning_players = ranks.ix[np.append(fem_idx,mal_idx)]
    for i, pos in enumerate(POSITION_ORDERING):
        if (args.verbose):
            print("Choosing %s"%pos)
            print(inning_players.sort(pos))
        lucky_ix = inning_players[pos].argmin()
        lineup[i] = inning_players.ix[lucky_ix]['PLAYER']
        if args.verbose: print("Chose %s")%lineup[i]
        inning_players = inning_players.drop(lucky_ix)
    #Make it print prettier
    lineout = pa.Series(dict(zip(lineup,POSITION_ORDERING)))
    print(lineout)
    #Let's make sure the same players don't sit on the bench all game
    m_mask = np.roll(m_mask,1)
    f_mask = np.roll(f_mask,1)




