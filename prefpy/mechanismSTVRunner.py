import sys
from prefpy import io
from prefpy import mechanism

inputFile = open(sys.argv[1], 'r')
candMap, rankMaps, rankMapsCounts, numVoters = io.read_election_file(inputFile)

io.pp_profile_toscreen(candMap, rankMaps, rankMapsCounts)

#io.pp_result_toscreen(candMap, scores)
