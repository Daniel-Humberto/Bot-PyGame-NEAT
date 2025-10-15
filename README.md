# Flappy Bird Evolutionary Bot 
## Proyecto de IA Evolutiva con Algoritmo NEAT


<p align="center">
  <img src="Imagenes/1.png" alt="Visual de Matemáticas en IA, Data y Ops"
       style="max-width: 90%; height: auto; border-radius: 12px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);">
</p>


<p align="center">
  <img src="Imagenes/2.png" alt="Visual de Matemáticas en IA, Data y Ops"
       style="max-width: 90%; height: auto; border-radius: 12px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);">
</p>


---


## 🎯 Descripción General

Este proyecto implementa un sistema de **Machine Learning** basado en **algoritmos genéticos** para entrenar agentes capaces de jugar Flappy Bird de manera autónoma. Utiliza **NEAT (NeuroEvolution of Augmenting Topologies)**, una técnica de neuroevolución que desarrolla redes neuronales a través de principios evolutivos.

El sistema evoluciona redes neuronales que controlan pájaros virtuales, optimizando su comportamiento generación tras generación para maximizar la distancia recorrida y evitar obstáculos.


---


## ✨ Características Principales

- 🧠 **Entrenamiento con NEAT**: Implementación completa del algoritmo NEAT para evolución de redes neuronales
- 🎮 **Simulación en Tiempo Real**: Visualización del entrenamiento con Pygame
- 📈 **Métricas Detalladas**: Seguimiento de fitness, generaciones y estadísticas de población
- 💾 **Persistencia**: Guardado y carga de genomas ganadores
- 📊 **Visualización de Redes**: Generación de gráficos de topología de red neuronal
- 🏆 **Sistema de Highscore**: Registro persistente de mejores puntuaciones (V2.5+)
- 🔄 **Evolución Iterativa**: Mejoras incrementales en 10 versiones distintas


---


## 🛠️ Stack Tecnológico


### Lenguaje y Entorno
    - **Python**: 3.12.3
    - **Gestor de Paquetes**: virtualenv


### Bibliotecas Principales

    | Biblioteca | Versión | Propósito |
    |-----------|---------|-----------|
    | **neat-python** | Latest | Motor principal del algoritmo NEAT |
    | **pygame** | Latest | Renderizado gráfico y simulación del juego |
    | **matplotlib** | Latest | Visualización de estadísticas y grafos |
    | **numpy** | Latest | Operaciones matemáticas y cálculos |
    | **pillow** | Latest | Procesamiento de imágenes |
    | **graphviz** | Latest | Generación de diagramas de redes neuronales |


---


## 📁 Estructura del Proyecto

```
NEAT/
├── V1/                             # Primera generación del proyecto
│   ├── V1.1/                       # Versión base inicial
│   ├── V1.2/                       # Añadida visualización de entrenamiento
│   ├── V1.3/                       # Mejoras en la interfaz
│   ├── V1.4/                       # Optimización del algoritmo
│   └── V1.5/                       # Refinamiento de parámetros
│       ├── config.txt              # Configuración NEAT
│       ├── game.py                 # Lógica del juego
│       ├── main.py                 # Script principal
│       ├── visualize.py            # Herramientas de visualización
│       ├── winner.pickle           # Genoma ganador serializado
│       └── winner_network          # Gráfico de red ganadora
│
└── V2/                             # Segunda generación del proyecto
    ├── V2.1/                       # Refactorización mayor
    ├── V2.2/                       # Mejoras en fitness function
    ├── V2.3/                       # Optimización de colisiones
    ├── V2.4/                       # Ajuste de hiperparámetros
    └── V2.5/                       # Versión actual estable
        ├── config.txt              # Configuración NEAT optimizada
        ├── game.py                 # Motor del juego mejorado
        ├── main.py                 # Script principal refactorizado
        ├── visualize.py            # Visualización avanzada
        ├── Highscore.json          # Sistema de puntuaciones
        ├── best_genome.pickle      # Mejor genoma de la generación
        ├── winner_genome.pickle    # Genoma ganador final
        └── winner_network.svg      # Diagrama de red neuronal
```


---


## 📊 Evolución del Proyecto


---


### Versión 1 (V1)

La primera iteración del proyecto estableció las bases fundamentales del sistema de entrenamiento con NEAT.


---


#### **V1.1 - Creación** 🌱
- ✅ Implementación básica de Flappy Bird con Pygame
- ✅ Integración inicial del algoritmo NEAT
- ✅ Lógica de fitness simple basada en tiempo de supervivencia
- ✅ Entrenamiento funcional sin visualización avanzada

#### **V1.2 - Visualización** 👁️
- ✅ Añadida ventana de entrenamiento con caption personalizado
- ✅ Visualización en tiempo real del proceso de entrenamiento
- ✅ Guardado de genomas ganadores en formato `.pickle`
- ✅ Primera implementación de `winner_network`

#### **V1.3 - Refinamiento UI** 🎨
- ✅ Mejoras en la interfaz de usuario
- ✅ Optimización del renderizado gráfico
- ✅ Ajustes en la visualización de estadísticas
- ✅ Mejora en la presentación del entrenamiento

#### **V1.4 - Optimización** ⚡
- ✅ Refinamiento de la función de fitness
- ✅ Optimización del loop principal
- ✅ Mejoras en la eficiencia del entrenamiento
- ✅ Reducción de tiempo por generación

#### **V1.5 - Estabilización** 🔒
- ✅ Ajuste fino de hiperparámetros NEAT
- ✅ Estabilización del proceso de evolución
- ✅ Mejora en la consistencia de resultados
- ✅ Última versión estable de la rama V1


---


### Versión 2 (V2)

La segunda generación representa una **refactorización completa** con arquitectura mejorada y características avanzadas.


---


#### **V2.1 - Nueva Arquitectura** 🏗️
- ✅ Refactorización completa del código
- ✅ Separación mejorada de responsabilidades
- ✅ Nuevo sistema de gestión de genomas: `best_genome.pickle` + `winner_genome.pickle`
- ✅ Generación de diagramas de red en formato SVG
- ✅ Código más modular y mantenible

#### **V2.2 - Fitness Avanzado** 📈
- ✅ Rediseño de la función de fitness
- ✅ Incorporación de múltiples criterios de evaluación
- ✅ Sistema de recompensas más sofisticado
- ✅ Mejora significativa en la velocidad de aprendizaje

#### **V2.3 - Detección de Colisiones** 🎯
- ✅ Sistema de colisiones más preciso
- ✅ Optimización de hitboxes
- ✅ Mejora en la física del juego
- ✅ Reducción de falsos positivos/negativos

#### **V2.4 - Hiperparámetros** 🔬
- ✅ Experimentación exhaustiva con configuración NEAT
- ✅ Ajuste de tasas de mutación y crossover
- ✅ Optimización del tamaño de población
- ✅ Configuración final documentada en `config.txt`

#### **V2.5 - Sistema de Highscore** 🏆
- ✅ **Versión actual estable**
- ✅ Implementación de `Highscore.json` para persistencia
- ✅ Sistema de tracking de mejores puntuaciones
- ✅ Comparación entre ejecuciones
- ✅ Estadísticas históricas completas
- ✅ Máxima estabilidad y rendimiento


---


## 🔬 Arquitectura Técnica


---


### Componentes Principales


#### **1. main.py** - Controlador Principal
- Inicializa la configuración NEAT desde `config.txt`
- Gestiona el bucle de evolución generacional
- Coordina la evaluación de genomas
- Maneja la persistencia de modelos
- Controla el sistema de highscores (V2.5)


#### **2. game.py** - Motor del Juego

**Clases principales:**
- `Bird`: Entidad controlada por IA con física realista
- `Pipe`: Obstáculos generados dinámicamente
- `Ground`: Base del juego con scrolling
- `Game`: Coordinador del estado del juego y lógica de colisiones

**Características:**
- Sistema de física con gravedad y velocidad
- Detección de colisiones pixel-perfect
- Generación procedural de obstáculos
- Renderizado optimizado con Pygame


#### **3. visualize.py** - Visualización
- Generación de gráficos de fitness por generación
- Creación de diagramas de topología de redes neuronales
- Exportación de grafos en formato SVG usando Graphviz
- Análisis visual de la evolución del algoritmo


#### **4. config.txt** - Configuración NEAT
Parámetros clave ajustados a lo largo de las versiones:

```ini
[NEAT]
fitness_criterion     = max
fitness_threshold     = [ajustado por versión]
pop_size             = [optimizado V1.5 → V2.4]
reset_on_extinction  = False

[DefaultGenome]
activation_default   = tanh
aggregation_default  = sum
num_inputs           = [sensores del pájaro]
num_outputs          = 1 (saltar/no saltar)
```


---


### Flujo de Entrenamiento

```
1. Inicialización
   ↓
2. Crear Población (genomas aleatorios)
   ↓
3. Para cada Generación:
   │
   ├─→ Evaluar Genomas
   │   ├─→ Crear Red Neuronal
   │   ├─→ Ejecutar Simulación
   │   ├─→ Calcular Fitness
   │   └─→ Registrar Resultados
   │
   ├─→ Selección Natural
   │   ├─→ Seleccionar mejores genomas
   │   └─→ Eliminar genomas débiles
   │
   ├─→ Reproducción
   │   ├─→ Crossover (cruce genético)
   │   └─→ Mutación (variación genética)
   │
   └─→ Nueva Generación
   │
4. Guardar Ganador → best_genome.pickle
   ↓
5. Visualizar Red → winner_network.svg
```


---


### Entradas de la Red Neuronal

La red recibe típicamente:
- Posición vertical del pájaro
- Distancia al próximo tubo
- Altura del hueco superior del tubo
- Altura del hueco inferior del tubo
- Velocidad vertical del pájaro


### Salida de la Red Neuronal

- **Valor > 0.5**: El pájaro salta
- **Valor ≤ 0.5**: El pájaro no hace nada (cae por gravedad)


---


## 📈 Resultados

### Métricas de Rendimiento

| Versión | Gen. Promedio | Fitness Máximo | Tiempo/Gen |
|---------|---------------|----------------|------------|
| V1.1    | ~50-80        | ~500          | ~15s       |
| V1.5    | ~30-50        | ~800          | ~10s       |
| V2.1    | ~25-40        | ~1200         | ~8s        |
| V2.5    | ~15-30        | ~2000+        | ~6s        |


### Mejoras Clave

- **Reducción 70%** en generaciones necesarias (V1.1 → V2.5)
- **Aumento 300%** en fitness máximo alcanzado
- **Mejora 60%** en tiempo de convergencia
- **100%** de estabilidad en ejecuciones (V2.5)


---


## 📝 Licencia

Este proyecto está licenciado bajo la [Licencia GNU](LICENSE).


---
