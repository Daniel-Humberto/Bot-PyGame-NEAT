import matplotlib.pyplot as plt
import numpy as np
import os
import graphviz
import warnings


warnings.filterwarnings("ignore", category=UserWarning)


# Plots the population's average and best fitness.
def plot_stats(statistics, ylog=False, view=False, filename='avg_fitness.svg'):

    if plt is None:
        warnings.warn("This display is not available due to a missing optional dependency (matplotlib)")
        return

    generation = range(len(statistics.most_fit_genomes))
    best_fitness = [c.fitness for c in statistics.most_fit_genomes]
    avg_fitness = np.array(statistics.get_fitness_mean())
    stdev_fitness = np.array(statistics.get_fitness_stdev())

    plt.figure(figsize=(10, 6))
    plt.plot(generation, avg_fitness, 'b-', label="average")
    plt.plot(generation, avg_fitness - stdev_fitness, 'g-.', label="-1 sd")
    plt.plot(generation, avg_fitness + stdev_fitness, 'g-.', label="+1 sd")
    plt.plot(generation, best_fitness, 'r-', label="best")

    plt.title("Population's Average and Best Fitness")
    plt.xlabel("Generations")
    plt.ylabel("Fitness")
    plt.grid()
    plt.legend(loc="best")
    if ylog:
        plt.gca().set_yscale('symlog')

    plt.savefig(filename)
    if view:
        plt.show()

    plt.close()


# Visualizes speciation throughout evolution.
def plot_species(statistics, view=False, filename='speciation.svg'):

    if plt is None:
        warnings.warn("This display is not available due to a missing optional dependency (matplotlib)")
        return

    species_sizes = statistics.get_species_sizes()
    num_generations = len(species_sizes)
    curves = np.array(species_sizes).T

    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.stackplot(range(num_generations), *curves)

    plt.title("Speciation")
    plt.ylabel("Size per Species")
    plt.xlabel("Generations")

    plt.savefig(filename)

    if view:
        plt.show()

    plt.close()


# Draw a neural network with arbitrary topology.
def draw_net(config, genome, view=False, filename=None, node_names=None, show_disabled=True, prune_unused=False,
             node_colors=None, fmt='svg'):
    
    if graphviz is None:
        warnings.warn("This display is not available due to a missing optional dependency (graphviz)")
        return

    if node_names is None:
        node_names = {}

    if node_colors is None:
        node_colors = {}

    nodes = []
    connections = []

    # Get connections and enabled status
    for cg in genome.connections.values():
        if cg.enabled or show_disabled:
            connections.append((cg.key[0], cg.key[1], cg.weight, cg.enabled))

    # Determine nodes
    input_nodes = []
    hidden_nodes = []
    output_nodes = []

    for k in genome.nodes.keys():
        if k < config.genome_config.num_inputs:
            input_nodes.append(k)
        elif k < config.genome_config.num_inputs + config.genome_config.num_outputs:
            output_nodes.append(k)
        else:
            hidden_nodes.append(k)

    # Create digraph
    dot = graphviz.Digraph(format=fmt)

    # Input nodes
    for n in input_nodes:
        attrs = {'style': 'filled', 'shape': 'box', 'fillcolor': node_colors.get(n, 'lightgray')}
        dot.node(str(n), label=node_names.get(n, str(n)), **attrs)

    # Output nodes
    for n in output_nodes:
        attrs = {'style': 'filled', 'shape': 'box', 'fillcolor': node_colors.get(n, 'lightblue')}
        dot.node(str(n), label=node_names.get(n, str(n)), **attrs)

    # Hidden nodes
    for n in hidden_nodes:
        attrs = {'style': 'filled', 'shape': 'ellipse', 'fillcolor': node_colors.get(n, 'white')}
        dot.node(str(n), label=node_names.get(n, str(n)), **attrs)

    # Connections
    for src, tgt, weight, enabled in connections:
        if enabled:
            color = 'green' if weight > 0 else 'red'
            width = str(0.1 + abs(weight / 5.0))
        else:
            color = 'gray'
            width = str(0.1)

        dot.edge(str(src), str(tgt), color=color, penwidth=width)

    # Return the dot
    if filename is not None:
        dot.render(filename)

    if view:
        dot.view()

    return dot