#!/usr/bin/env python

import pandas as pa
import argparse as ap
import numpy as np
import itertools as it

INNINGS = 7
POSITION_ORDERING = np.asarray(
        ['SS', 'SB', 'LF', 'FB', 'TB', 'CF', 'RF', 'RV','CA'])

parser = ap.ArgumentParser("Generate Softball Rosters")
parser.add_argument('file', help="Today's roster file to load")
parser.add_argument('-ve', '--verbose', type=int, help="Set verbosity level \
        for decision process.")
parser.add_argument('-pr', '--printranks', action='store_true', help="Print out\
         rankings for current roster.")
parser.add_argument('-al', '--algorithm', default="skill_chooser", help="The \
        selection algorithm to use.")
args = parser.parse_args()

def pos_rank_chooser(fielded_players, i, pos):
    lucky_ix = fielded_players[pos].sort(('SEASONS','SKILL'),inplace=False).argmin()
    lineup[i] = fielded_players.ix[lucky_ix]['PLAYER']
    return lucky_ix

def skill_chooser(fielded_players, i):
    lucky_ix = fielded_players['SKILL'].argmin()
    lineup[i] = fielded_players.ix[lucky_ix]['PLAYER']
    return lucky_ix

#Load the data set
ranks = pa.read_csv('ranks.csv')
players = np.loadtxt(args.file)
ranks = ranks.iloc[players]
if args.printranks:
    print(ranks)
    quit()

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
if num_mp != num_mpp:
    m_mask = [False if i%np.floor(num_mp/(num_mp-num_mpp))==0 else True for i in
        range(num_mp)]
else:
    m_mask = [True]*num_mp
if num_fp != num_fpp:
    f_mask = [False if i%np.floor(num_fp/(num_fp-num_fpp))==0 else True for i in
        range(num_fp)]
else:
    f_mask = [True]*num_fp

assert sum(m_mask) == num_mpp
assert sum(f_mask) == num_fpp

#Let's make a lineup for every inning
for inning in range(INNINGS):
    fem_idx = fp.index[f_mask]
    mal_idx = mp.index[m_mask]
    #Let's greedily choose the best player for each position in order of
    #the positions importance. This is a terrible solution, but we'll make
    #a better one later if it's necessary.
    inning_players = ranks.ix[np.append(fem_idx,mal_idx)]
    if args.verbose > 0:
        print(inning_players)
    for i, pos in enumerate(POSITION_ORDERING):
        if (args.verbose > 2):
            print("Choosing %s"%pos)
            print(inning_players.sort(pos))
        #Find our winner, trying to account for seasons and skill
        if args.algorithm == 'pos_rank_chooser':
            lucky_ix = pos_rank_chooser(inning_players, i, pos)
        elif args.algorithm == 'skill_chooser':
            lucky_ix = skill_chooser(inning_players, i)
        else:
            print("Error: No valid algorithm chosen.")
        if args.verbose > 1: print("Chose %s\n")%lineup[i]
        inning_players = inning_players.drop(lucky_ix)
    #Make it print prettier
    lineout = pa.Series(dict(zip(lineup,POSITION_ORDERING)))
    print("\nInning %d:"%(inning+1))
    print(lineout)
    #Let's make sure the same players don't sit on the bench all game
    m_mask = np.roll(m_mask,1)
    f_mask = np.roll(f_mask,1)




