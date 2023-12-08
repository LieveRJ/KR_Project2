import json
import networkx as nx
import tkinter as tk
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
# from PIL import ImageTk, Image
import os

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


# proponent = player1
# opponent = player2

# def proponent(framework, last_attack, starting_arg= -1):
#     # the starting argument has not been used yet == first round
#     if starting_arg!= -1 and not framework.nodes[starting_arg]['p_used']:
#         framework.nodes[starting_arg]['p_used'] = True
#         framework.nodes[starting_arg]['status'] = 'in'
#         return True, starting_arg
#
#     # otherwise, need to attack the last argument from O
#
#     possible_args = list(framework.predecessors(last_attack))
#
#     if len(possible_args) == 0:
#         # no attacks are available, proponent looses
#         print("Proponent cannot attack Opponent's argument, Opponent wins\n")
#         return False, None
#
#     for arg in possible_args:
#         if not framework.nodes[arg]['o_used']:
#             # a valid argument is found
#             framework.nodes[arg]['p_used'] = True
#             framework.nodes[arg]['status'] = 'in'
#             print(f"Proponent states IN: {arg}")
#             return True, arg
#
#     # all possible args have been used by the Opponent, Opponent wins
#     print("Proponent can only choose contradicting arguments, Opponent wins\n")
#     return False, None
#
#
# def available_args(framework):
#     #
#     attacks = []
#     # all arguments that the opponent stated...
#     for n in [x for x, y in framework.nodes(data=True) if y['p_used']]:
#         # ...can be attacked by parent arguments if the argument has not been used yet by the opponent
#         attacks += [e[0] for e in framework.in_edges(n) if not framework.nodes[e[0]]['o_used']]
#
#     return True if len(attacks) > 0 else False, set(attacks)
#
#
# def opponent(framework, human=True):
#     available, args = available_args(framework)
#
#     if not available:
#         # no more available arguments
#         print('Opponent has no options left, Proponent wins\n')
#         return False, None
#
#     if human:
#         arg = input(f"Opponent, please choose an attacking argument among {args}\n")
#         while arg not in args:
#             arg = input(f"Argument not allowed, please choose an attacking argument among {args}\n")
#
#         if framework.nodes[arg]['p_used']:
#             print(f'Contradiction found by stating {arg}, Opponent wins\n')
#             return False, None
#
#         framework.nodes[arg]['o_used'] = True
#         framework.nodes[arg]['status'] = 'out'
#         print(f'Opponent states OUT: {arg}')
#
#     return True, arg

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

    # this stores attacks relations that have been used
    nx.set_edge_attributes(framework, False, "p_used")
    nx.set_edge_attributes(framework, False, "o_used")

    # graphical part, need to better understand how to update
    frame = tk.Tk()
    frame.wm_title("Framework")

    fig = Figure(figsize=(5, 4), dpi=100)

    ax = fig.add_subplot()
    seed = 42
    pos = nx.spring_layout(framework, seed=seed)

    nx.draw(framework, pos=pos, ax=ax, with_labels=True)
    canvas = FigureCanvasTkAgg(fig, master=frame)  # A tk.DrawingArea.
    canvas.draw()



    # pack_toolbar=False will make it easier to use a layout manager later on.
    toolbar = NavigationToolbar2Tk(canvas, frame, pack_toolbar=False)
    toolbar.update()

    canvas.mpl_connect(
        "key_press_event", lambda event: print(f"you pressed {event.key}"))
    canvas.mpl_connect("key_press_event", key_press_handler)

    # button_quit = tk.Button(master=frame, text="Quit", command=frame.destroy)
    # button_quit.pack(side=tk.BOTTOM)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)



    #tk.mainloop()



    return


game(argument='1')
