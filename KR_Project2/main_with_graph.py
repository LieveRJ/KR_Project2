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


def proponent(framework, last_attack, starting_arg):
    # the starting argument has not been used yet == first round
    if starting_arg != -1 and starting_arg in framework.nodes and not framework.nodes[starting_arg]['p_used']:
        framework.nodes[starting_arg]['p_used'] = True
        framework.nodes[starting_arg]['status'] = 'in'
        return True, starting_arg

    # otherwise, need to attack the last argument from O

    possible_args = list(framework.predecessors(last_attack)) #entering edges

    if len(possible_args) == 0:
        # no attacks are available, proponent looses
        print("Proponent cannot attack Opponent's argument, Opponent wins\n")
        return False, None

    for arg in possible_args:
        if not framework.nodes[arg]['o_used']:
            # a valid argument is found, no strategy here
            framework.nodes[arg]['p_used'] = True
            framework.nodes[arg]['status'] = 'in'
            print(f"Proponent states IN: {arg}")
            return True, arg

    # all possible args have been used by the Opponent, Opponent wins
    print("Proponent can only choose contradicting arguments, Opponent wins\n")
    return False, None


def available_args(framework):
    #
    attacks = []
    # all arguments that the proponent stated...
    for n in [x for x, y in framework.nodes(data=True) if y['p_used']]:
        # ...can be attacked by parent arguments if the argument has not been used yet by the opponent
        attacks += [e[0] for e in framework.in_edges(n) if not framework.nodes[e[0]]['o_used']]

    return True if len(attacks) > 0 else False, set(attacks)


# def admissibility(framework, argument):
    # TODO


def opponent(framework, human=True):
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


def key_press_handler(event):
    print(f"you pressed {event.key}")

def find_node_id(event, pos):
    for node, (x, y) in pos.items():
            if x - 0.05 < event.xdata < x + 0.05 and y - 0.05 < event.ydata < y + 0.05:
                node_id = node
                break
    return node_id


def game(fname='example-argumentation-framework.json', argument=''):
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

    #this is not yet used, but ideally it's for adding colors in the graph
    # nx.set_node_attributes(framework, 'u', 'status')
    frame = tk.Tk()
    frame.wm_title("Framework")

    fig = Figure(figsize=(5, 4), dpi=100)
    ax = fig.add_subplot()
    seed = 42
    pos = nx.spring_layout(framework, seed=seed)
    nx.draw(framework, pos=pos, ax=ax, with_labels=True)
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, frame, pack_toolbar=False)
    toolbar.update()
    canvas.mpl_connect("key_press_event", lambda event: print(f"you pressed {event.key}"))

    def proponent_turn(framework, last_attack=None, starting_arg=''):
        running, p_argument = proponent(framework, last_attack=last_attack, starting_arg=starting_arg)
        if running:
            framework.nodes[p_argument]['color'] = 'red'
            update_node_colors()
            frame.after(1000, lambda: opponent_turn(framework))
        else:
            print("Game over. No more nodes to attack.")
            frame.quit()

    def opponent_turn(framework):
        running, o_attack = opponent(framework)
        if running:
            frame.after(1000, lambda: proponent_turn(framework, last_attack=o_attack))

    def update_node_colors():
        node_colors = [framework.nodes[node].get('color', 'blue') for node in framework.nodes]
        nx.draw(framework, pos=pos, ax=ax, with_labels=True, node_color=node_colors)
        canvas.draw()

    def on_node_click(event):
        node_id = find_node_id(event, pos)

        if node_id is not None:
            print(f"Node clicked: {node_id}")
            framework.nodes[node_id]['color'] = 'red'
            update_node_colors()
            frame.after(1000, lambda: proponent_turn(framework, last_attack=node_id))
    
    canvas.mpl_connect("button_press_event", on_node_click)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    canvas.mpl_connect("key_press_event", key_press_handler)

    tk.mainloop()


if __name__ == "__main__":
    game(argument='1')
    # game(argument = sys.argv[1])
