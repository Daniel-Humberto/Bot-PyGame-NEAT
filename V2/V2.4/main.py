import pygame
from game import FlappyBird
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from visualize import draw_net, plot_stats
import numpy as np
import random
import pickle
import time
import neat
import os




# Dimensiones principales
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1010



# Definición de áreas y secciones
STATS_PANEL_HEIGHT = 180  # Panel de estadísticas arriba
MAIN_AREA_HEIGHT = SCREEN_HEIGHT - STATS_PANEL_HEIGHT - 40


# Dimensiones de los juegos
MAIN_GAME_WIDTH = 640
MAIN_GAME_HEIGHT = 480


# Dimensiones para mini-juegos
MINI_GAME_WIDTH = 160
MINI_GAME_HEIGHT = 120
MINI_GAMES_PER_COLUMN = 9


# Dimensiones para paneles inferiores
BOTTOM_PANEL_HEIGHT = 275


# Márgenes y espaciado
MARGIN = 20
PADDING = 15
WIDGET_SPACING = 10


# Paleta de colores
BG_COLOR = (10, 10, 10)
HIGHLIGHT_COLOR = (40, 40, 40)
PANEL_BG = (60, 60, 60)
BORDER_COLOR = (255, 255, 255)


# Paleta de colores
TEXT_COLOR_DEFAULT = (255, 255, 255)
GRID_COLOR = (0, 0, 0)
SUCCESS_COLOR = (0, 150, 0)
DANGER_COLOR = (150, 0, 0)
ACCENT_COLOR = (0, 0, 125)


# Para SMALL_FONT (usada en etiquetas de mini-juegos)
SMALL_FONT_COLOR_MINI_GAME_LABEL = (255, 255, 255)


# Para NORMAL_FONT (usada en el panel de información NEAT)
NORMAL_FONT_COLOR_NETWORK_INFO_LABEL = (255, 255, 255)
NORMAL_FONT_COLOR_NETWORK_INFO_VALUE = (255, 255, 255)


# Para STAT_FONT (usada para etiquetas de KPI en el panel de estadísticas)
STAT_FONT_COLOR_KPI_LABEL = (255, 255, 255)


# Para HEADER_FONT (usada en los encabezados de los paneles)
HEADER_FONT_COLOR_PANEL_TITLE = (255, 255, 255)


# Para TITLE_FONT (usada para el score en el juego principal, mensajes)
TITLE_FONT_COLOR_MAIN_GAME_SCORE = (255, 255, 255)
TITLE_FONT_COLOR_GRAPH_NO_DATA = (255, 255, 255)
TITLE_FONT_COLOR_MESSAGE_SUBTEXT = (255, 255, 255)


# Para LARGE_FONT (usada para valores de KPI, mensaje principal)
LARGE_FONT_COLOR_KPI_VALUE_DEFAULT = HIGHLIGHT_COLOR
LARGE_FONT_COLOR_MESSAGE_MAIN = DANGER_COLOR




# INICIALIZACIÓN DE PYGAME Y TIPOGRAFÍAS




# Inicializacion de PyGame
pygame.init()


# Sistema de tipografías coherente
SMALL_FONT = pygame.font.SysFont("Arial", 15)
NORMAL_FONT = pygame.font.SysFont("Arial", 17)
STAT_FONT = pygame.font.SysFont("Arial", 20)
HEADER_FONT = pygame.font.SysFont("Arial", 30, bold=True)
TITLE_FONT = pygame.font.SysFont("Arial", 25, bold=True)
LARGE_FONT = pygame.font.SysFont("Arial", 30, bold=True)


# Inicialización de la ventana
WINDOW = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("NEAT Flappy Bird - AI Training Visualization")


# Variables globales para estadísticas
generation = 0
best_fitness = 0
generation_fitnesses = []
generation_best_fitness = 0
all_time_best_genome = None
games = []




# FUNCIONES DE UI - COMPONENTES REUTILIZABLES




#    Dibuja un panel con bordes opcionales y esquinas redondeadas
def draw_panel(surface, rect, color=PANEL_BG, border=True, border_radius=8):

    pygame.draw.rect(surface, color, rect, border_radius=border_radius)

    if border:
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1, border_radius=border_radius)


#    Dibuja un encabezado con texto centrado
def draw_header(surface, rect, text, color=HIGHLIGHT_COLOR, text_color=HEADER_FONT_COLOR_PANEL_TITLE):

    pygame.draw.rect(surface, color, rect, border_radius=8)
    text_surf = HEADER_FONT.render(text, True, text_color)
    text_x = rect.left + (rect.width - text_surf.get_width()) // 2
    text_y = rect.top + (rect.height - text_surf.get_height()) // 2
    surface.blit(text_surf, (text_x, text_y))


#    Dibuja un indicador KPI con etiqueta y valor
def draw_kpi(surface, rect, label, value, value_color=LARGE_FONT_COLOR_KPI_VALUE_DEFAULT):

    draw_panel(surface, rect)
    label_surf = STAT_FONT.render(label, True, STAT_FONT_COLOR_KPI_LABEL)
    label_x = rect.left + (rect.width - label_surf.get_width()) // 2
    surface.blit(label_surf, (label_x, rect.top + PADDING))
    value_surf = LARGE_FONT.render(str(value), True, value_color)
    value_x = rect.left + (rect.width - value_surf.get_width()) // 2
    value_y = rect.top + label_surf.get_height() + PADDING
    surface.blit(value_surf, (value_x, value_y))




# FUNCIONES DE DIBUJO PRINCIPALES




#     Dibuja el panel de estadísticas global en la parte superior
def draw_stats_panel(surface):

    # Panel principal de estadísticas
    stats_panel = pygame.Rect(
        MARGIN,
        MARGIN,
        SCREEN_WIDTH - MARGIN * 2,
        STATS_PANEL_HEIGHT
    )
    draw_panel(surface, stats_panel)

    # Encabezado del panel
    header_rect = pygame.Rect(
        stats_panel.left,
        stats_panel.top,
        stats_panel.width,
        50
    )
    draw_header(surface, header_rect, "ESTADÍSTICAS DE ENTRENAMIENTO")

    # Distribución de KPIs en fila
    kpi_width = (stats_panel.width - PADDING * 5) // 4
    kpi_height = stats_panel.height - header_rect.height - PADDING * 2

    # KPI: Generación actual
    gen_kpi_rect = pygame.Rect(
        stats_panel.left + PADDING,
        header_rect.bottom + PADDING,
        kpi_width,
        kpi_height
    )
    draw_kpi(surface, gen_kpi_rect, "Generación Actual", generation)

    # KPI: Birds vivos
    birds_kpi_rect = pygame.Rect(
        gen_kpi_rect.right + PADDING,
        header_rect.bottom + PADDING,
        kpi_width,
        kpi_height
    )
    draw_kpi(surface, birds_kpi_rect, "Birds Vivos", len(games), SUCCESS_COLOR)

    # KPI: Mejor fitness histórico
    best_kpi_rect = pygame.Rect(
        birds_kpi_rect.right + PADDING,
        header_rect.bottom + PADDING,
        kpi_width,
        kpi_height
    )
    draw_kpi(surface, best_kpi_rect, "Mejor Fitness Histórico", f"{best_fitness:.1f}")

    # KPI: Mejor fitness generación actual
    gen_best_kpi_rect = pygame.Rect(
        best_kpi_rect.right + PADDING,
        header_rect.bottom + PADDING,
        kpi_width,
        kpi_height
    )

    # Color condicional según si supera el récord histórico
    gen_best = generation_best_fitness
    best_color = SUCCESS_COLOR if gen_best >= best_fitness else HIGHLIGHT_COLOR
    draw_kpi(surface, gen_best_kpi_rect, "Mejor Fitness Actual", f"{gen_best:.1f}", best_color)


#    Dibuja el juego principal en grande en el centro
def draw_main_game(surface, game):

    main_game_x = (SCREEN_WIDTH - MAIN_GAME_WIDTH) // 2
    main_game_y = STATS_PANEL_HEIGHT + MARGIN * 2
    main_game_rect = pygame.Rect(main_game_x, main_game_y, MAIN_GAME_WIDTH, MAIN_GAME_HEIGHT)
    draw_panel(surface, main_game_rect)

    header_rect = pygame.Rect(main_game_rect.left, main_game_rect.top, main_game_rect.width, 40)
    draw_header(surface, header_rect, "Mejor Bird en Acción")

    game_view_rect = (
        main_game_rect.left + PADDING,
        header_rect.bottom + PADDING,
        main_game_rect.width - PADDING * 2,
        main_game_rect.height - header_rect.height - PADDING * 2
    )
    game.draw(surface, game_view_rect)

    score_box = pygame.Rect(main_game_rect.left + PADDING, main_game_rect.bottom - 60, 120, 40)
    draw_panel(surface, score_box, ACCENT_COLOR, border=False, border_radius=20)
    score_text = TITLE_FONT.render(f"Score: {game.score}", True, TITLE_FONT_COLOR_MAIN_GAME_SCORE)
    surface.blit(score_text, (
        score_box.left + (score_box.width - score_text.get_width()) // 2,
        score_box.top + (score_box.height - score_text.get_height()) // 2
    ))


#    Dibuja los mini-juegos de la columna izquierda (birds 1-9)
def draw_left_mini_games(surface, games):

    if len(games) <= 1: return

    column_width = SCREEN_WIDTH // 4
    column_x = MARGIN
    column_y = STATS_PANEL_HEIGHT + MARGIN * 2
    column_rect = pygame.Rect(column_x, column_y, column_width - MARGIN, MAIN_GAME_HEIGHT)
    draw_panel(surface, column_rect)
    header_rect = pygame.Rect(column_rect.left, column_rect.top, column_rect.width, 40)
    draw_header(surface, header_rect, "Birds 1-9")

    mini_width = (column_rect.width - PADDING * 4) // 3
    mini_height = (column_rect.height - header_rect.height - PADDING * 4) // 3

    for i in range(1, min(10, len(games))):

        col = (i - 1) % 3
        row = (i - 1) // 3
        x = column_rect.left + PADDING + col * (mini_width + PADDING)
        y = header_rect.bottom + PADDING + row * (mini_height + PADDING)
        cell_rect = pygame.Rect(x, y, mini_width, mini_height)
        draw_panel(surface, cell_rect, pygame.Color(5, 5, 5), border_radius=4)  # Fondo de celda mini-juego
        game_view = (x + 2, y + 2, mini_width - 4, mini_height - 22)
        games[i].draw(surface, game_view)
        label_rect = pygame.Rect(x, y + mini_height - 20, mini_width, 20)
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, label_rect, border_radius=4)  # Fondo de etiqueta
        bird_text = SMALL_FONT.render(f"Bird #{i} | Score: {games[i].score}", True, SMALL_FONT_COLOR_MINI_GAME_LABEL)
        text_x_pos = x + (mini_width - bird_text.get_width()) // 2
        surface.blit(bird_text, (text_x_pos, y + mini_height - 18))


#    Dibuja los mini-juegos de la columna derecha (birds 10-18)
def draw_right_mini_games(surface, games):

    if len(games) <= 10: return

    column_width = SCREEN_WIDTH // 4
    column_x = SCREEN_WIDTH - column_width
    column_y = STATS_PANEL_HEIGHT + MARGIN * 2
    column_rect = pygame.Rect(column_x, column_y, column_width - MARGIN, MAIN_GAME_HEIGHT)
    draw_panel(surface, column_rect)
    header_rect = pygame.Rect(column_rect.left, column_rect.top, column_rect.width, 40)
    draw_header(surface, header_rect, "Birds 10-18")

    mini_width = (column_rect.width - PADDING * 4) // 3
    mini_height = (column_rect.height - header_rect.height - PADDING * 4) // 3

    for i in range(10, min(19, len(games))):

        col = (i - 10) % 3
        row = (i - 10) // 3
        x = column_rect.left + PADDING + col * (mini_width + PADDING)
        y = header_rect.bottom + PADDING + row * (mini_height + PADDING)
        cell_rect = pygame.Rect(x, y, mini_width, mini_height)
        draw_panel(surface, cell_rect, pygame.Color(2, 2, 2), border_radius=4)  # Fondo de celda mini-juego
        game_view = (x + 2, y + 2, mini_width - 4, mini_height - 22)
        games[i].draw(surface, game_view)
        label_rect = pygame.Rect(x, y + mini_height - 20, mini_width, 20)
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, label_rect, border_radius=4)  # Fondo de etiqueta
        bird_text = SMALL_FONT.render(f"Bird #{i} | Score: {games[i].score}", True, SMALL_FONT_COLOR_MINI_GAME_LABEL)
        text_x_pos = x + (mini_width - bird_text.get_width()) // 2
        surface.blit(bird_text, (text_x_pos, y + mini_height - 18))


#    Dibuja el panel de información de la red neuronal en la parte inferior izquierda
def draw_network_info(surface):

    panel_width = SCREEN_WIDTH // 2 - MARGIN * 1.5
    panel_x = MARGIN
    panel_y = STATS_PANEL_HEIGHT + MAIN_GAME_HEIGHT + MARGIN * 3
    info_panel = pygame.Rect(panel_x, panel_y, panel_width, BOTTOM_PANEL_HEIGHT)
    draw_panel(surface, info_panel)
    title_rect = pygame.Rect(info_panel.left, info_panel.top, info_panel.width, 50)
    draw_header(surface, title_rect, "Configuración NEAT")

    info_texts = [
        ("Neural Network:", "4 Inputs, 1 Output"),
        ("Inputs:", "Bird height, distances to pipes, velocity"),
        ("Output:", "Jump decision (>0.5 threshold)"),
        ("Population Size:", "1000"),
        ("Mutation Rates:", "100"),
        ("  - Weight:", "0.8"),
        ("  - Add Node:", "0.2"),
        ("  - Add Connection:", "0.5"),
        ("Fitness Formula:", "Distance + 5 × pipes passed")
    ]
    col_width = (info_panel.width - PADDING * 3) // 2
    for i, (label, value) in enumerate(info_texts):
        col = 0 if i < 5 else 1
        row_idx = i if i < 5 else i - 5
        x = info_panel.left + PADDING + col * (col_width + PADDING)
        y = title_rect.bottom + PADDING + row_idx * 28
        label_surf = NORMAL_FONT.render(label, True, NORMAL_FONT_COLOR_NETWORK_INFO_LABEL)
        surface.blit(label_surf, (x, y))
        if value:
            value_surf = NORMAL_FONT.render(value, True, NORMAL_FONT_COLOR_NETWORK_INFO_VALUE)
            value_x = x + 160
            surface.blit(value_surf, (value_x, y))


#    Dibuja el gráfico de fitness histórico en la parte inferior derecha
def draw_fitness_graph(surface):

    panel_width = SCREEN_WIDTH // 2 - MARGIN * 1.5
    panel_x = SCREEN_WIDTH // 2 + MARGIN // 2
    panel_y = STATS_PANEL_HEIGHT + MAIN_GAME_HEIGHT + MARGIN * 3
    graph_panel = pygame.Rect(panel_x, panel_y, panel_width, BOTTOM_PANEL_HEIGHT)
    draw_panel(surface, graph_panel)
    title_rect = pygame.Rect(graph_panel.left, graph_panel.top, graph_panel.width, 40)
    draw_header(surface, title_rect, "Histórico de Fitness")

    if not generation_fitnesses:
        msg_surf = TITLE_FONT.render("No hay datos de fitness disponibles", True, TITLE_FONT_COLOR_GRAPH_NO_DATA)
        msg_x = graph_panel.left + (graph_panel.width - msg_surf.get_width()) // 2
        msg_y = graph_panel.top + (graph_panel.height - msg_surf.get_height()) // 2
        surface.blit(msg_surf, (msg_x, msg_y))
        return

    fig_width = (graph_panel.width - PADDING * 2) / 100
    fig_height = (graph_panel.height - title_rect.height - PADDING * 2) / 100

    # Colores para Matplotlib (0-1 range)
    plot_line_color_mpl = tuple(c / 255 for c in HIGHLIGHT_COLOR)
    plot_trend_color_mpl = '#e74c3c'  # Rojo para la tendencia
    plot_avg_line_color_mpl = '#27ae60'  # Verde para promedio
    plot_grid_color_mpl = '#cccccc'
    plot_text_color_mpl = tuple(c / 255 for c in NORMAL_FONT_COLOR_NETWORK_INFO_VALUE)  # Color oscuro
    plot_bg_color_mpl = tuple(c / 255 for c in PANEL_BG)  # Fondo del gráfico similar al panel

    fig = plt.figure(figsize=(fig_width, fig_height), dpi=100, facecolor=plot_bg_color_mpl)  # Usar color de fondo
    ax = fig.add_subplot(111, facecolor=plot_bg_color_mpl)  # Usar color de fondo para el área del plot

    ax.plot(range(1, len(generation_fitnesses) + 1), generation_fitnesses, color=plot_line_color_mpl, marker='o',
            markersize=4, linewidth=2)
    if len(generation_fitnesses) > 1:
        z = np.polyfit(range(1, len(generation_fitnesses) + 1), generation_fitnesses, 1)
        p = np.poly1d(z)
        trend_x = np.array(range(1, len(generation_fitnesses) + 1))
        ax.plot(trend_x, p(trend_x), linestyle='--', color=plot_trend_color_mpl, alpha=0.7, linewidth=1.5)

    ax.set_xlabel('Generación', fontsize=9, color=plot_text_color_mpl)
    ax.set_ylabel('Mejor Fitness', fontsize=9, color=plot_text_color_mpl)
    ax.tick_params(axis='both', which='major', labelsize=8, colors=plot_text_color_mpl)
    ax.grid(True, linestyle='--', alpha=0.4, color=plot_grid_color_mpl)

    # Color de los ejes (spines)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color(plot_text_color_mpl)
    ax.spines['left'].set_color(plot_text_color_mpl)

    max_fitness_val = max(generation_fitnesses) if generation_fitnesses else 10
    ax.set_ylim(0, max(10, max_fitness_val * 1.2))

    if len(generation_fitnesses) >= 5:
        last_5_avg = sum(generation_fitnesses[-5:]) / 5
        ax.axhline(y=last_5_avg, color=plot_avg_line_color_mpl, linestyle='--', alpha=0.5)
        ax.text(
            0.05, 0.92, f"Prom. 5 Gen: {last_5_avg:.1f}", transform=ax.transAxes,
            color=plot_text_color_mpl,  # Color del texto del promedio
            bbox=dict(facecolor=plot_bg_color_mpl, alpha=0.8, boxstyle='round,pad=0.3', edgecolor=plot_grid_color_mpl)
        )
    plt.tight_layout()
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()
    size = canvas.get_width_height()
    surf = pygame.image.frombuffer(raw_data, size, "RGBA")
    surface.blit(surf, (graph_panel.left + PADDING, title_rect.bottom + PADDING))
    plt.close(fig)


#    Dibuja un panel de mensaje cuando no hay juegos activos
def draw_message_panel(surface, message, submessage=""):

    main_game_x = (SCREEN_WIDTH - MAIN_GAME_WIDTH) // 2
    main_game_y = STATS_PANEL_HEIGHT + MARGIN * 2
    message_panel_rect = pygame.Rect(main_game_x, main_game_y, MAIN_GAME_WIDTH, MAIN_GAME_HEIGHT)
    draw_panel(surface, message_panel_rect)

    msg_surf = LARGE_FONT.render(message, True, LARGE_FONT_COLOR_MESSAGE_MAIN)
    msg_x = message_panel_rect.left + (message_panel_rect.width - msg_surf.get_width()) // 2
    msg_y = message_panel_rect.top + (message_panel_rect.height - msg_surf.get_height()) // 2 - (
        msg_surf.get_height() // 4 if submessage else 0)
    surface.blit(msg_surf, (msg_x, msg_y))

    if submessage:

        sub_surf = TITLE_FONT.render(submessage, True, TITLE_FONT_COLOR_MESSAGE_SUBTEXT)
        sub_x = message_panel_rect.left + (message_panel_rect.width - sub_surf.get_width()) // 2
        sub_y = msg_y + msg_surf.get_height() + PADDING // 2
        surface.blit(sub_surf, (sub_x, sub_y))




# FUNCIÓN PRINCIPAL PARA DIBUJAR TODA LA INTERFAZ




#    Dibuja toda la interfaz de usuario con los juegos y estadísticas
def draw_interface(surface, games_list):

    surface.fill(BG_COLOR)

    draw_stats_panel(surface)

    if games_list:
        draw_main_game(surface, games_list[0])
        draw_left_mini_games(surface, games_list)
        draw_right_mini_games(surface, games_list)
    else:
        draw_message_panel(surface, "¡Todos los pájaros murieron!", "Pasando a la siguiente generación...")
    draw_network_info(surface)

    draw_fitness_graph(surface)

    pygame.display.update()




# FUNCIONES PRINCIPALES DE EJECUCIÓN




#    Evalúa cada genoma ejecutando el juego con la red neuronal controlando al pájaro.
def eval_genomes(genomes_list, config):

    global generation, best_fitness, generation_fitnesses, all_time_best_genome
    global games, generation_best_fitness  # 'games' es la lista global de instancias de FlappyBird

    nets = []
    # games = [] # Esta línea se elimina para usar la variable global 'games'
    ge = []

    games.clear()  # Limpiar la lista de juegos de la generación anterior

    generation += 1
    generation_best_fitness = 0

    for genome_id, genome_obj in genomes_list:
        net = neat.nn.FeedForwardNetwork.create(genome_obj, config)
        nets.append(net)
        games.append(FlappyBird())
        genome_obj.fitness = 0
        ge.append(genome_obj)

    run = True
    clock = pygame.time.Clock()

    active_indices = list(range(len(games)))

    while run and len(games) > 0:

        clock.tick(100)  # Ajustar FPS según sea necesario

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                exit()

        # Iterar hacia atrás para poder eliminar elementos de forma segura
        for i_idx in range(len(games) - 1, -1, -1):

            game_instance = games[i_idx]
            genome_instance = ge[i_idx]
            net_instance = nets[i_idx]

            if not game_instance.pipes:  # Si no hay tuberías, el pájaro podría estar esperando para empezar
                output = net_instance.activate((0.5, 0.5, 0.5, 0))  # Salto por defecto o input neutral
                if output[0] > 0.5:
                    game_instance.bird.jump()  # Permitir saltar incluso antes de las tuberías
                game_instance.update()  # Actualizar para que aparezcan tuberías
                continue  # Saltar el resto de la lógica si no hay tuberías aún

            pipe_ind = 0
            if len(game_instance.pipes) > 1 and game_instance.bird.x > game_instance.pipes[0].x + game_instance.pipes[
                0].PIPE_TOP.get_width():
                pipe_ind = 1

            # Normalizar inputs para la red neuronal
            bird_y_norm = game_instance.bird.y / MAIN_GAME_HEIGHT
            dist_to_top_pipe_norm = abs(game_instance.bird.y - game_instance.pipes[pipe_ind].height) / MAIN_GAME_HEIGHT
            dist_to_bottom_pipe_norm = abs(
                game_instance.bird.y - game_instance.pipes[pipe_ind].bottom) / MAIN_GAME_HEIGHT
            bird_vel_norm = game_instance.bird.vel / 30  # Velocidad máxima

            inputs = (
                np.clip(bird_y_norm, 0, 1),
                np.clip(dist_to_top_pipe_norm, 0, 1),
                np.clip(dist_to_bottom_pipe_norm, 0, 1),
                np.clip(bird_vel_norm, -1, 1)
            )

            output = net_instance.activate(inputs)
            if output[0] > 0.5:
                game_instance.bird.jump()

            result = game_instance.update()

            # Fitness: recompensa por sobrevivir y por pasar tuberías
            genome_instance.fitness += 0.5  # Recompensa por seguir vivo
            if game_instance.score > (
                    genome_instance.fitness - 0.1 * game_instance.bird.tick_count) / 5:  # Ajustar para que el score sea el factor principal
                genome_instance.fitness = game_instance.score * 5

            if genome_instance.fitness > generation_best_fitness:
                generation_best_fitness = genome_instance.fitness

            if result == "dead":
                nets.pop(i_idx)
                ge.pop(i_idx)
                games.pop(i_idx)

        # Ordenar los juegos restantes por fitness (opcional, para que games[0] sea el mejor)
        # Esto es costoso si se hace cada frame. Es mejor hacerlo solo si es necesario para la visualización.
        # Si `draw_main_game` siempre toma `games[0]`, y `games` es la lista global que se modifica,
        # es importante que `games[0]` sea representativo o el mejor.
        # Por ahora, se asume que el orden se mantiene o no es crítico para `games[0]` ser el "mejor" vivo.
        # Una forma de asegurar que el "mejor" se muestra en el juego principal es encontrarlo explícitamente:
        # current_best_game_for_display = max(games, key=lambda g: g.genome_ref.fitness) if games else None
        # Y luego pasar `current_best_game_for_display` a `draw_main_game`.
        # Pero para simplificar, mantendremos la estructura actual.

        draw_interface(WINDOW, games)  # Pasar la lista global 'games'

    # Después de la generación
    if generation_best_fitness > best_fitness:
        best_fitness = generation_best_fitness
        # Encontrar el mejor genoma de esta generación para guardarlo como `all_time_best_genome`
        # `ge` ahora puede estar vacío o no contener al mejor si todos murieron.
        # Es mejor iterar sobre los genomas originales de `genomes_list` que NEAT nos pasó.
        current_gen_best_genome = None
        for genome_id, genome_obj in genomes_list:  # Usar la lista original de genomas de la generación
            if genome_obj.fitness == best_fitness:  # O el `generation_best_fitness`
                current_gen_best_genome = genome_obj
                break  # Encontramos uno

        if current_gen_best_genome:
            if all_time_best_genome is None or current_gen_best_genome.fitness > all_time_best_genome.fitness:
                all_time_best_genome = current_gen_best_genome
                with open("best_genome.pickle", "wb") as f:  # Cambiado a best_genome.pickle
                    pickle.dump(all_time_best_genome, f)

    generation_fitnesses.append(generation_best_fitness)


#    Ejecuta el algoritmo NEAT con el archivo de configuración dado.
def run_neat(config_path):

    global all_time_best_genome  # Para accederlo después si es necesario

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 100)    #    ----------    20 generaciones    ----------

    print('\nMejor genoma encontrado por NEAT:\n{!s}'.format(winner))
    with open("winner_genome.pickle", "wb") as f:  # Guardar el ganador final de NEAT
        pickle.dump(winner, f)

    # Opcional: guardar el mejor de todos los tiempos si es diferente al 'winner' de p.run
    # (esto ya se hace en eval_genomes con 'best_genome.pickle')

    if 'draw_net' in globals() and callable(draw_net):
        draw_net(config, winner, True, filename="winner_network.svg")  # Guardar como SVG
    if 'plot_stats' in globals() and callable(plot_stats):
        plot_stats(stats, ylog=False, view=True, filename="fitness_history.svg")


#    Ejecuta el genoma ganador en el juego para mostrar su rendimiento.
def run_winner(config_path, genome_path="winner_genome.pickle"):
    config = neat.config.Config(
        neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path
    )
    try:
        with open(genome_path, "rb") as f:
            genome = pickle.load(f)
    except FileNotFoundError:
        print(f"Archivo de genoma ganador '{genome_path}' no encontrado. Ejecuta el entrenamiento primero.")
        return

    net = neat.nn.FeedForwardNetwork.create(genome, config)
    game_instance = FlappyBird()  # Instancia única para el ganador

    # Para mostrar al ganador, podríamos reutilizar draw_interface de forma simplificada
    # o tener una función de dibujo específica para el ganador.
    # Por ahora, usaremos una versión simplificada del bucle de juego.

    run = True
    clock = pygame.time.Clock()

    # Configurar una pequeña lista de 'juegos' para draw_interface
    winner_display_games = [game_instance]
    # Asignar el genoma a la instancia del juego si FlappyBird lo usa (ej. para fitness display)
    game_instance.genome_ref = genome # Si es necesario

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                exit()

        if not game_instance.pipes:
            game_instance.update()  # Actualizar para que aparezcan tuberías
            # Dibujar estado inicial antes de que comience la acción
            WINDOW.fill(BG_COLOR)
            draw_main_game(WINDOW, game_instance)  # Mostrar el juego del ganador
            pygame.display.update()
            continue

        pipe_ind = 0
        if len(game_instance.pipes) > 1 and game_instance.bird.x > game_instance.pipes[0].x + game_instance.pipes[
            0].PIPE_TOP.get_width():
            pipe_ind = 1

        bird_y_norm = game_instance.bird.y / MAIN_GAME_HEIGHT
        dist_to_top_pipe_norm = abs(game_instance.bird.y - game_instance.pipes[pipe_ind].height) / MAIN_GAME_HEIGHT
        dist_to_bottom_pipe_norm = abs(game_instance.bird.y - game_instance.pipes[pipe_ind].bottom) / MAIN_GAME_HEIGHT
        bird_vel_norm = game_instance.bird.vel / 10

        inputs = (
            np.clip(bird_y_norm, 0, 1),
            np.clip(dist_to_top_pipe_norm, 0, 1),
            np.clip(dist_to_bottom_pipe_norm, 0, 1),
            np.clip(bird_vel_norm, -1, 1)
        )
        output = net.activate(inputs)
        if output[0] > 0.5:
            game_instance.bird.jump()

        result = game_instance.update()
        if result == "dead":
            print(f"El ganador ha muerto. Puntuación final: {game_instance.score}")
            # Pausa antes de cerrar o reiniciar
            time.sleep(2)
            run = False
            break

            # Dibujar la interfaz para el ganador
        # Se podría llamar a una versión simplificada de draw_interface
        # o solo dibujar el juego principal.
        WINDOW.fill(BG_COLOR)
        # Podríamos añadir un texto indicando que es el ganador.
        winner_text_surf = TITLE_FONT.render("DEMO DEL GANADOR", True, SUCCESS_COLOR)
        WINDOW.blit(winner_text_surf,
                    (SCREEN_WIDTH // 2 - winner_text_surf.get_width() // 2, MARGIN + STATS_PANEL_HEIGHT - 60))

        draw_main_game(WINDOW, game_instance)  # Mostrar el juego del ganador
        # Opcionalmente, mostrar info de la red del ganador si se desea.
        pygame.display.update()

    print("Demostración del ganador finalizada.")




#    Punto de entrada principal para ejecutar el entrenamiento NEAT y la demostración del ganador.
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_file_path = os.path.join(local_dir, "config.txt")

    # Verificar si el archivo de configuración existe
    if not os.path.exists(config_file_path):
        print(f"Error: Archivo de configuración '{config_file_path}' no encontrado.")
        print("Asegúrate de tener un archivo 'config.txt' en el mismo directorio que el script.")
        pygame.quit()
        exit()

    # Verificar si los módulos 'game' y 'visualize' están disponibles
    try:
        # Esta es una forma simple de verificar si se pueden importar,
        # no garantiza que tengan las funciones/clases esperadas.
        import game
        import visualize
    except ImportError as e:
        print(f"Error al importar módulos necesarios: {e}")
        print("Asegúrate de que 'game.py' y 'visualize.py' están en el mismo directorio o en PYTHONPATH.")
        pygame.quit()
        exit()

    run_neat(config_file_path)
    # Preguntar al usuario si quiere ver la demo del ganador
    show_winner_demo = input("¿Ejecutar demostración del genoma ganador? (s/n): ")
    if show_winner_demo.lower() == 's':
        run_winner(config_file_path, genome_path="winner_genome.pickle")  # Usar el guardado por p.run
    # O para el mejor de todos los tiempos (si se guardó):
    run_winner(config_file_path, genome_path="best_genome.pickle")

    pygame.quit()
    exit()