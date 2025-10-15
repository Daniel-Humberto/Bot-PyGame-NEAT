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
MAIN_AREA_HEIGHT = SCREEN_HEIGHT - STATS_PANEL_HEIGHT - 40  # Área principal (menos márgenes)


# Dimensiones de los juegos
MAIN_GAME_WIDTH = 640
MAIN_GAME_HEIGHT = 480


# Dimensiones para mini-juegos
MINI_GAME_WIDTH = 160
MINI_GAME_HEIGHT = 120
MINI_GAMES_PER_COLUMN = 9  # 9 mini-juegos por columna (izquierda y derecha)


# Dimensiones para paneles inferiores
BOTTOM_PANEL_HEIGHT = 275


# Márgenes y espaciado
MARGIN = 20
PADDING = 15
WIDGET_SPACING = 10


# Paleta de colores
BG_COLOR = (20, 20, 20)
HIGHLIGHT_COLOR = (40, 40, 40)
PANEL_BG = (60, 60, 60)
BORDER_COLOR =  (255, 255, 255)

TEXT_COLOR = (255, 255, 255)
GRID_COLOR =  (0, 0, 0)
SUCCESS_COLOR = (0, 150, 0)
DANGER_COLOR = (150, 0, 0)
ACCENT_COLOR = (0, 0, 125)




# INICIALIZACIÓN DE PYGAME Y TIPOGRAFÍAS




pygame.init()

# Sistema de tipografías coherente
SMALL_FONT = pygame.font.SysFont("Arial", 15)  #
NORMAL_FONT = pygame.font.SysFont("Arial", 17)  #
STAT_FONT = pygame.font.SysFont("Arial", 20)
HEADER_FONT = pygame.font.SysFont("Arial", 30, bold=True) #
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

    # Dibuja el panel con esquinas redondeadas
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)

    # Dibuja el borde si se solicita
    if border:
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1, border_radius=border_radius)


#    Dibuja un encabezado con texto centrado
def draw_header(surface, rect, text, color=HIGHLIGHT_COLOR, text_color=PANEL_BG):

    # Dibuja el fondo del encabezado
    pygame.draw.rect(surface, color, rect, border_radius=8)

    # Dibuja el texto centrado
    text_surf = HEADER_FONT.render(text, True, text_color)
    text_x = rect.left + (rect.width - text_surf.get_width()) // 2
    text_y = rect.top + (rect.height - text_surf.get_height()) // 2
    surface.blit(text_surf, (text_x, text_y))


#    Dibuja un indicador KPI con etiqueta y valor
def draw_kpi(surface, rect, label, value, value_color=HIGHLIGHT_COLOR):

    # Dibuja el panel de fondo
    draw_panel(surface, rect)

    # Dibuja la etiqueta en la parte superior
    label_surf = STAT_FONT.render(label, True, TEXT_COLOR)
    label_x = rect.left + (rect.width - label_surf.get_width()) // 2
    surface.blit(label_surf, (label_x, rect.top + PADDING))

    # Dibuja el valor más grande debajo
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

    # Calcular posición para centrar el juego principal
    main_game_x = (SCREEN_WIDTH - MAIN_GAME_WIDTH) // 2
    main_game_y = STATS_PANEL_HEIGHT + MARGIN * 2

    # Área del juego principal con su panel
    main_game_rect = pygame.Rect(
        main_game_x,
        main_game_y,
        MAIN_GAME_WIDTH,
        MAIN_GAME_HEIGHT
    )
    draw_panel(surface, main_game_rect)

    # Encabezado para el juego principal
    header_rect = pygame.Rect(
        main_game_rect.left,
        main_game_rect.top,
        main_game_rect.width,
        40
    )
    draw_header(surface, header_rect, "Mejor Bird en Acción")

    # Dibujar el juego con el espacio adecuado
    game_view_rect = (
        main_game_rect.left + PADDING,
        header_rect.bottom + PADDING,
        main_game_rect.width - PADDING * 2,
        main_game_rect.height - header_rect.height - PADDING * 2
    )
    game.draw(surface, game_view_rect)

    # Indicador de puntuación
    score_box = pygame.Rect(
        main_game_rect.left + PADDING,
        main_game_rect.bottom - 60,
        120,
        40
    )
    draw_panel(surface, score_box, ACCENT_COLOR, border=False, border_radius=20)

    score_text = TITLE_FONT.render(f"Score: {game.score}", True, PANEL_BG)
    surface.blit(score_text, (
        score_box.left + (score_box.width - score_text.get_width()) // 2,
        score_box.top + (score_box.height - score_text.get_height()) // 2
    ))


#    Dibuja los mini-juegos de la columna izquierda (birds 1-9)
def draw_left_mini_games(surface, games):

    if len(games) <= 1:
        return

    # Calcular dimensiones de la columna
    column_width = SCREEN_WIDTH // 4
    column_x = MARGIN
    column_y = STATS_PANEL_HEIGHT + MARGIN * 2

    # Panel para los mini-juegos
    column_rect = pygame.Rect(
        column_x,
        column_y,
        column_width - MARGIN,
        MAIN_GAME_HEIGHT
    )
    draw_panel(surface, column_rect)

    # Encabezado de la columna
    header_rect = pygame.Rect(
        column_rect.left,
        column_rect.top,
        column_rect.width,
        40
    )
    draw_header(surface, header_rect, "Birds 1-9")

    # Calcular dimensiones para cada mini-juego
    mini_width = (column_rect.width - PADDING * 4) // 3
    mini_height = (column_rect.height - header_rect.height - PADDING * 4) // 3

    # Dibujar los mini-juegos (máximo 9)
    for i in range(1, min(10, len(games))):
        col = (i - 1) % 3
        row = (i - 1) // 3

        # Calcular posición
        x = column_rect.left + PADDING + col * (mini_width + PADDING)
        y = header_rect.bottom + PADDING + row * (mini_height + PADDING)

        # Dibujar celda
        cell_rect = pygame.Rect(x, y, mini_width, mini_height)
        draw_panel(surface, cell_rect, pygame.Color(248, 248, 248), border_radius=4)

        # Dibujar el mini-juego
        game_view = (
            x + 2,
            y + 2,
            mini_width - 4,
            mini_height - 22
        )
        games[i].draw(surface, game_view)

        # Etiqueta con información del bird
        label_rect = pygame.Rect(
            x,
            y + mini_height - 20,
            mini_width,
            20
        )
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, label_rect, border_radius=4)

        # Texto de la etiqueta
        bird_text = SMALL_FONT.render(f"Bird #{i} | Score: {games[i].score}", True, PANEL_BG)
        text_x = x + (mini_width - bird_text.get_width()) // 2
        surface.blit(bird_text, (text_x, y + mini_height - 18))


#    Dibuja los mini-juegos de la columna derecha (birds 10-18)
def draw_right_mini_games(surface, games):

    if len(games) <= 10:
        return

    # Calcular dimensiones de la columna
    column_width = SCREEN_WIDTH // 4
    column_x = SCREEN_WIDTH - column_width
    column_y = STATS_PANEL_HEIGHT + MARGIN * 2

    # Panel para los mini-juegos
    column_rect = pygame.Rect(
        column_x,
        column_y,
        column_width - MARGIN,
        MAIN_GAME_HEIGHT
    )
    draw_panel(surface, column_rect)

    # Encabezado de la columna
    header_rect = pygame.Rect(
        column_rect.left,
        column_rect.top,
        column_rect.width,
        40
    )
    draw_header(surface, header_rect, "Birds 10-18")

    # Calcular dimensiones para cada mini-juego
    mini_width = (column_rect.width - PADDING * 4) // 3
    mini_height = (column_rect.height - header_rect.height - PADDING * 4) // 3

    # Dibujar los mini-juegos (10-18)
    for i in range(10, min(19, len(games))):
        col = (i - 10) % 3
        row = (i - 10) // 3

        # Calcular posición
        x = column_rect.left + PADDING + col * (mini_width + PADDING)
        y = header_rect.bottom + PADDING + row * (mini_height + PADDING)

        # Dibujar celda
        cell_rect = pygame.Rect(x, y, mini_width, mini_height)
        draw_panel(surface, cell_rect, pygame.Color(248, 248, 248), border_radius=4)

        # Dibujar el mini-juego
        game_view = (
            x + 2,
            y + 2,
            mini_width - 4,
            mini_height - 22
        )
        games[i].draw(surface, game_view)

        # Etiqueta con información del bird
        label_rect = pygame.Rect(
            x,
            y + mini_height - 20,
            mini_width,
            20
        )
        pygame.draw.rect(surface, HIGHLIGHT_COLOR, label_rect, border_radius=4)

        # Texto de la etiqueta
        bird_text = SMALL_FONT.render(f"Bird #{i} | Score: {games[i].score}", True, PANEL_BG)
        text_x = x + (mini_width - bird_text.get_width()) // 2
        surface.blit(bird_text, (text_x, y + mini_height - 18))


#    Dibuja el panel de información de la red neuronal en la parte inferior izquierda
def draw_network_info(surface):

    # Calcular dimensiones del panel
    panel_width = SCREEN_WIDTH // 2 - MARGIN * 1.5
    panel_x = MARGIN
    panel_y = STATS_PANEL_HEIGHT + MAIN_GAME_HEIGHT + MARGIN * 3

    # Panel para información NEAT
    info_panel = pygame.Rect(
        panel_x,
        panel_y,
        panel_width,
        BOTTOM_PANEL_HEIGHT
    )
    draw_panel(surface, info_panel)

    # Título del panel
    title_rect = pygame.Rect(
        info_panel.left,
        info_panel.top,
        info_panel.width,
        50
    )
    draw_header(surface, title_rect, "Configuración NEAT")

    # Información de la red neuronal organizada en columnas
    info_texts = [
        ("Neural Network:", "4 Inputs, 1 Output"),
        ("Inputs:", "Bird height, distances to pipes, velocity"),
        ("Output:", "Jump decision (>0.5 threshold)"),
        ("Population Size:", "50"),
        ("Mutation Rates:", ""),
        ("  - Weight:", "0.8"),
        ("  - Add Node:", "0.2"),
        ("  - Add Connection:", "0.5"),
        ("Fitness Formula:", "Distance + 5 × pipes passed")
    ]

    # Dibujar en dos columnas para mejor organización
    col_width = (info_panel.width - PADDING * 3) // 2
    for i, (label, value) in enumerate(info_texts):
        # Determinar si va en columna 1 o 2
        col = 0 if i < 5 else 1
        row = i if i < 5 else i - 5

        # Calcular posición exacta
        x = info_panel.left + PADDING + col * (col_width + PADDING)
        y = title_rect.bottom + PADDING + row * 28

        # Renderizar etiqueta
        label_surf = NORMAL_FONT.render(label, True, TEXT_COLOR)
        surface.blit(label_surf, (x, y))

        # Renderizar valor
        if value:
            value_surf = NORMAL_FONT.render(value, True, HIGHLIGHT_COLOR)
            value_x = x + 140  # Posición fija para alinear valores
            surface.blit(value_surf, (value_x, y))


#    Dibuja el gráfico de fitness histórico en la parte inferior derecha
def draw_fitness_graph(surface):

    # Calcular dimensiones del panel
    panel_width = SCREEN_WIDTH // 2 - MARGIN * 1.5
    panel_x = SCREEN_WIDTH // 2 + MARGIN // 2
    panel_y = STATS_PANEL_HEIGHT + MAIN_GAME_HEIGHT + MARGIN * 3

    # Panel para el gráfico
    graph_panel = pygame.Rect(
        panel_x,
        panel_y,
        panel_width,
        BOTTOM_PANEL_HEIGHT
    )
    draw_panel(surface, graph_panel)

    # Título del gráfico
    title_rect = pygame.Rect(
        graph_panel.left,
        graph_panel.top,
        graph_panel.width,
        40
    )
    draw_header(surface, title_rect, "Histórico de Fitness")

    # Verificar si hay datos para graficar
    if not generation_fitnesses:
        # Mostrar mensaje si no hay datos
        msg_surf = TITLE_FONT.render("No hay datos de fitness disponibles", True, TEXT_COLOR)
        msg_x = graph_panel.left + (graph_panel.width - msg_surf.get_width()) // 2
        msg_y = graph_panel.top + (graph_panel.height - msg_surf.get_height()) // 2
        surface.blit(msg_surf, (msg_x, msg_y))
        return

    # Crear figura de matplotlib con estilo mejorado
    fig_width = (graph_panel.width - PADDING * 2) / 100
    fig_height = (graph_panel.height - title_rect.height - PADDING * 2) / 100
    fig = plt.figure(figsize=(fig_width, fig_height), dpi=100, facecolor='white')
    ax = fig.add_subplot(111)

    # Convertir colores a formato matplotlib
    highlight_rgb = (HIGHLIGHT_COLOR[0] / 255, HIGHLIGHT_COLOR[1] / 255, HIGHLIGHT_COLOR[2] / 255)

    # Dibujar línea principal
    ax.plot(
        range(1, len(generation_fitnesses) + 1),
        generation_fitnesses,
        color=highlight_rgb,
        marker='o',
        markersize=4,
        linewidth=2
    )

    # Añadir línea de tendencia
    if len(generation_fitnesses) > 1:
        z = np.polyfit(range(1, len(generation_fitnesses) + 1), generation_fitnesses, 1)
        p = np.poly1d(z)
        trend_x = np.array(range(1, len(generation_fitnesses) + 1))
        ax.plot(
            trend_x,
            p(trend_x),
            linestyle='--',
            color='#e74c3c',
            alpha=0.7,
            linewidth=1.5
        )

    # Estilo limpio
    ax.set_xlabel('Generación', fontsize=9)
    ax.set_ylabel('Mejor Fitness', fontsize=9)
    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.grid(True, linestyle='--', alpha=0.4, color='#cccccc')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Rango dinámico del eje Y
    max_fitness = max(generation_fitnesses) if generation_fitnesses else 10
    ax.set_ylim(0, max(10, max_fitness * 1.2))

    # Añadir promedio de últimas 5 generaciones
    if len(generation_fitnesses) >= 5:
        last_5_avg = sum(generation_fitnesses[-5:]) / 5
        ax.axhline(y=last_5_avg, color='#27ae60', linestyle='--', alpha=0.5)
        ax.text(
            0.05, 0.92,
            f"Prom. 5 Gen: {last_5_avg:.1f}",
            transform=ax.transAxes,
            bbox=dict(
                facecolor='white',
                alpha=0.8,
                boxstyle='round,pad=0.3',
                edgecolor='#eeeeee'
            )
        )

    # Maximizar área del gráfico
    plt.tight_layout()

    # Convertir a superficie pygame
    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()
    size = canvas.get_width_height()

    # Crear superficie pygame y dibujarla
    surf = pygame.image.frombuffer(raw_data, size, "RGBA")
    surface.blit(
        surf,
        (
            graph_panel.left + PADDING,
            title_rect.bottom + PADDING
        )
    )

    plt.close(fig)


#    Dibuja un panel de mensaje cuando no hay juegos activos
def draw_message_panel(surface, message, submessage=""):

    # Calcular posición para centrar el mensaje
    main_game_x = (SCREEN_WIDTH - MAIN_GAME_WIDTH) // 2
    main_game_y = STATS_PANEL_HEIGHT + MARGIN * 2

    # Panel principal para mensajes
    message_panel = pygame.Rect(
        main_game_x,
        main_game_y,
        MAIN_GAME_WIDTH,
        MAIN_GAME_HEIGHT
    )
    draw_panel(surface, message_panel)

    # Mensaje principal
    msg_surf = LARGE_FONT.render(message, True, DANGER_COLOR)
    msg_x = message_panel.left + (message_panel.width - msg_surf.get_width()) // 2
    msg_y = message_panel.top + (message_panel.height - msg_surf.get_height()) // 2
    surface.blit(msg_surf, (msg_x, msg_y))

    # Submensaje opcional
    if submessage:
        sub_surf = TITLE_FONT.render(submessage, True, TEXT_COLOR)
        sub_x = message_panel.left + (message_panel.width - sub_surf.get_width()) // 2
        sub_y = msg_y + msg_surf.get_height() + PADDING
        surface.blit(sub_surf, (sub_x, sub_y))




# FUNCIÓN PRINCIPAL PARA DIBUJAR TODA LA INTERFAZ




#    Dibuja toda la interfaz de usuario con los juegos y estadísticas
def draw_interface(surface, games):


    # Limpiar la pantalla
    surface.fill(BG_COLOR)

    # Dibujar el panel de estadísticas en la parte superior
    draw_stats_panel(surface)

    if games:
        # Dibujar juego principal (mejor desempeño) en el centro
        draw_main_game(surface, games[0])

        # Dibujar mini-juegos en la parte izquierda (birds 1-9)
        draw_left_mini_games(surface, games)

        # Dibujar mini-juegos en la parte derecha (birds 10-18)
        draw_right_mini_games(surface, games)
    else:
        # Mostrar mensaje cuando todos los pájaros murieron
        draw_message_panel(
            surface,
            "¡Todos los pájaros murieron!",
            "Pasando a la siguiente generación..."
        )

    # Dibujar panel de información NEAT en la parte inferior izquierda
    draw_network_info(surface)

    # Dibujar gráfico de fitness histórico en la parte inferior derecha
    draw_fitness_graph(surface)

    # Actualizar pantalla
    pygame.display.update()




# FUNCIONES PRINCIPALES DE EJECUCIÓN




#    Evalúa cada genoma ejecutando el juego con la red neuronal controlando al pájaro.
def eval_genomes(genomes, config):

    global generation, best_fitness, generation_fitnesses, all_time_best_genome
    global games, generation_best_fitness

    # Tracking de redes, juegos y genomas
    nets = []
    games = []
    ge = []

    # Nueva generación
    generation += 1
    generation_best_fitness = 0  # Reiniciar para esta generación

    # Crear instancia de juego para cada genoma
    for genome_id, genome in genomes:
        # Crear red para cada genoma
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)

        # Crear juego para este genoma
        games.append(FlappyBird())

        # Inicializar fitness
        genome.fitness = 0
        ge.append(genome)

    # Bucle principal del juego
    run = True
    clock = pygame.time.Clock()

    while run and len(games) > 0:
        # Limitar FPS
        clock.tick(30)

        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # Para cada juego activo, obtener info de tubos y tomar decisiones
        for i, game in enumerate(games):
            # Asegurar que hay tubos antes de continuar
            if not game.pipes:
                continue

            # Obtener índice del tubo más cercano
            pipe_ind = 0
            if len(game.pipes) > 1 and game.bird.x > game.pipes[0].x + game.pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1

            # Inputs para la red neuronal - normalizados a [0, 1]
            inputs = (
                game.bird.y / MAIN_GAME_HEIGHT,  # Posición Y del pájaro
                abs(game.bird.y - game.pipes[pipe_ind].height) / MAIN_GAME_HEIGHT,  # Distancia al tubo superior
                abs(game.bird.y - game.pipes[pipe_ind].bottom) / MAIN_GAME_HEIGHT,  # Distancia al tubo inferior
                game.bird.vel / 10  # Velocidad del pájaro (normalizada)
            )

            # Obtener salida de la red neuronal
            output = nets[i].activate(inputs)

            # Si la salida es > 0.5, el pájaro salta
            if output[0] > 0.5:
                game.bird.jump()

            # Actualizar estado del juego y obtener resultado
            result = game.update()

            # Actualizar fitness
            ge[i].fitness += 0.1  # Pequeña recompensa por seguir vivo

            # Verificar si el pájaro pasó un tubo
            if game.score > 0 and game.score > ge[i].fitness / 5:
                ge[i].fitness = game.score * 5  # Gran recompensa por pasar tubos

            # Actualizar mejor fitness de la generación
            if ge[i].fitness > generation_best_fitness:
                generation_best_fitness = ge[i].fitness

            # Si el pájaro chocó, eliminarlo
            if result == "dead":
                # Eliminar esta instancia de juego
                nets.pop(i)
                ge.pop(i)
                games.pop(i)

        # Dibujar toda la interfaz usando nuestra nueva función centralizada
        draw_interface(WINDOW, games)

    # Actualizar estadísticas después de la generación
    if generation_best_fitness > best_fitness:
        best_fitness = generation_best_fitness

        # Encontrar el mejor genoma de esta generación
        best_genome = None
        best_fitness_val = 0
        for genome in ge:
            if genome.fitness > best_fitness_val:
                best_fitness_val = genome.fitness
                best_genome = genome

        if best_genome and (all_time_best_genome is None or best_fitness_val > all_time_best_genome.fitness):
            all_time_best_genome = best_genome

            # Guardar el mejor genoma
            with open("best.pickle", "wb") as f:
                pickle.dump(best_genome, f)

    generation_fitnesses.append(generation_best_fitness)


#    Ejecuta el algoritmo NEAT con el archivo de configuración dado.
def run_neat(config_path):

    # Cargar configuración
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # Crear población
    p = neat.Population(config)

    # Añadir reportero para mostrar progreso en terminal
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Ejecutar hasta 50 generaciones
    winner = p.run(eval_genomes, 50)

    # Mostrar estadísticas finales
    print('\nMejor genoma:\n{!s}'.format(winner))

    # Guardar el ganador
    with open("winner.pickle", "wb") as f:
        pickle.dump(winner, f)

    # Visualizar la red del ganador
    draw_net(config, winner, True, filename="winner_network")

    # Graficar estadísticas
    plot_stats(stats, ylog=False, view=True)


#    Ejecuta el genoma ganador en el juego para mostrar su rendimiento.
def run_winner(config_path, genome_path="winner.pickle"):

    # Cargar configuración
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    # Cargar el genoma ganador
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    # Crear la red neuronal
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    # Crear juego
    game = FlappyBird()

    # Bucle principal
    run = True
    clock = pygame.time.Clock()

    while run:
        # Limitar FPS
        clock.tick(30)

        # Manejo de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # Verificar que hay tubos
        if not game.pipes:
            continue

        # Obtener información del tubo
        pipe_ind = 0
        if len(game.pipes) > 1 and game.bird.x > game.pipes[0].x + game.pipes[0].PIPE_TOP.get_width():
            pipe_ind = 1

        # Inputs para la red neuronal
        inputs = (
            game.bird.y / MAIN_GAME_HEIGHT,
            abs(game.bird.y - game.pipes[pipe_ind].height) / MAIN_GAME_HEIGHT,
            abs(game.bird.y - game.pipes[pipe_ind].bottom) / MAIN_GAME_HEIGHT,
            game.bird.vel / 10
        )

        # Obtener salida
        output = net.activate(inputs)

        # Saltar si es necesario
        if output[0] > 0.5:
            game.bird.jump()

        # Actualizar juego
        result = game.update()

        # Verificar si terminó
        if result == "dead":
            run = False
            break

        # Dibujar interfaz limpia
        WINDOW.fill(BG_COLOR)




#    Punto de entrada principal para ejecutar el entrenamiento NEAT y la demostración del ganador.
if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    run_neat(config_path)
    run_winner(config_path)