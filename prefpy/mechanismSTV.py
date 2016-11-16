import random
from .mechanism import Mechanism
from .preference import Preference
from .profile import Profile

class MechanismSTV(Mechanism):
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

        candScoreMap, candPreferenceMap = {},{}
        for cand in allCands:
            candScoreMap[cand] = 0
            candPreferenceMap[cand] = []
        rankingOffset = {}
        rankingCount = {}
        
        for ranking,count in zip(rankMaps,rankMapCounts):
            tupleRanking = self.convRankingToTuple(ranking)
            rankingCount[tupleRanking] = count
            candScoreMap[tupleRanking[0][0]] += rankingCount[tupleRanking]
            candPreferenceMap[tupleRanking[0][0]].append(tupleRanking)
            if tupleRanking not in rankingOffset:
                rankingOffset[tupleRanking] = 0
        
        return candScoreMap, candPreferenceMap, rankingCount, rankingOffset

    def getWinLoseCandidates(self, candScoreMap, winningQuota):
        winners, losers = set(), set()
        lowestScore = winningQuota
        for cand,score in candScoreMap.items():
            if score >= winningQuota:
                winners.add(cand)
            elif score < lowestScore and score != 0:
                lowestScore = score
                losers = set([cand])
            elif score == lowestScore:
                losers.add(cand)
        return winners, losers

    def breakLoserTie(self, losers, deltaCandScores, profile):
        curCandScores = self.getInitialCandMaps(profile)[0]
        curRound = 0
        while(len(losers)>1 and curRound < len(deltaCandScores)):
            lowestScore = -1
            newLosers = set()
            for loser in losers:
                score = curCandScores[loser]
                if score < lowestScore or lowestScore == -1:
                    lowestScore = score
                    newLosers = {loser}
                elif score == lowestScore:
                    newLosers.add(loser)
            losers = newLosers
            
            for cand in deltaCandScores[curRound]:
                curCandScores[cand] += deltaCandScores[curRound][cand]
        return random.choice(list(losers))
        
    def reallocLoserVotes(self, candScoreMap, candPreferenceMap, rankingCount, rankingOffset,
                             loser, noMoreVotesHere, deltaCandScores):
        deltaCandScore = {}
        for ranking in candPreferenceMap[loser]:
            curOffset = rankingOffset[ranking]
            oldCand = ranking[curOffset][0]
            while(curOffset < len(ranking) and ranking[curOffset][0] in noMoreVotesHere):
                curOffset += 1
            rankingOffset[ranking] = curOffset
            if curOffset < len(ranking):
                newCand = ranking[curOffset][0]
                candPreferenceMap[newCand].append(ranking)
                candScoreMap[newCand] += rankingCount[ranking]
                if newCand not in deltaCandScore:
                    deltaCandScore[newCand] = 0
                deltaCandScore[newCand] += rankingCount[ranking]
            candScoreMap[oldCand] -= rankingCount[ranking]
            if oldCand not in deltaCandScore:
                deltaCandScore[oldCand] = 0
            deltaCandScore[oldCand] -= rankingCount[ranking]
        candPreferenceMap[loser] = []
        deltaCandScores.append(deltaCandScore)
        return


    def getCandScoresMap(self, profile):
        winningQuota = self.getWinningQuota(profile)
        numCandidates = profile.numCands
        candScoreMap, candPreferenceMap, rankingCount, rankingOffset = \
            self.getInitialCandMaps(profile)
        roundNum = 0

        deltaCandScores = []
        victoriousCands, eliminatedCands = set(), set()
        while(len(victoriousCands) < self.seatsAvailable and \
              len(victoriousCands) + len(eliminatedCands) + 1 < numCandidates):
            winners, losers = self.getWinLoseCandidates(candScoreMap, winningQuota)
            loser = self.breakLoserTie(losers, deltaCandScores, profile)
            victoriousCands = victoriousCands | winners
            eliminatedCands = eliminatedCands | {loser}
            print('[round %d]'%roundNum,'prefMap:-',candPreferenceMap)
            print('[round %d]'%roundNum,'scores:-',candScoreMap,'loser:-',loser,
                  'w&l:-',victoriousCands, eliminatedCands)
            self.reallocLoserVotes(candScoreMap, candPreferenceMap, rankingCount, rankingOffset,                                   loser, (victoriousCands | eliminatedCands), deltaCandScores)
            roundNum+= 1
        return candScoreMap
