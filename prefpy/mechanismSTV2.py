import random
from .mechanism import Mechanism
from .preference import Preference
from .profile import Profile

class MechanismSTV2(Mechanism):
    def __init__(self):
        self.maximizeCandScore = True
        self.seatsAvailable = 1

    def getWinningQuota(self, profile):
        return (profile.numVoters / (self.seatsAvailable + 1)) + 1

    def convRankingToTuple(self, ranking):
        return tuple(tuple(ranking[k+1]) for k in range(0,len(ranking)))

    def getInitialCandMaps(self, profile):
        allCands = list(profile.candMap.keys())
        rankMaps = profile.getReverseRankMaps()
        rankMapCounts = profile.getPreferenceCounts()

        candScoreMap = {cand:0 for cand in allCands}
        candPreferenceMap = {cand:[] for cand in allCands}
        rankingCount = {self.convRankingToTuple(ranking):count \
                        for ranking,count in zip(rankMaps,rankMapCounts)}
        
        for ranking in rankingCount:
            candScoreMap[ranking[0][0]] += rankingCount[ranking]
            candPreferenceMap[ranking[0][0]].append(ranking)
        
        return candScoreMap, candPreferenceMap, rankingCount

    def getWinLoseCandidates(self, candScoreMap, winningQuota):
        winners, losers = set(), set()
        lowestScore = winningQuota
        for cand,score in candScoreMap.items():
            if score >= winningQuota:
                winners.add(cand)
            elif score < lowestScore:
                lowestScore = score
                losers = set([cand])
            elif score == lowestScore:
                losers.add(cand)
        return winners, losers

    def getCandScoresMap(self, profile):
        winningQuota = self.getWinningQuota(profile)
        numCandidates = profile.numCands
        candScoreMap, candPreferenceMap, rankingCount = self.getInitialCandMaps(profile)
        print(candScoreMap)
        print(candPreferenceMap)
        print(rankingCount)

        winners, losers = self.getWinLoseCandidates(candScoreMap, winningQuota)
        while(len(winners) < self.seatsAvailable and len(losers) + 2 < numCandidates):
            pass
        return candScoreMap
