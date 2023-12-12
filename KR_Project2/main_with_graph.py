import json
import networkx as nx
import tkinter as tk
import matplotlib
import random
import os


matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure

game_over_flag = False
last_node = None
first_click = True


def proponent(framework, last_attack, starting_arg):
    # the starting argument has not been used yet == first round
    if starting_arg != -1 and starting_arg in framework.nodes and not framework.nodes[starting_arg]['p_used']:
        framework.nodes[starting_arg]['p_used'] = True
        framework.nodes[starting_arg]['status'] = 'in'
        return True, starting_arg

    # otherwise, need to attack the last argument from O

    possible_args = list(framework.predecessors(last_attack)) #entering edges
    # print("possible", possible_args)
    if len(possible_args) == 0:
        # no attacks are available, proponent looses
        print("Proponent cannot attack Opponent's argument.")
        return False, None

    for arg in possible_args:
        if not framework.nodes[arg]['o_used']:
            # a valid argument is found, no strategy here
            framework.nodes[arg]['p_used'] = True
            framework.nodes[arg]['status'] = 'in'
            print(f"Proponent states IN: {arg}")
            return True, arg

    # all possible args have been used by the Opponent, Opponent wins
    print("Proponent can only choose contradicting arguments.")
    return False, None


def available_args(framework):
    #
    attacks = []
    # all arguments that the proponent stated...
    for n in [x for x, y in framework.nodes(data=True) if y['p_used']]:
        # ...can be attacked by parent arguments if the argument has not been used yet by the opponent
        attacks += [e[0] for e in framework.in_edges(n) if not framework.nodes[e[0]]['o_used']]

    return True if len(attacks) > 0 else False, set(attacks)


def opponent(framework, last_attack, human=True):
    try:   
        available, args = available_args(framework)

        if not available:
            # no more available arguments
            print('Opponent has no options left, Proponent wins\n')
            return False, None

        if human:
            for i in list(framework.nodes):
                if framework.nodes[i]['color'] == 'green':
                    framework.nodes[i]['color'] = 'grey'
            possible_args = []
            for i in list(framework.predecessors(last_attack)):
                if not framework.nodes[i]['color'] == 'red':
                    possible_args.append(i)
            arg = input(f"Opponent, please choose an attacking argument among {possible_args}\n")            
        else:
            arg = random.choice(list(args))

            if framework.nodes[arg]['p_used']:
                # an argument is used both by prop and opp
                print(f'Contradiction found by stating {arg}, Opponent wins\n')
                return False, None
        
            print("setting")
            framework.nodes[arg]['o_used'] = True
            framework.nodes[arg]['status'] = 'out'
            print(f'Opponent states OUT: {arg}')

        # print(f"Opponent chose: {arg}")  # Move this line here, this was for terminal input

        return True, arg
    except RuntimeError as e:
        return False, None
        # Handle the error when needed


def find_node_id(event, pos):
    node_id = None
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
    nx.set_node_attributes(framework, "grey", "color")

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
        global last_node
        running, p_argument = proponent(framework, last_attack=last_attack, starting_arg=starting_arg)
        last_node = p_argument
        if running:
        
            framework.nodes[p_argument]['color'] = 'red'
            framework.nodes[p_argument]['p_used'] = True
            possible_args = list(framework.predecessors(p_argument)) 
        
            for i in possible_args:
                if not framework.nodes[i]['color'] == 'red':
                    framework.nodes[i]['color'] = 'green'

            update_node_colors()
            frame.after(1000, lambda: opponent_turn(framework, p_argument))
        else:
            game_over("Oponent")

    def opponent_turn(framework, last_attack = None):
        running, o_attack = opponent(framework, last_attack)
        if running:
            frame.after(1000, lambda: proponent_turn(framework, last_attack=o_attack))
        else:
            print("Oponent has no more nodes to attack.")
            game_over("Proponent")
            

    def update_node_colors():
        node_colors = [framework.nodes[node].get('color', 'grey') for node in framework.nodes]
        nx.draw(framework, pos=pos, ax=ax, with_labels=True, node_color=node_colors)
        canvas.draw()

  
    def game_over(winner):
        global game_over_flag
        game_over_flag = True
        print(f"Game over, {winner} wins.")
        frame.quit()


    def on_node_click(event):
        global game_over_flag  # Reference the global variable
        global first_click

        # Check if the game is over
        if game_over_flag:
            print("The game is over. Click events are disabled.")
            return
        
        node_id = find_node_id(event, pos)

        if node_id is not None:
            if framework.nodes[node_id]['p_used']:
                # an argument is used by prop
                print(f'Contradiction found by stating {node_id}.')
                frame.after(1000, lambda: game_over("Proponent"))
                return False, None
            if framework.nodes[node_id]['o_used']:
                # an argument is used by opp
                print(f'Argument ({node_id}) already used by oponent.')
                frame.after(1000, lambda: game_over("Proponent"))
                return False, None
            if not first_click and node_id not in list(framework.predecessors(last_node)):
                # an argument is not a possible attack
                print(f'Node {node_id} is no possible attack on {last_node}. Please try again.')
                return False, None

            framework.nodes[node_id]['o_used'] = True
            framework.nodes[node_id]['status'] = 'out'
            print(f'Opponent states OUT: {node_id}')
            framework.nodes[node_id]['color'] = 'red'
            update_node_colors()
            first_click = False
            frame.after(1000, lambda: proponent_turn(framework, last_attack=node_id))
            

    
    canvas.mpl_connect("button_press_event", on_node_click)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    tk.mainloop()


if __name__ == "__main__":
    game(argument='1')
    # game(argument = sys.argv[1])
