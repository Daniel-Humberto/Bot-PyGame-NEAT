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
GAME_HEIGHT = 700  # Reduced to make room for stats at bottom
STATS_HEIGHT = 100  # Height of stats bar at bottom
SIDEBAR_WIDTH = 600  # Width of the right sidebar


# Colors
BG_COLOR = (240, 240, 240)
PANEL_COLOR = (220, 220, 220)
TEXT_COLOR = (50, 50, 50)
HIGHLIGHT_COLOR = (70, 130, 180)  # Steel blue
GRID_COLOR = (200, 200, 200)
POSITIVE_COLOR = (46, 139, 87)  # Sea green
NEGATIVE_COLOR = (220, 20, 60)  # Crimson


# Initialize pygame
pygame.init()
STAT_FONT = pygame.font.SysFont("Arial", 24)
TITLE_FONT = pygame.font.SysFont("Arial", 28, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 18)
END_FONT = pygame.font.SysFont("Arial", 50, bold=True)
WINDOW = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("NEAT Flappy Bird - AI Training Visualization")


# Game stats
generation = 0
best_fitness = 0
generation_fitnesses = []
all_time_best_genome = None


# Draw a panel with optional border
def draw_panel(surface, rect, color=PANEL_COLOR, border=True):
    
    pygame.draw.rect(surface, color, rect)
    if border:
        pygame.draw.rect(surface, (180, 180, 180), rect, 1)


# Draw the statistics panel at the bottom of the screen
def draw_stats_panel(surface):
    
    # Draw the panel background
    stats_rect = pygame.Rect(0, GAME_HEIGHT, SCREEN_WIDTH, STATS_HEIGHT)
    draw_panel(surface, stats_rect)

    # Draw title
    title = TITLE_FONT.render("TRAINING STATISTICS", 1, HIGHLIGHT_COLOR)
    surface.blit(title, (20, GAME_HEIGHT + 10))

    # Draw KPIs
    kpi_width = 200
    kpi_spacing = 20
    kpi_y = GAME_HEIGHT + 50

    # Generation
    gen_text = STAT_FONT.render(f"Generation:", 1, TEXT_COLOR)
    gen_value = TITLE_FONT.render(f"{generation}", 1, HIGHLIGHT_COLOR)
    surface.blit(gen_text, (20, kpi_y))
    surface.blit(gen_value, (40, kpi_y + 25))

    # Alive birds
    alive_text = STAT_FONT.render(f"Birds Alive:", 1, TEXT_COLOR)
    alive_value = TITLE_FONT.render(f"{len(games) if 'games' in globals() else 0}", 1, POSITIVE_COLOR)
    surface.blit(alive_text, (kpi_width + kpi_spacing, kpi_y))
    surface.blit(alive_value, (kpi_width + kpi_spacing + 40, kpi_y + 25))

    # All-time best fitness
    best_text = STAT_FONT.render(f"All-time Best:", 1, TEXT_COLOR)
    best_value = TITLE_FONT.render(f"{best_fitness:.1f}", 1, HIGHLIGHT_COLOR)
    surface.blit(best_text, (2 * kpi_width + 2 * kpi_spacing, kpi_y))
    surface.blit(best_value, (2 * kpi_width + 2 * kpi_spacing + 40, kpi_y + 25))

    # Current generation best fitness
    current_text = STAT_FONT.render(f"Current Best:", 1, TEXT_COLOR)
    gen_best = generation_best_fitness if 'generation_best_fitness' in globals() else 0
    current_value = TITLE_FONT.render(f"{gen_best:.1f}", 1,
                                      POSITIVE_COLOR if gen_best >= best_fitness else TEXT_COLOR)
    surface.blit(current_text, (3 * kpi_width + 3 * kpi_spacing, kpi_y))
    surface.blit(current_value, (3 * kpi_width + 3 * kpi_spacing + 40, kpi_y + 25))


# Draw the generation fitness graph
def draw_fitness_graph(surface):
    
    if not generation_fitnesses:
        return

    # Panel for the graph
    graph_rect = pygame.Rect(GAME_WIDTH + 20, 360, SIDEBAR_WIDTH - 40, 320)
    draw_panel(surface, graph_rect)

    # Title
    title = TITLE_FONT.render("Generation Fitness History", 1, HIGHLIGHT_COLOR)
    surface.blit(title, (GAME_WIDTH + 30, 370))

    # Create a matplotlib figure with improved styling
    fig = plt.figure(figsize=(5.6, 3), dpi=80)
    plt.plot(range(1, len(generation_fitnesses) + 1), generation_fitnesses,
             color=HIGHLIGHT_COLOR[0] / 255, marker='o', markersize=3)

    # Add trend line
    if len(generation_fitnesses) > 1:
        z = np.polyfit(range(1, len(generation_fitnesses) + 1), generation_fitnesses, 1)
        p = np.poly1d(z)
        plt.plot(range(1, len(generation_fitnesses) + 1), p(range(1, len(generation_fitnesses) + 1)),
                 "r--", alpha=0.7)

    plt.title('Fitness Progression')
    plt.xlabel('Generation')
    plt.ylabel('Best Fitness')
    plt.grid(True, linestyle='--', alpha=0.7)

    # Set dynamic y-axis range
    max_fitness = max(generation_fitnesses)
    plt.ylim(0, max(10, max_fitness * 1.2))

    # Add last 5 generations annotation
    if len(generation_fitnesses) >= 5:
        last_5_avg = sum(generation_fitnesses[-5:]) / 5
        plt.axhline(y=last_5_avg, color='green', linestyle='--', alpha=0.5)
        plt.text(0.05, 0.9, f"Last 5 Gen Avg: {last_5_avg:.1f}",
                 transform=plt.gca().transAxes, bbox=dict(facecolor='white', alpha=0.7))

    # Convert to pygame surface
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()
    size = canvas.get_width_height()

    # Create pygame surface
    surf = pygame.image.frombuffer(raw_data, size, "RGBA")
    surface.blit(surf, (GAME_WIDTH + 30, 400))

    plt.close(fig)


# Draw neural network information panel
def draw_info_panel(surface):
    
    # Panel for neural network info
    info_rect = pygame.Rect(GAME_WIDTH + 20, 20, SIDEBAR_WIDTH - 40, 320)
    draw_panel(surface, info_rect)

    # Title
    title = TITLE_FONT.render("NEAT Configuration", 1, HIGHLIGHT_COLOR)
    surface.blit(title, (GAME_WIDTH + 30, 30))

    # Network info
    info_texts = [
        "Neural Network: 4 Inputs, 1 Output",
        "Inputs: Bird height, distances to pipes, velocity",
        "Output: Jump decision (>0.5 threshold)",
        "Population Size: 50",
        "Mutation Rates:",
        "  - Weight: 0.8",
        "  - Add Node: 0.2",
        "  - Add Connection: 0.5",
        "Fitness: Distance traveled + 5 * pipes passed"
    ]

    for i, text in enumerate(info_texts):
        rendered = SMALL_FONT.render(text, 1, TEXT_COLOR)
        surface.blit(rendered, (GAME_WIDTH + 40, 70 + i * 25))

    # Current generation status
    gen_status = STAT_FONT.render(f"Generation {generation} Progress", 1, HIGHLIGHT_COLOR)
    surface.blit(gen_status, (GAME_WIDTH + 30, 330))


# Draw the small games in a grid layout
def draw_small_games_grid(surface, games):
    
    if len(games) <= 1:
        return

    grid_x, grid_y = GAME_WIDTH + 20, 20
    cell_width, cell_height = (SIDEBAR_WIDTH - 60) // 3, 100
    padding = 10

    # Draw grid title
    title = TITLE_FONT.render(f"Top Performing Birds ({min(9, len(games) - 1)})", 1, HIGHLIGHT_COLOR)
    surface.blit(title, (grid_x, grid_y))
    grid_y += 40

    # Draw grid background
    grid_rect = pygame.Rect(grid_x - padding, grid_y - padding,
                            3 * cell_width + 2 * padding + 20,
                            3 * cell_height + 2 * padding + 20)
    draw_panel(surface, grid_rect)

    # Draw small game views
    for i in range(1, min(10, len(games))):
        x = grid_x + ((i - 1) % 3) * (cell_width + 10)
        y = grid_y + ((i - 1) // 3) * (cell_height + 10)

        # Draw cell background
        cell_rect = pygame.Rect(x, y, cell_width, cell_height)
        draw_panel(surface, cell_rect, pygame.Color(230, 230, 230))

        # Draw the game
        games[i].draw(surface, (x, y, cell_width, cell_height))

        # Draw bird number
        bird_text = SMALL_FONT.render(f"Bird #{i}", 1, TEXT_COLOR)
        surface.blit(bird_text, (x + 5, y + 5))

        # Draw bird score
        score_text = SMALL_FONT.render(f"Score: {games[i].score}", 1, POSITIVE_COLOR)
        surface.blit(score_text, (x + 5, y + cell_height - 20))


# Evaluate each genome by running the game with the neural network controlling the bird.
def eval_genomes(genomes, config):
    
    global generation, best_fitness, generation_fitnesses, all_time_best_genome, games

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
        # Limit frame rate
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
        WINDOW.fill(BG_COLOR)

        # Draw panels and info
        if games:
            # Draw the first game (best performer) in the main view
            games[0].draw(WINDOW, (0, 0, GAME_WIDTH, GAME_HEIGHT))

            # Add label for main game
            main_label = TITLE_FONT.render("Best Performing Bird", 1, HIGHLIGHT_COLOR)
            main_score = STAT_FONT.render(f"Score: {games[0].score}", 1, TEXT_COLOR)
            WINDOW.blit(main_label, (20, 20))
            WINDOW.blit(main_score, (20, 55))

            # Draw small game views in grid
            draw_small_games_grid(WINDOW, games)

            # Draw fitness graph
            draw_fitness_graph(WINDOW)
        else:
            # If no games are active, show message
            no_birds = END_FONT.render("All birds died!", 1, NEGATIVE_COLOR)
            WINDOW.blit(no_birds, (GAME_WIDTH // 2 - no_birds.get_width() // 2,
                                   GAME_HEIGHT // 2 - no_birds.get_height() // 2))

            # Draw fitness graph
            draw_fitness_graph(WINDOW)

        # Draw stats panel
        draw_stats_panel(WINDOW)

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
    draw_net(config, winner, True, filename="winner_network")

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
        WINDOW.fill(BG_COLOR)
        game.draw(WINDOW, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Draw score
        text = TITLE_FONT.render(f"Score: {game.score}", 1, HIGHLIGHT_COLOR)
        WINDOW.blit(text, (20, 20))

        # Draw info
        info_text = STAT_FONT.render("Running winner genome from training", 1, TEXT_COLOR)
        WINDOW.blit(info_text, (20, 60))

        # Update display
        pygame.display.update()


# 
if __name__ == "__main__":
    # Get path to configuration file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    # Run NEAT
    run_neat(config_path)

    # Run the winner
    run_winner(config_path)