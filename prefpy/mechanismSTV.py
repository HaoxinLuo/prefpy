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

        rankingOffset = [1 for i in rankMapCounts]
        roundNum = 1

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
                    nextRankingOffset = self.reallocLoserVotes(rankMaps, rankMapCounts, rankingOffset, newEliminatedCands)
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
        """
        Returns all candidates who have won by passing the winning quota and all who have tied for lowest score.

        :ivar list<dict<int, list<int>>> rankMaps: List of rankings in dict form, where dict maps placement to list of candidates.
        :ivar list<int> rankMapCounts: Count of votes in corresponding entry of rankMaps
        :ivar list<int> rankingOffset: Index of top remaining candidate in corresponding entry of rankMaps
        :ivar int winningQuota: minimum value needed to be winner
        """
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

    def reallocLoserVotes(self, rankMaps, rankMapCounts, rankingOffset, eliminatedCands):
        """
        Makes new rankingOffset based on who has been eliminated.

        :ivar list<dict<int, list<int>>> rankMaps: List of rankings in dict form, where dict maps placement to list of candidates.
        :ivar list<int> rankMapCounts: Count of votes in corresponding entry of rankMaps
        :ivar list<int> rankingOffset: Index of top remaining candidate in corresponding entry of rankMaps
        :ivar set<int> eliminatedCandidates: Set of candidates that have been eliminated
        """
        newRankingOffset = [i for i in rankingOffset]
        i = 0;
        while i < len(rankMaps):
            ranking = rankMaps[i]
            offset = newRankingOffset[i]
            cands = ranking[offset]
            nonLoserCands = []
            for cand in cands:
                if cand not in eliminatedCands:
                    nonLoserCands.append(cand)
            if len(nonLoserCands) == 0:
                newRankingOffset[i] = offset + 1
            else:
                i += 1
        return newRankingOffset
