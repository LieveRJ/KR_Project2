import json
import networkx as nx
import tkinter as tk
import matplotlib
import matplotlib.pyplot as plt
import random
import sys

matplotlib.use('TkAgg')
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure

import os


def dfs(fw, inargs, outargs, last, prop):
    if prop:
        #cannot pick outargs
        options = set(fw.predecessors(last)).difference(outargs)
        for opt in options:
            # print(f'\t prop checks {opt}')
            hope, answers = dfs(fw, inargs.union({opt}), outargs, opt, False)
            if hope:
                return True, opt

        return False, None
    else:
        options = set()
        #can attack any previous args
        for defender in inargs:
            for atk in set(fw.predecessors(defender)):
                # contradiction found
                if atk in inargs:
                    return False, None
                # cannot reuse arguments
                if atk not in outargs:
                    options.add(atk)
        # print(f'\t\t\t opponent checks: {options}\n')
        for opt in options:
            hope, answers = dfs(fw, inargs, outargs.union({opt}),opt, True)
            if not hope:
                #propagate the fact that the opponent can win
                return False, None
        # opponent cant attack
        return True, None

def proponent(framework, last_attack, starting_arg):
    # the starting argument has not been used yet == first round
    if not framework.nodes[starting_arg]['p_used']:
        framework.nodes[starting_arg]['p_used'] = True
        framework.nodes[starting_arg]['status'] = 'in'
        print(f'proponent starts: {starting_arg}\n')
        return True, starting_arg

    # otherwise, try to find a winning path
    inargs = set([node for node in framework.nodes if framework.nodes[node]['status'] == 'in'])
    outargs = set([node for node in framework.nodes if framework.nodes[node]['status'] == 'out'])
    hope, response=  dfs(framework, inargs, outargs, last_attack, True)
    if hope:
        framework.nodes[response]['p_used'] = True
        framework.nodes[response]['status'] = 'in'
        print(f'proponent states IN: {response}\n')
        return True, response
    else:
        #no hope, pick random
        if len(list(framework.predecessors(last_attack))) == 0:
            # no otpions
            print("Proponent can only choose contradicting arguments, Opponent wins\n")
            return False, None
        else:
            response = list(framework.predecessors(last_attack))[0]
            framework.nodes[response]['p_used'] = True
            framework.nodes[response]['status'] = 'in'
            print(f'proponent states IN: {response}\t ps: no hope here\n')
            return True, response
    # all possible args have been used by the Opponent, Opponent wins



def available_args(framework):
    #
    attacks = []
    # all arguments that the proponent stated...
    for n in [x for x, y in framework.nodes(data=True) if y['p_used']]:
        # ...can be attacked by parent arguments if the argument has not been used yet by the opponent
        attacks += [e[0] for e in framework.in_edges(n) if not framework.nodes[e[0]]['o_used']]

    return True if len(attacks) > 0 else False, set(attacks)


def opponent(framework, human=False):
    available, args = available_args(framework)

    if not available:
        # no more available arguments
        print('Opponent has no options left, Proponent wins\n')
        return False, None

    if human:
        arg = input(f"Opponent, please choose an attacking argument among {args}\n")
        while arg not in args:
            # if something went wrong with the input
            arg = input(f"Argument not allowed, please choose an attacking argument among {args}\n")

        if framework.nodes[arg]['p_used']:
            # an argument is used both by prop and opp
            print(f'Contradiction found by stating {arg}, Opponent wins\n')
            return False, None

        framework.nodes[arg]['o_used'] = True
        framework.nodes[arg]['status'] = 'out'
        print(f'Opponent states OUT: {arg}')
    else:
        arg = random.choice(list(args))

        if framework.nodes[arg]['p_used']:
            # an argument is used both by prop and opp
            print(f'Contradiction found by stating {arg}, Opponent wins\n')
            return False, None

        framework.nodes[arg]['o_used'] = True
        framework.nodes[arg]['status'] = 'out'
        print(f'Opponent states OUT: {arg}')

    return True, arg


def game(fname='examples/xample-argumentation-framework.json', argument='', human=True):
    with open(fname, 'r') as file:
        data = json.load(file)

    for key, value in data.items():
        print(f"Key: {key}, Value: {value}")

    # create the framework as a directed graph
    framework = nx.DiGraph()
    framework.add_edges_from(data['Attack Relations'])

    # initialize all nodes as not used
    nx.set_node_attributes(framework, False, "p_used")
    nx.set_node_attributes(framework, False, "o_used")

    # this is not yet used, but ideally it's for adding colors in the graph
    nx.set_node_attributes(framework, 'u', 'status')

    running = True
    o_attack = None
    while running:
        running, p_argument = proponent(framework, last_attack=o_attack, starting_arg=argument)

        if running:
            running, o_attack = opponent(framework, human=human)

    return


# game(argument = sys.argv[1])
game(fname='examples/example3.json', argument='d')


