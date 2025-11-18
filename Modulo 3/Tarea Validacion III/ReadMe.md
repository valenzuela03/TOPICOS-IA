Este archivo contiene una implementación modular, documentada y corregida
de un Algoritmo Genético para el problema del viajante (TSP).


Contenido:
- Clases: Municipality, Fitness
- Funciones: creación de ruta, población inicial, ranking, selección,
cruce, mutación (swap), y flujo del algoritmo genético.


Parámetros que puedes modificar desde main():
- population_size: tamaño de la población
- elite_size: número de individuos que pasan directo a la siguiente generación
- mutation_rate: probabilidad de mutación por gen
- generations: número de generaciones a evolucionar


Descripción breve del algoritmo genético:
1. Generar población inicial aleatoria.
2. Evaluar aptitud (fitness) de cada individuo como el inverso de la distancia total.
3. Seleccionar padres por elitismo + ruleta (probabilidad proporcional a la aptitud).
4. Cruzar padres para generar hijos (preservando orden relativo: "order crossover").
5. Aplicar mutación por intercambio (swap) según tasa de mutación.
6. Repetir por el número de generaciones.