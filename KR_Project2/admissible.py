import json


def is_admissible(label):
    propagate(label)
    
    # if label is admissible then return true.
    if all(label[x] != 'mustOut' for x in label):
        print('inside admissible')
        return True
    
    # Check if label is hopeless.
    for x in label:
        if all(label[y] in {'out, mustOut', 'und'} for y in [attacker for (attacker, attacked) in framework if attacked == x]):
            return False

    # label1 ← label
    label1 = label.copy()

    # select some x ∈ {y | label(y) = mustOut} − with label(x) = blank.
    x = [y for y in label if label[y] == 'mustOut' and label1[x] == 'blank']

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
        else:
            """If there is no x with label(x) = blank such that for 
            all y ∈ {x} − label(y) ∈ {out,mustOut} then halt."""
            break

def in_trans(label, x):
    label[x] = 'in'

    # For each y ∈ {x}+ do label(y) ← out.
    for y in [y for (attacker, y) in framework if attacker == x]:
        label[y] = 'out'

    # For each y ∈ {x}- with label(y) != out do label(y) ← mustOut.
    for y in [attacker for (attacker, attacked) in framework if attacked == x]:
        if label[y] != 'out':
            label[y] = 'mustOut'

def und_trans(label, x):
    if label[x] == 'blank':
        label[x] = 'und'    

def main(arg, args, framework):
    """
    if the query argument s is self-attacking, then we conclude with arg being 
    inadmissible
    """
    if (arg, arg) in framework:
        print(f"{arg} inadmissible")
        return

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
    
    if is_admissible(label):
        print(f"{arg} admissible")
    else:
        print(f"{arg} inadmissible")

#args = set(['a', 'b', 'c', 'd', 'e'])
#framework = [('a','b'),('c','b'), ('c','d'), ('d','c'),('d','e'),('e','e')]

#framework_file = input(f'Enter framework file: \n')

framework_file = 'examples/example1.json'
arg = input(f"Enter an argument: \n")

with open(framework_file, 'r') as file:
    data = json.load(file)

args = set(data['Arguments'].keys())
framework = data['Attack Relations']
main(arg, args, framework)
