The format for all election data is (each element on a new line):
* Number of Candidates
* 1, Candidate Name
* 2, Candidate Name
* ...
* Number of Voters, Sum of Vote Count, Number of Unique Orders
* count, preference list. (12,1,2,{3,4}). A strict ordering is indicated by a comma (,) and elements that are indifferent are grouped with a ({ }).
* count, preference list. (12,1,2,3,4). A strict ordering is indicated by a comma (,) and elements that are indifferent are grouped with a ({ }).
* ...

[The above is based on preflib's format. Visit them for more info](http://www.preflib.org/data/format.php#election-data)

Demo usage code is in [mechanismSTVRunner.py](./blob/stv_refactor/prefpy/mechanismSTVRunner.py)
Sample input are in [prefpy/tests](./prefpy/tree/stv_refactor/tests)
