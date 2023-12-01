import json

with open('example-argumentation-framework.json', 'r') as file:
    data = json.load(file)

for key, value in data.items():
    print(f"Key: {key}, Value: {value}")

""" The opponent can only choose arguments that attack another argument previously outputted by the proponent. 
The attacked arguments can be from the previous round, but also from an earlier round.
The proponent always has to answer with an argument that attacks the argument that the opponent selected in the 
directly preceding round.
The opponent is not allowed to use the same argument twice. (The proponent however can.)
The game is over and a winner selected based on the following conditions:

If the opponent uses an argument previously used by the proponent, then the opponent wins (because he has shown 
that the proponent contradicts itself).
If the proponent uses an argument previously used by the opponent, then the opponent wins (for similar reasons 
as in the previous point).
If the proponent is unable to make a move, then the opponent wins.
If the opponent has no choices left, then the proponent wins. """

proponent = player1
opponent = player2

