import random
from pprint import pprint
from .mechanism import Mechanism
from .preference import Preference
from .profile import Profile

class MechanismSTV(Mechanism):
    """
    The Single Transferable Vote Mechanism. This class is the parent class for
    several mechanisms and cannot be constructed directly. All child classes are
    expected to implement getScoringVector() method.
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

    def getCandMaps(self, profile, rankMaps, rankMapCounts):
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

        # initialize all cands to have 0 score and [] supporting rankings
        allCands = list(profile.candMap.keys())
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

    def getInitialRankMaps(self, profile):
        """
        Returns a multi-part representation of the election profile referenced by
        profile.

        :ivar Profile profile: A Profile object that represents an election profile.
        """
        allCands = list(profile.candMap.keys())
        rankMaps = profile.getReverseRankMaps()
        rankMapCounts = profile.getPreferenceCounts()
        return rankMaps, rankMapCounts

    def getCandScoresMap(self, profile):
        """
        Returns a dictionary that associates integer representations of each
        candidate with their frequency as top ranked candidate or 0 if they were
        eliminated.

        This function assumes that breakLoserTie(self, losers, deltaCandScores, profile)
        is implemented for the child MechanismSTV class.

        :ivar Profile profile: A Profile object that represents an election profile.
        """

        # Currently, we expect the profile to contain an ordering over candidates
        # with no ties.
        elecType = profile.getElecType()
        if elecType != "soc" and elecType != "soi":
            print("ERROR: unsupported election type")
            exit()

        winningQuota = self.getWinningQuota(profile)
        print("Winning quota is %d votes" % winningQuota)
        numCandidates = profile.numCands
        rankMaps, rankMapCounts = self.getInitialRankMaps(profile)
        # candScoreMap, candPreferenceMap, rankingCount, rankingOffset = self.getCandMaps(profile, rankMaps, rankMapCounts)
        rankingOffset = [1 for i in rankMapCounts]
        roundNum = 0

        victoriousCands = set()
        eliminatedCandsList = [set()]
        rankingOffsets = [rankingOffset]
        while roundNum < numCandidates:
            print("\n\nRound %d\t\t" % roundNum)
            newRankingOffsets = []
            newEliminatedCandsList = []
            for i in range(len(rankingOffsets)):
                rankingOffset = rankingOffsets[i]
                winners, losers = self.getWinLoseCandidates(rankMaps, rankMapCounts, rankingOffset, winningQuota)
                victoriousCands = victoriousCands | winners
                print("\tWinners: %s" % victoriousCands)
                print("\tEliminated so far: %s" % eliminatedCandsList[i])

                if len(losers) > 1:
                    print("\t\t%s are tied" % losers)
                else:
                    print("\t\t%s is loser" % losers)
                for loser in losers:
                    newEliminatedCands = eliminatedCandsList[i] | {loser}
                    print("\t\tCands eliminated: %s" % newEliminatedCands)
                    nextRankingOffset = self.reallocLoserVotes(rankMaps, rankMapCounts, rankingOffset, loser, newEliminatedCands)
                    newEliminatedCandsList.append(newEliminatedCands)
                    newRankingOffsets.append(nextRankingOffset)
            rankingOffsets = newRankingOffsets
            eliminatedCandsList = newEliminatedCandsList
            roundNum+= 1

        candScoreMap = {}
        for eliminatedCands in eliminatedCandsList:
            for cand in eliminatedCands:
                candScoreMap[cand] = 0
        for cand in victoriousCands:
            candScoreMap[cand] = 1
        return candScoreMap

    def getWinLoseCandidates(self, rankMaps, rankMapCounts, rankingOffset, winningQuota):
        candScores = {}
        # calculate scores
        for i in range(len(rankMaps)):
            ranking = rankMaps[i]
            offset = rankingOffset[i]
            cands = ranking[offset]
            for cand in cands:
                if cand not in candScores:
                    candScores[cand] = 0
                candScores[cand] += rankMapCounts[i]
        print(candScores)
        # find winners and losers
        winners = set()
        losers = set()
        minScore = min(candScores.values())
        for cand in candScores:
            score = candScores[cand]
            if score >= winningQuota:
                winners.add(cand)
            if score == minScore:
                losers.add(cand)

        return winners, losers

    def reallocLoserVotes(self, rankMaps, rankMapCounts, rankingOffset, loser, eliminatedCands):
        newRankingOffset = [i for i in rankingOffset]
        for i in range(len(rankMaps)):
            ranking = rankMaps[i]
            offset = rankingOffset[i]
            cands = ranking[offset]
            nonLoserCands = []
            for cand in cands:
                if cand not in eliminatedCands:
                    nonLoserCands.append(cand)
            if len(nonLoserCands) == 0:
                newRankingOffset[i] = offset + 1
        return newRankingOffset
