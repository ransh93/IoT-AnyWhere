# MUDIS
MUD Inspection System tool that compares the network behavior of devices, based on their formal description in the MUD file
MUDIS tool introduces comparison and generalization features, allowing users to investigate MUD files differences.

Motivated by the impact of location on the MUD, we built
the MUDIS tool, which gets two MUDs as input and performs
two tasks:

* MUD Comparison - calculates the MUD similarity measure. It then examines the differences between two MUD
files and highlights similar entries. This allows us to drill
down and gain insights about the origin of the differences.
* MUD Generalization - creates a generalized MUD that
can serve as a white-list for the network behavior of both
MUDs (represent two locations in our experiments), this
is done by covering both input MUDs.
