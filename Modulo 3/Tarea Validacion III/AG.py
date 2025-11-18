import random
import math
from typing import List, Tuple


class Municipality:
    """Representa una ciudad con coordenadas (x, y).

    Aporta método para calcular distancia euclidiana a otra ciudad.
    """

    def __init__(self, x: float, y: float, name: str = "") -> None:
        self.x = float(x)
        self.y = float(y)
        self.name = name

    def distance(self, other: "Municipality") -> float:
        """Devuelve la distancia euclidiana a `other`."""
        return math.hypot(self.x - other.x, self.y - other.y)

    def __repr__(self) -> str:
        if self.name:
            return f"{self.name}({self.x:.4f},{self.y:.4f})"
        return f"({self.x:.4f},{self.y:.4f})"


class Fitness:
    """Calcula y almacena la distancia y la aptitud de una ruta (individuo).

    La aptitud se define como 1 / distancia_total, por eso se debe garantizar
    que la distancia no sea 0 (no sucede en rutas con >=2 ciudades). """

    def __init__(self, route: List[Municipality]) -> None:
        self.route = route
        self._distance = None
        self._fitness = None

    def distance(self) -> float:
        """Calcula la distancia total recorriendo la ruta y volviendo al inicio."""
        if self._distance is None:
            total = 0.0
            for i in range(len(self.route)):
                start_city = self.route[i]
                next_city = self.route[(i + 1) % len(self.route)]
                total += start_city.distance(next_city)
            self._distance = total
        return self._distance

    def fitness(self) -> float:
        """Devuelve la aptitud como inverso de la distancia.

        Si la distancia fuese 0 (caso excepcional), devolvemos una aptitud muy alta.
        """
        if self._fitness is None:
            dist = self.distance()
            self._fitness = 1.0 / dist if dist > 0 else float('inf')
        return self._fitness


# -------------------- Operaciones sobre población --------------------

def create_route(city_list: List[Municipality]) -> List[Municipality]:
    """Crea una ruta aleatoria (permuta) a partir de la lista de ciudades."""
    return random.sample(city_list, len(city_list))


def initial_population(pop_size: int, city_list: List[Municipality]) -> List[List[Municipality]]:
    """Genera la población inicial compuesta por `pop_size` rutas."""
    return [create_route(city_list) for _ in range(pop_size)]


def rank_routes(population: List[List[Municipality]]) -> List[Tuple[int, float]]:
    """Devuelve una lista de tuplas (índice_individuo, aptitud) ordenada descendentemente por aptitud."""
    fitness_results = [(i, Fitness(ind).fitness()) for i, ind in enumerate(population)]
    fitness_results.sort(key=lambda x: x[1], reverse=True)
    return fitness_results


def selection(pop_ranked: List[Tuple[int, float]], elite_size: int) -> List[int]:
    """Selecciona índices de la población para reproducirse.

    - Mantiene elite_size mejores individuos (elitismo).
    - Resto se selecciona por ruleta proporcional a la aptitud. """
    selection_results = []

    # Elitismo directo
    for i in range(elite_size):
        selection_results.append(pop_ranked[i][0])

    # Preparar ruleta: calcular suma de aptitudes y probabilidades acumuladas
    fitness_sum = sum([f for _, f in pop_ranked])
    probs = []
    cum = 0.0
    for _, f in pop_ranked:
        # proteger división por cero
        p = (f / fitness_sum) if fitness_sum > 0 else 0
        cum += p
        probs.append(cum)

    # Seleccionar el resto mediante ruleta
    for _ in range(len(pop_ranked) - elite_size):
        r = random.random()
        for idx, cum_prob in enumerate(probs):
            if r <= cum_prob:
                selection_results.append(pop_ranked[idx][0])
                break

    return selection_results


def mating_pool(population: List[List[Municipality]], selection_results: List[int]) -> List[List[Municipality]]:
    """Construye el pool de apareamiento devolviendo las rutas seleccionadas por índice."""
    return [population[i] for i in selection_results]


def breed(parent1: List[Municipality], parent2: List[Municipality]) -> List[Municipality]:
    """Cruza dos padres con un `order crossover` sencillo (preserva orden relativo).

    Elegimos dos puntos y copiamos el tramo del padre1, luego rellenamos con el orden
    de padre2 sin duplicados. """
    child = [None] * len(parent1)

    start = random.randint(0, len(parent1) - 1)
    end = random.randint(0, len(parent1) - 1)

    if start > end:
        start, end = end, start

    # Copiar segmento del padre1
    for i in range(start, end + 1):
        child[i] = parent1[i]

    # Rellenar con ciudades del padre2 en orden
    parent2_idx = 0
    for i in range(len(child)):
        if child[i] is None:
            while parent2[parent2_idx] in child:
                parent2_idx += 1
            child[i] = parent2[parent2_idx]

    return child


def breed_population(matingpool: List[List[Municipality]], elite_size: int) -> List[List[Municipality]]:
    """Genera la nueva población cruzando.

    Los elite_size primeros se copian directamente.
    El resto se obtiene cruzando padres (tomados aleatoriamente del pool). """
    children = []
    length = len(matingpool) - elite_size
    pool = random.sample(matingpool, len(matingpool))

    # Copiar élites
    for i in range(elite_size):
        children.append(matingpool[i])

    # Cruces
    for i in range(length):
        child = breed(pool[i], pool[len(matingpool) - i - 1])
        children.append(child)

    return children


def mutate(individual: List[Municipality], mutation_rate: float) -> List[Municipality]:
    """Aplica mutación por swap (intercambio de dos genes) con probabilidad mutation_rate por posición."""
    for swapped in range(len(individual)):
        if random.random() < mutation_rate:
            swap_with = int(random.random() * len(individual))

            individual[swapped], individual[swap_with] = individual[swap_with], individual[swapped]
    return individual


def mutate_population(population: List[List[Municipality]], mutation_rate: float) -> List[List[Municipality]]:
    return [mutate(ind.copy(), mutation_rate) for ind in population]


def next_generation(current_gen: List[List[Municipality]], elite_size: int, mutation_rate: float) -> List[List[Municipality]]:
    """Genera la siguiente generación a partir de la actual."""
    pop_ranked = rank_routes(current_gen)
    selection_results = selection(pop_ranked, elite_size)
    matingpool = mating_pool(current_gen, selection_results)
    children = breed_population(matingpool, elite_size)
    next_gen = mutate_population(children, mutation_rate)
    return next_gen


def genetic_algorithm(city_list: List[Municipality], population_size: int, elite_size: int,
                      mutation_rate: float, generations: int, verbose: bool = True) -> List[Municipality]:
    """Evoluciona una población y devuelve la mejor ruta encontrada."""
    pop = initial_population(population_size, city_list)

    if verbose:
        initial_distance = 1.0 / rank_routes(pop)[0][1]
        print(f"Distancia inicial: {initial_distance:.4f}")

    for i in range(generations):
        pop = next_generation(pop, elite_size, mutation_rate)

        if verbose and (i + 1) % max(1, generations // 10) == 0:
            best_distance = 1.0 / rank_routes(pop)[0][1]
            print(f"Generación {i+1:4d} mejor distancia: {best_distance:.4f}")

    best_index = rank_routes(pop)[0][0]
    best_route = pop[best_index]

    if verbose:
        final_distance = 1.0 / rank_routes(pop)[0][1]
        print(f"Distancia final: {final_distance:.4f}")

    return best_route


# -------------------- Ejemplo de uso (main) --------------------

if __name__ == "__main__":
    # Ejemplo: lista de ciudades (las coordenadas están en lat/lon, pero para el demo
    # se tratan como coordenadas planas — suficiente para ilustrar el algoritmo).
    city_coords = [
        (40.4168, -3.7038, "Madrid"),
        (41.3784, 2.1925, "Barcelona"),
        (37.3891, -5.9845, "Sevilla"),
        (36.7213, -4.4214, "Malaga"),
        (39.4699, -0.3763, "Valencia")
    ]

    ciudades = [Municipality(x, y, name) for (x, y, name) in city_coords]

    # Parámetros del algoritmo (puedes cambiarlos)
    population_size = 100
    elite_size = 20
    mutation_rate = 0.01
    generations = 500

    mejor = genetic_algorithm(ciudades, population_size, elite_size, mutation_rate, generations)

    print("\nMejor ruta encontrada:")
    print(mejor)
    print("Distancia de la mejor ruta:")
    print(Fitness(mejor).distance())