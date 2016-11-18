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
            
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 -m prefpy.mechanismSTVRunner tests/<any test file>\n",
              ''' input file follows the election data format described at (http://www.preflib.org/data/format.php#election-data):
    * <number of candidates>
    * <candidate number; e.g. 1>,<candidate name; e.g. apple>
    * ... //until all candidates listed
    * <total number of voters>,<sum of vote count;usually same as total number of votes>,<number of unique rankings>
    * <number of votes with this ranking>,<ranking;e.g. 1,2,3,4>
    * ... //until all unique rankings are listed''')
        exit()
    profile = electionFileToProfile(sys.argv[1])

    stv = mechanismSTV.MechanismSTVForward()
    print("\n\n")
    print("Using STV with forward tie breaking")
    print(stv.getWinners(profile))
    print("\n" + "=" * 80)
    stv = mechanismSTV.MechanismSTVBackward()
    print("Using STV with backward tie breaking")
    print(stv.getWinners(profile))
    print("\n" + "=" * 80)
    stv = mechanismSTV.MechanismSTVBorda()
    print("Using STV with Borda tie breaking")
    print(stv.getWinners(profile))
    print("\n" + "=" * 80)
    stv = mechanismSTV.MechanismSTVCoombs()
    print("Using STV with Coombs tie breaking")
    print(stv.getWinners(profile))
    print("\n" + "=" * 80)
    print("\n\n")
