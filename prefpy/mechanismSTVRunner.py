import sys
from prefpy import io
from prefpy import mechanismSTV
from .preference import Preference
from .profile import Profile

def electionFileToProfile(file):
    inputFile = open(sys.argv[1], 'r')
    candMap, rankMaps, rankMapsCounts, numVoters = io.read_election_file(inputFile)

    preferences = []
    # ranking: [dict<cand,pos in order>, freq of ranking]
    for ranking in zip(rankMaps,rankMapsCounts):
        cands = list(ranking[0].keys())
        wmg = {}
        for i in range(len(cands)):
            for j in range(i+1, len(cands)):
                cand1, cand2 = cands[i], cands[j]
                if cand1 not in wmg:
                    wmg[cand1] = {}
                if cand2 not in wmg:
                    wmg[cand2] = {}
                if ranking[0][cand1] < ranking[0][cand2]:
                    wmg[cand1][cand2] = 1
                    wmg[cand2][cand1] = -1
                elif ranking[0][cand1] > ranking[0][cand2]:
                    wmg[cand1][cand2] = -1
                    wmg[cand2][cand1] = 1
                else:
                    wmg[cand1][cand2] = 0
                    wmg[cand2][cand1] = 0
        preferences.append(Preference(wmg, ranking[1]))
    return Profile(candMap, preferences)
            
profile = electionFileToProfile(sys.argv[1])
stv = mechanismSTV.MechanismSTV()
print(stv.getWinners(profile))
print(stv.getCandScoresMap(profile))


# stvMech = mechanism.mechanismSTV()
# scores = stvMech.getCandScoresMap(
