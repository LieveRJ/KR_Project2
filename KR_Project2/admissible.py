import json
import sys

def is_admissible(label):
    propagate(label)
    
    # if label is admissible then return true.
    if all(label[x] != 'mustOut' for x in label):
        return True

    # Check if label is hopeless.
    for x in label:
        if label[x] == 'mustOut' and all(label[y] in {'out', 'mustOut', 'und'} for y in [attacker for (attacker, attacked) in framework if attacked == x]):
            return False

    # label1 ← label
    label1 = label.copy()

    # select some x ∈ {y | label(y) = mustOut} − with label(x) = blank.
    #x = [y for y in label if label[y] == 'mustOut' and label1[x] == 'blank']
    # should work if not hopeless
    x = [attacker for (attacker, attacked) in framework if label[attacked] == 'mustOut' and label[attacker] == 'blank'][0]
    if x:
        in_trans(label1, x[0])

        # if isAdmissible(label1)=true then return true.
        if is_admissible(label1):
            return True

        und_trans(label, x)

        # isAdmissible(label)=true then return true
        if is_admissible(label):
            return True
        else:
            return False

def propagate(label):
    while True:
        """Checks for an argument with label 'blank'.
        Select some x with label(x) = blank such that for all 
        y ∈ {x}− label(y) ∈ {out,mustOut}"""
        candidates = [x for x in label if label[x] == 'blank']

        for x in candidates:
            # Checks conditions for all y ∈ {x}− label(y) ∈ {out, mustOut}
            if all(label[y] in {'out', 'mustOut'} for y in [attacker for (attacker, attacked) in framework if attacked == x]):
                in_trans(label, x)
                break #the for loop, the while continues
        else:
            """If there is no x with label(x) = blank such that for 
            all y ∈ {x} − label(y) ∈ {out,mustOut} then halt."""
            return

def in_trans(label, x):
    label[x] = 'in'

    # For each y ∈ {x}+ do label(y) ← out.
    for y in [y for (attacker, y) in framework if attacker == x]:
        label[y] = 'out'

    # For each y ∈ {x}- with label(y) != out do label(y) ← mustOut.
    for y in [attacker for (attacker, attacked) in framework if attacked == x]:
        if label[y] != 'out':
            label[y] = 'mustOut'
    return

def und_trans(label, x):
    if label[x] == 'blank':
        label[x] = 'und'

# credulous accepted arguments for preferred semantics.
def credulous_accepted_arguments(label):
    if is_admissible(label):
        return True
    else:
        return False


def main(arg, args, framework):
    """
    if the query argument s is self-attacking, then we conclude with arg being
    inadmissible
    """
    if (arg, arg) in framework:
        print('No')
        return False

    """
    Setting all args to blank except the self attacking args which are set to 
    undecided.
    """
    label = {}
    for x in args:
        label[x] = 'blank'

    for x in label:
        if (x, x) in framework:
            label[x] = 'und'

    in_trans(label, arg)

    credulous_accepted = credulous_accepted_arguments(label)
    if credulous_accepted:
        print('Yes')
    else:
        print('No')


# args = set(['a', 'b', 'c', 'd', 'e'])
# framework = [('a','b'),('b','a'), ('b','c'), ('c','d'),('d','e'),('e','c')]

with open(sys.argv[1], 'r') as file:
    data = json.load(file)

for key, value in data.items():
        print(f"Key: {key}, Value: {value}")

args = set(data["Arguments"].keys())
framework = [(rel[0], rel[1]) for rel in data["Attack Relations"]]

arg = input(f"Enter an argument to check for credulous acceptance: ")

main(arg, args, framework)
