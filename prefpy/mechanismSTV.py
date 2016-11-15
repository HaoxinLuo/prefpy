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

    def getCandScoresMap(self, profile):
        """
        Returns a dictionary that associates integer representations of each candidate with their 
        frequency as top ranked candidate or 0 if they were eliminated.

        :ivar Profile profile: A Profile object that represents an election profile.
        """
        
        # Currently, we expect the profile to contain complete ordering over candidates with no 
        # ties.
        elecType = profile.getElecType()
        if elecType != "soc" and elecType != "soi":
            print("ERROR: unsupported election type")
            exit()

        winningQuota = self.getWinningQuota(profile)

        candScoresMap = [{cand:0 for cand in profile.candMap}]

        rankMaps = profile.getReverseRankMaps()
        rankMapCounts = profile.getPreferenceCounts()
        rankOffsets = [1 for x in rankMaps]

        # ranoff for getting too little votes
        eliminatedCandidates = set()
        # already has winning num of votes
        victoriousCandidates = set()
        roundNum = 0
        while(len(victoriousCandidates)!=self.seatsAvailable and 
              profile.numCands - len(victoriousCandidates) - len(eliminatedCandidates) > \
                  self.seatsAvailable):
            print("win&losers",roundNum,victoriousCandidates, eliminatedCandidates);
            if roundNum >= len(candScoresMap):
                candScoresMap.append({cand:0 for cand in profile.candMap \
                                      if cand not in eliminatedCandidates})
            #stores plurality scoring in candScoresMap
            for rankIndex in range(len(rankMaps)):
                rankMap = rankMaps[rankIndex]
                cand = rankMap[rankOffsets[rankIndex]][0]
                # print(rankMap,cand,rankOffsets,rankIndex,"~~~")
                candScoresMap[roundNum][cand] += rankMapCounts[rankIndex]

            lowestCands = self.lowestCandidates(profile, candScoresMap[roundNum], victoriousCandidates)

            print("plurality",roundNum,eliminatedCandidates,candScoresMap[roundNum],lowestCands)

            loser = self.forwardTieBreak(lowestCands, candScoresMap)
            eliminatedCandidates.add(loser)

            print("eliminates",roundNum,loser)
            
            # increment rankOffsets to skip over those cands already eliminated
            for rankIndex in range(len(rankMaps)):
                rankMap = rankMaps[rankIndex]
                # while current cand in rankMap is eliminated or victorious, go to next cand
                while((rankMap[rankOffsets[rankIndex]][0] in eliminatedCandidates or
                      rankMap[rankOffsets[rankIndex]][0] in victoriousCandidates) and
                      rankOffsets[rankIndex] < len(rankMap)):
                    rankOffsets[rankIndex] += 1
            
            roundNum += 1
        
        #put eliminated candidates back in with 0 votes???
        for cand in eliminatedCandidates:
            if cand not in candScoresMap[-1]:
                candScoresMap[-1][cand] = 0
        return candScoresMap[-1]

    def getWinningQuota(self, profile):
        """
        Returns minimum number of votes needed to definitively win, using Drope quota

        :ivar Profile profile: A Profile object that represents an election profile.
        """
        return (profile.numVoters / (self.seatsAvailable + 1)) + 1

    def lowestCandidates(self, profile, candScores, victoriousCandidates):
        """
        Returns list of candidates with lowest plurality votes
        Updates victoriousCandidates if needed

        :ivar Profile profile: A Profile object that represents an election profile.
        :ivar dict candScores: dictionary mapping candidate to score in current round
        :ivar set victoriousCandidates: set of candidates that are automatically victorious
        """
        winningQuota = self.getWinningQuota(profile)
        lowestScore = winningQuota
        lowestCands = []
        # go through all the cand and their scores
        for cand,score in candScores.items():
            # if cand got enough votes
            if score >= winningQuota:
                victoriousCandidates.add(cand)
            # if cand has new lowest num of votes
            elif score < lowestScore:
                lowestScore = score
                lowestCands = [cand]
            # if cand has the same lowest num of votes
            elif score == lowestScore:
                lowestCands.append(cand)
        return lowestCands

    def forwardTieBreak(self, lowestCands, candScoresMap):
        """
        Runs forward tie breaking, putting eliminated candidates in eliminatedCandidates

        :ivar list lowestCands list of tied lowest-ranking candidates
        :ivar dict candScoresMap maps rounds to map of candidates to scores
        :ivar set eliminatedCandidates
        """

        for roundCandScoreMap in candScoresMap[:-1]:
            # no loser tie to break
            if len(lowestCands) < 2:
                break;
            lowestScore = roundCandScoreMap[lowestCands[0]]
            evenLowerCands = []
            # for each cand tied for last
            for cand in lowestCands:
                # find their previous score and compare
                score = roundCandScoreMap[cand]
                if score < lowestScore:
                    lowestScore = score
                    evenLowerCands = [cand]
                    # if cand has the same lowest num of votes
                elif score == lowestScore:
                    evenLowerCands.append(cand)
            # swap them to maintain lowestCands
            lowestCands = evenLowerCands

        # if still not tie broken, randomly select loser
        return random.choice(lowestCands)
