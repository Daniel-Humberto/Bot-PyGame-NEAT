import os
import pygame
import neat
import time
import random
import pickle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
from game import FlappyBird
from visualize import draw_net, plot_stats


# Global constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
GAME_WIDTH = 600
GAME_HEIGHT = 800


# Initialize pygame
pygame.init()
STAT_FONT = pygame.font.SysFont("comicsans", 30)
END_FONT = pygame.font.SysFont("comicsans", 50)
WINDOW = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("NEAT Flappy Bird")


# Game stats
generation = 0
best_fitness = 0
generation_fitnesses = []
all_time_best_genome = None


# Evaluate each genome by running the game with the neural network controlling the bird.
def eval_genomes(genomes, config):
    
    global generation, best_fitness, generation_fitnesses, all_time_best_genome

    # Keep track of the nets, birds, and genomes
    nets = []
    games = []
    ge = []

    generation += 1
    generation_best_fitness = 0

    # Create a game instance for each genome
    for genome_id, genome in genomes:
        # Create network for each genome
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)

        # Create a new game for this genome
        games.append(FlappyBird())

        # Set initial fitness to 0
        genome.fitness = 0
        ge.append(genome)

    # Main game loop
    run = True
    clock = pygame.time.Clock()

    while run and len(games) > 0:
        # Limit frame rate to 30 FPS
        clock.tick(30)

        # Handle quitting
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # For each active game, get pipe information and make decision
        for i, game in enumerate(games):
            # Move to the next iteration to give the bird information about its position
            pipe_ind = 0
            if len(game.pipes) > 1 and game.bird.x > game.pipes[0].x + game.pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1

            # Get inputs for neural network
            # Normalized inputs to range [0, 1]:
            # 1. Bird's y position
            # 2. Distance to top pipe
            # 3. Distance to bottom pipe
            # 4. Bird's velocity
            inputs = (
                game.bird.y / GAME_HEIGHT,  # Bird's y position
                abs(game.bird.y - game.pipes[pipe_ind].height) / GAME_HEIGHT,  # Distance to top pipe
                abs(game.bird.y - game.pipes[pipe_ind].bottom) / GAME_HEIGHT,  # Distance to bottom pipe
                game.bird.vel / 10  # Bird's velocity (normalized)
            )

            # Get neural network output
            output = nets[i].activate(inputs)

            # If output is > 0.5, the bird jumps
            if output[0] > 0.5:
                game.bird.jump()

            # Update game state and get result
            result = game.update()

            # Update fitness
            ge[i].fitness += 0.1  # Small reward for staying alive

            # Check if the bird passed a pipe
            if game.score > 0 and game.score > ge[i].fitness / 5:
                ge[i].fitness = game.score * 5  # Big reward for passing pipes

            # If bird hit something, remove it
            if result == "dead":
                # Update best fitness
                if ge[i].fitness > generation_best_fitness:
                    generation_best_fitness = ge[i].fitness

                # Remove this game instance
                nets.pop(i)
                ge.pop(i)
                games.pop(i)

        # Draw everything
        WINDOW.fill((255, 255, 255))

        # Draw games
        if games:
            # Draw the first game (or a random one) larger on the left
            games[0].draw(WINDOW, (0, 0, GAME_WIDTH, GAME_HEIGHT))

            # Draw smaller versions of other games if there are any
            small_height = 200
            small_width = 150
            spacing = 10

            for i in range(1, min(9, len(games))):
                x = GAME_WIDTH + spacing + ((i - 1) % 3) * (small_width + spacing)
                y = spacing + ((i - 1) // 3) * (small_height + spacing)
                games[i].draw(WINDOW, (x, y, small_width, small_height))

        # Draw statistics
        text = STAT_FONT.render(f"Generation: {generation}", 1, (0, 0, 0))
        WINDOW.blit(text, (GAME_WIDTH + 10, GAME_HEIGHT - 300))

        text = STAT_FONT.render(f"Alive: {len(games)}", 1, (0, 0, 0))
        WINDOW.blit(text, (GAME_WIDTH + 10, GAME_HEIGHT - 270))

        text = STAT_FONT.render(f"Best Fitness: {best_fitness:.1f}", 1, (0, 0, 0))
        WINDOW.blit(text, (GAME_WIDTH + 10, GAME_HEIGHT - 240))

        text = STAT_FONT.render(f"Current Best: {generation_best_fitness:.1f}", 1, (0, 0, 0))
        WINDOW.blit(text, (GAME_WIDTH + 10, GAME_HEIGHT - 210))

        # Draw the generation fitness graph
        if generation_fitnesses:
            # Create a matplotlib figure
            fig = plt.figure(figsize=(5, 3), dpi=80)
            plt.plot(range(1, len(generation_fitnesses) + 1), generation_fitnesses)
            plt.title('Generation Best Fitness')
            plt.xlabel('Generation')
            plt.ylabel('Fitness')
            plt.grid(True)

            # Convert to pygame surface
            canvas = FigureCanvasAgg(fig)
            canvas.draw()
            renderer = canvas.get_renderer()
            raw_data = renderer.buffer_rgba()
            size = canvas.get_width_height()

            # Create pygame surface (use RGBA)
            surf = pygame.image.frombuffer(raw_data, size, "RGBA")
            WINDOW.blit(surf, (GAME_WIDTH + 10, GAME_HEIGHT - 200))

            plt.close(fig)


        # Update display
        pygame.display.update()

    # Update statistics after generation
    if generation_best_fitness > best_fitness:
        best_fitness = generation_best_fitness

        # Find the best genome from this generation
        best_genome = None
        best_fitness_val = 0
        for genome in ge:
            if genome.fitness > best_fitness_val:
                best_fitness_val = genome.fitness
                best_genome = genome

        if best_genome and (all_time_best_genome is None or best_fitness_val > all_time_best_genome.fitness):
            all_time_best_genome = best_genome

            # Save the best genome
            with open("best.pickle", "wb") as f:
                pickle.dump(best_genome, f)

    generation_fitnesses.append(generation_best_fitness)


# Run the NEAT algorithm with the given config file.
def run_neat(config_path):
    
    # Load configuration
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    # Create the population
    p = neat.Population(config)

    # Add a reporter to show progress in the terminal
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to 50 generations
    winner = p.run(eval_genomes, 50)

    # Show final stats
    print('\nBest genome:\n{!s}'.format(winner))

    # Save the winner
    with open("winner.pickle", "wb") as f:
        pickle.dump(winner, f)

    # Visualize the winner network
    draw_net(config, winner, True)

    # Plot stats
    plot_stats(stats, ylog=False, view=True)


# Run the winner genome in the game to showcase its performance.
def run_winner(config_path, genome_path="winner.pickle"):
    
    # Load configuration
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    # Load the winner genome
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    # Create the neural network
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    # Create a game
    game = FlappyBird()

    # Main game loop
    run = True
    clock = pygame.time.Clock()

    while run:
        # Limit frame rate
        clock.tick(30)

        # Handle quitting
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # Get pipe information
        pipe_ind = 0
        if len(game.pipes) > 1 and game.bird.x > game.pipes[0].x + game.pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1

        # Get inputs for neural network
        inputs = (
            game.bird.y / GAME_HEIGHT,
            abs(game.bird.y - game.pipes[pipe_ind].height) / GAME_HEIGHT,
            abs(game.bird.y - game.pipes[pipe_ind].bottom) / GAME_HEIGHT,
            game.bird.vel / 10
        )

        # Get neural network output
        output = net.activate(inputs)

        # If output is > 0.5, the bird jumps
        if output[0] > 0.5:
            game.bird.jump()

        # Update game state
        result = game.update()

        # Check if game is over
        if result == "dead":
            run = False
            break

        # Draw game
        WINDOW.fill((255, 255, 255))
        game.draw(WINDOW, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Draw score
        text = STAT_FONT.render(f"Score: {game.score}", 1, (0, 0, 0))
        WINDOW.blit(text, (10, 10))

        # Update display
        pygame.display.update()


if __name__ == "__main__":
    # Get path to configuration file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    # Run NEAT
    run_neat(config_path)

    # Run the winner
    run_winner(config_path)