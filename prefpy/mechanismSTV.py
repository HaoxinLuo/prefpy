import random
from .mechanism import Mechanism
from .preference import Preference
from .profile import Profile

class MechanismSTV(Mechanism):
    """
    The Single Transferable Vote Mechanism
    """

    def __init__(self):
        self.maximizeCandScore = True
        self.seatsAvailable = 1

    def getWinningQuota(self, profile):
        """
        Returns an integer that is the minimum number of votes needed to 
        definitively win using Droop quota
        
        :ivar Profile profile: A Profile object that represents an election profile.
        """

        return (profile.numVoters / (self.seatsAvailable + 1)) + 1

    def convRankingToTuple(self, ranking):
        """
        Returns a tuple of tuples that represents the ranking where the first inner
        tuple contains candidates that are ranked number 1 in original ranking and
        so on for each following inner tuple. e.g. {{4,}, {1,}, {3,}, {2,}} is a 
        ranking where candidates are ranked in the order 4 > 1 > 3 > 2.
        
        :rtype tuple<tuple<int>>: will referred to as tupleRanking type.
        
        :ivar dict<int,list<int>> ranking: A mapping of ranking position number to 
            list of candidates ranked at that position. e.g. {1:[2,3]} means 
            candidates 2 and 3 are both ranked number 1 in the ranking.
        """

        return tuple(tuple(ranking[k+1]) for k in range(0,len(ranking)))

    def getInitialCandMaps(self, profile):
        """
        Returns a multi-part representation of the election profile referenced by 
        profile.

        .. note:: tupleRanking is equal to tuple<tuple<int>> as returned by 
            convRankingToTuple.
        :rtype dict<int,int> candScoreMap: A mapping of each candidate to their 
            score, which starts out as the number of rankings with this candidate
            ranked first, or 0 if no rankings start out supporting this canddiate.
        :rtype dict<int,list<tupleRanking>> candPreferenceMap: A mapping of each
            candidate to a list all rankings, represented as tuple of tuples, that
            contribute to their score, which starts out empty.
        :rtype dict<tupleRanking, int> rankingCount: A mapping of rankings in tuple
            form to their corresponding count as given by profile.
        :rtype dict<tupleRanking, int> rankingOffset: A mapping of rankings in tuple
            form to the their own offset, which shows which candidate the ranking is
            currently supporting. Each ranking starts off supporting its first ranked
            candidate.

        :ivar Profile profile: A Profile object that represents an election profile.
        """

        allCands = list(profile.candMap.keys())
        rankMaps = profile.getReverseRankMaps()
        rankMapCounts = profile.getPreferenceCounts()

        # initialize all cands to have 0 score and [] supporting rankings
        candScoreMap, candPreferenceMap = {},{}
        for cand in allCands:
            candScoreMap[cand] = 0
            candPreferenceMap[cand] = []
        rankingOffset = {}
        rankingCount = {}
        
        for ranking,count in zip(rankMaps,rankMapCounts):
            tupleRanking = self.convRankingToTuple(ranking)
            rankingCount[tupleRanking] = count
            # find top ranked candidate and add to his score and supporint rankings
            candScoreMap[tupleRanking[0][0]] += rankingCount[tupleRanking]
            candPreferenceMap[tupleRanking[0][0]].append(tupleRanking)
            if tupleRanking not in rankingOffset:
                rankingOffset[tupleRanking] = 0
        
        return candScoreMap, candPreferenceMap, rankingCount, rankingOffset

    def getWinLoseCandidates(self, candScoreMap, winningQuota):
        """
        Returns candidates who gained at least winningQuota worth of votes and
        those with the least positive number of votes.

        :rtype set<int> winners: The set of candidates who has winningQuota worth
            of votes this round.
        :rtype set<int> losers: The set of candidates who has the least positive
            amount of votes.

        :ivar dict<int, int> candScoremap: A mapping of candidates to their score.
        :ivar int winningQuota: the amount of votes needed to win a seat
        """
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
        """
        Returns one candidate to be eliminated.

        :rtype int loser: the candidate to be eliminated this round.

        :ivar set<int> losers: A set of candidates who are tied for being eliminated.
        :ivar list<dict<int,int>> deltaCandScores: A list of the score change for 
            each candidate each round. Candidates whose score did not change for a 
            round would not appear in the dictionary for that round.
        :ivar Profile profile: A Profile object that represents an election profile.
        """

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
        
    def reallocLoserVotes(self, candScoreMap, candPreferenceMap, rankingCount, 
                          rankingOffset, loser, noMoreVotesHere, deltaCandScores):
        """
        Modifies rankingOffset so that the rankings supporting the just eliminated
        candidate will support the next non-winning-or-eliminated candidate, or
        no one if offset reaches the end of the ranking. Also updates candScoreMap,
        candPreferenceMap, and deltaCandScores to reflect the new scores, and
        supporting rankings due to one candidate being eliminated. A ranking that
        supports no candidate is removed from all lists in candPreferenceMap, but
        not from rankingOffset, and rankingCount.

        .. note:: tupleRanking is equal to tuple<tuple<int>> as returned by 
            convRankingToTuple.
        :ivar dict<int,int> candScoreMap: A mapping of candidates to their score.
        :ivar dict<int,list<tupleRanking>> candPreferenceMap: A mapping of each
            candidate to a list of supporting rankings in tuple form
        :ivar dict<tupleRanking, int> rankingCount: A mapping of rankings in tuple
            form to their corresponding count as given by profile.
        :ivar dict<tupleRanking, int> rankingOffset: A mapping of rankings in tuple
            form to the their own offset to the currently supproted candidate.
        """
        deltaCandScore = {}
        for ranking in candPreferenceMap[loser]:
            curOffset = rankingOffset[ranking]
            oldCand = ranking[curOffset][0]
            while(curOffset < len(ranking) and \
                  ranking[curOffset][0] in noMoreVotesHere):
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


    def getCandScoresMap(self, profile):
        """
        Returns a dictionary that associates integer representations of each 
        candidate with their frequency as top ranked candidate or 0 if they were
        eliminated.

        :ivar Profile profile: A Profile object that represents an election profile.
        """

        # Currently, we expect the profile to contain an ordering over candidates
        # with no ties.
        elecType = profile.getElecType()
        if elecType != "soc" and elecType != "soi":
            print("ERROR: unsupported election type")
            exit()

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
            self.reallocLoserVotes(candScoreMap, candPreferenceMap, rankingCount, 
                                   rankingOffset,loser, 
                                   victoriousCands | eliminatedCands, deltaCandScores)
            roundNum+= 1
        return candScoreMap
