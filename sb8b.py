#!/usr/bin/env python

import pandas as pa
import argparse as ap
import numpy as np
import itertools as it

INNINGS = 7
POSITION_ORDERING = np.asarray(['SS', 'LC', 'RC', 'SB', 'LF', 'FB', 'RF', 'TB','CA'])  # import thang and use

parser = ap.ArgumentParser("Generate Softball Rosters")
parser.add_argument('file', help="Today's roster file to load")
parser.add_argument('-ve', '--verbose', type=int, help="Set verbosity level \
		for decision process.")
parser.add_argument('-pr', '--printweights', action='store_true', help="Print out\
		 rankings for current roster.")
parser.add_argument('-al', '--algorithm', default="pos_weight_chooser", help="The \
		selection algorithm to use.")
args = parser.parse_args()

def pos_weight_chooser(fielded_players, i, pos):
	lucky_ix = fielded_players[pos].argmax()
	lineup[i] = fielded_players.ix[lucky_ix]['PLAYER']
	return lucky_ix

def pos_rank_chooser(fielded_players, i, pos):
    lucky_ix = fielded_players[pos].sort(('SEASONS','SKILL'),
            inplace=False).argmax()
    lineup[i] = fielded_players.ix[lucky_ix]['PLAYER']
    return lucky_ix

def skill_chooser(fielded_players, i):
	lucky_ix = fielded_players['SKILL'].argmin()
	lineup[i] = fielded_players.ix[lucky_ix]['PLAYER']
	return lucky_ix

#Load the data set
weights = pa.read_csv('player_weights.csv')
players = np.loadtxt(args.file)
weights = weights.iloc[players]
if args.printweights:
	print(weights)
	quit()

#Decide if we'll have 8 or 9 positions based on the number of female players
fp = weights[weights['SEX']=='F']
mp = weights[weights['SEX']=='M']
num_fp = len(fp.index)
num_mp = len(mp.index)

assert num_fp >= 2

if num_fp >= 3:
	positions = 9.0
else:
	positions = 8.0
	#Get rid of RV
	POSITION_ORDERING = np.delete(POSITION_ORDERING,-2)
lineup = [None]*int(positions)

#Decide how many of each gender will play in each inning
playing_ratio = positions/(num_fp+num_mp)
if num_fp >= 3:
	num_fpp = np.floor(playing_ratio*num_fp)
	num_mpp = np.ceil(playing_ratio*num_mp)
else:
	num_fpp = 2
	num_mpp = positions-num_fpp
assert(num_fpp+num_mpp==positions)

#Shuffle player numbers within genders
fp.index = np.random.permutation(fp.index)
mp.index = np.random.permutation(mp.index)

#Generate the benched mask
if num_mp != num_mpp:
	m_mask = [False if i%max(2,np.floor(num_mp/(num_mp-num_mpp)))==(num_mp%2) else True for i in
		range(num_mp)]
else:
	m_mask = [True]*num_mp
if num_fp != num_fpp:
	f_mask = [False if i%np.floor(num_fp/(num_fp-num_fpp))==(num_fp%2) else True for i in
		range(num_fp)]
else:
	f_mask = [True]*num_fp

if args.verbose > 0:
	print(num_mpp)
	print(m_mask)
	print(num_fpp)
	print(f_mask)

assert sum(m_mask) == num_mpp
assert sum(f_mask) == num_fpp

#Let's make a lineup for every inning
csv_output = []
for inning in range(INNINGS):
	fem_idx = fp.index[f_mask]
	mal_idx = mp.index[m_mask]
	#Let's greedily choose the best player for each position in order of
	#the positions importance. This is a terrible solution, but we'll make
	#a better one later if it's necessary.
	inning_players = weights.ix[np.append(fem_idx,mal_idx)]
	if args.verbose > 0:
		print(inning_players)
	for i, pos in enumerate(POSITION_ORDERING):
		if (args.verbose > 2):
			print("Choosing %s"%pos)
			print(inning_players.sort(pos))
		#Find our winner, trying to account for seasons and skill
		if args.algorithm == 'pos_rank_chooser':
			lucky_ix = pos_rank_chooser(inning_players, i, pos)
		elif args.algorithm == 'pos_weight_chooser':
			lucky_ix = pos_weight_chooser(inning_players, i, pos)
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
	csv_output.append(dict(zip(POSITION_ORDERING, lineup)))
	#Let's make sure the same players don't sit on the bench all game
	m_mask = np.roll(m_mask,1)
	f_mask = np.roll(f_mask,1)


output_f = open("lineup_output.csv", "w+")
output_f.write(",".join(["Position", "Inning 1","Inning 2","Inning 3","Inning 4","Inning 5","Inning 6","Inning 7", "\n"]))
for p in POSITION_ORDERING:
	players = [p]
	for l in csv_output:
		players.append(l[p])
	print players
	output_f.write(",".join(players) + "\n")
output_f.close()






