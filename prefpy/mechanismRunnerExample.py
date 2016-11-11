"""
Author: Kevin J. Hwang
"""
import io
import math
import itertools
from .profile import Profile
from .preference import Preference
# import prefpy.mechanism
from prefpy import mechanism
import prefpy.mov
import prefpy.utilityFunction
import prefpy.mechanismMcmc
import prefpy.mechanismMcmcSampleGenerator

# # First, let's generate a two-dimensional dictionary to represent the ranking {cand1 > cand2 > cand3}.
# wmgMap1 = dict()
# wmgMap1[1] = dict()
# wmgMap1[2] = dict()
# wmgMap1[3] = dict()

# # We associate every pair of candidates, cand1 and cand2, with 1 if cand1 is ranked above cand2, -1
# # if cand1 is ranked below cand2, and 0 if cand1 and cand2 are tied.
# wmgMap1[1][2] = -1
# wmgMap1[1][3] = -1
# wmgMap1[2][1] = 1
# wmgMap1[2][3] = 1
# wmgMap1[3][1] = 1
# wmgMap1[3][2] = -1

# # Next, let's generate a two-dimensional dictionary represent the ranking {cand2 > cand1 > cand3}.
# wmgMap2 = dict()
# wmgMap2[1] = dict()
# wmgMap2[2] = dict()
# wmgMap2[3] = dict()
# wmgMap2[1][2] = -1
# wmgMap2[1][3] = 1
# wmgMap2[2][1] = 1
# wmgMap2[2][3] = 1
# wmgMap2[3][1] = -1
# wmgMap2[3][2] = -1

# # We can generate Preference objects from these dictionaries, by calling the Preference constructor.

# # Let's say that the ranking {cand1 > cand2 > cand3} occurs only once. Then, we can call the 
# # Preference constructor with just the dictionary as our constructor.
# preference1 = Preference(wmgMap1)

# # Let's say that the ranking {cand2 > cand1 > cand3} occurs three times. Then, we can include an
# # optional int argument that represents the number of times the ranking occurs.
# preference2 = Preference(wmgMap2, 3)

# # Let's put these into a list.
# preferences = []
# preferences.append(preference1)
# preferences.append(preference2)

# # Let's set up a dictionary that associates integer representations of our candidates with their names.
# candMap = dict()
# candMap[1] = "john"
# candMap[2] = "jane"
# candMap[3] = "jill"

# # Now that we have this candidate mapping and a list of Preference objects, we can construct a 
# # Profile object.
# profile = Profile(candMap, preferences)

# # Let's print the output of some of the Profile object's methods.
# print(profile.getRankMaps())
# print(profile.getWmg())
# print(profile.getPreferenceCounts())
# print(profile.getElecType())
# print(profile.getReverseRankMaps())
# print(profile.getOrderVectors())

# Now let's see which candidate would win an election were we to use the Plurality rule.

wmgR1 = dict()
wmgR1[1] = dict()
wmgR1[2] = dict()
wmgR1[3] = dict()
wmgR1[4] = dict()

wmgR2 = dict()
wmgR2[1] = dict()
wmgR2[2] = dict()
wmgR2[3] = dict()
wmgR2[4] = dict()

wmgR3 = dict()
wmgR3[1] = dict()
wmgR3[2] = dict()
wmgR3[3] = dict()
wmgR3[4] = dict()

wmgR4 = dict()
wmgR4[1] = dict()
wmgR4[2] = dict()
wmgR4[3] = dict()
wmgR4[4] = dict()

wmgR1[1][2] = 1
wmgR1[1][3] = 1
wmgR1[1][4] = 1
wmgR1[2][1] = -1
wmgR1[2][3] = 1
wmgR1[2][4] = 1
wmgR1[3][1] = -1
wmgR1[3][2] = -1
wmgR1[3][4] = 1
wmgR1[4][1] = -1
wmgR1[4][2] = -1
wmgR1[4][3] = -1

wmgR2[1][2] = 1
wmgR2[1][3] = 1
wmgR2[1][4] = -1
wmgR2[2][1] = -1
wmgR2[2][3] = 1
wmgR2[2][4] = -1
wmgR2[3][1] = -1
wmgR2[3][2] = -1
wmgR2[3][4] = -1
wmgR2[4][1] = 1
wmgR2[4][2] = 1
wmgR2[4][3] = 1

wmgR3[1][2] = 1
wmgR3[1][3] = -1
wmgR3[1][4] = -1
wmgR3[2][1] = -1
wmgR3[2][3] = -1
wmgR3[2][4] = -1
wmgR3[3][1] = 1
wmgR3[3][2] = 1
wmgR3[3][4] = 1
wmgR3[4][1] = 1
wmgR3[4][2] = 1
wmgR3[4][3] = -1

wmgR4[1][2] = -1
wmgR4[1][3] = -1
wmgR4[1][4] = -1
wmgR4[2][1] = 1
wmgR4[2][3] = 1
wmgR4[2][4] = 1
wmgR4[3][1] = 1
wmgR4[3][2] = -1
wmgR4[3][4] = 1
wmgR4[4][1] = 1
wmgR4[4][2] = -1
wmgR4[4][3] = -1

preference1 = Preference(wmgR1,10)
preference2 = Preference(wmgR2,7)
preference3 = Preference(wmgR3,6)
preference4 = Preference(wmgR4,1)
preferences = [preference1, preference2, preference3, preference4]

candMap = {1:'a',2:'b',3:'c',4:'d'}

profile = Profile(candMap,preferences)

print(profile.getRankMaps())
print(profile.getWmg())
print(profile.getPreferenceCounts())
print(profile.getElecType())
print(profile.getReverseRankMaps())
print(profile.getOrderVectors())

# First, we construct a Mechanism object
# mechanism = mechanism.MechanismPlurality()
mechanism = mechanism.MechanismSTV()

print("READY TO BREAKK!!!!!!")

# Let's print the ouputs of some of the Mechanism object's methods.
print(mechanism.getWinners(profile))
print(mechanism.getCandScoresMap(profile))


# print(mechanism.getMov(profile))

# # We can also call margin of victory functions directly without constructing a mechanism object.
# # Let's print the margin of victory using Borda rule.
# print(mov.movBorda(profile))

# # Now we are going to use MCMC sampling to approximate the Bayesian loss of each candiate.

# # First, let's create a zero-one loss function.
# zeroOneLoss = utilityFunction.UtilityFunctionMallowsZeroOne()

# # Then, we will create a sample generation mechanism.
# sampleGen = mechanismMcmcSampleGenerator.MechanismMcmcSampleGeneratorMallowsJumpingDistribution(profile.getWmg(True), 0.9)

# # Now, lets see the results of both MCMC approximation and brute force.
# mcmc = mechanismMcmc.MechanismMcmcMallows(0.9, zeroOneLoss, 1, 10000, 0, sampleGen)
# print(mcmc.getWinners(profile))
# print(mcmc.getWinnersBruteForce(profile))
