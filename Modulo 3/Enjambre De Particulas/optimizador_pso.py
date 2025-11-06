# optimizador_pso.py

import numpy as np
import pyswarms as ps
from scipy.spatial.distance import cdist 
from procesador_datos import ProcesadorDatos

class OptimizadorPSO:
    """
    Clase para implementar y ejecutar el algoritmo PSO, conteniendo la lógica 
    de la Función de Aptitud (Fitness) para la colocación de sensores.
    """
    def __init__(self, procesador_datos: ProcesadorDatos, n_sensores, w_cultivo, w_suelo, w_cobertura):
        self.dp = procesador_datos
        self.N_SENSORES = n_sensores
        self.D = n_sensores * 2 
        
        self.W_CULTIVO = w_cultivo
        self.W_SUELO = w_suelo
        self.W_COBERTURA = w_cobertura
        
        # Definición de límites (bounds) para PSO - Opción B: Forzar Latitudes reales
        # Esto corrige el problema de las latitudes negativas generadas por el PSO.
        lat_min_real = 25.52  # Mínimo del área de estudio real (Latitud positiva)
        lat_max_real = 25.62  # Máximo del área de estudio real (Latitud positiva)
        
        min_b_lat_lon = []
        max_b_lat_lon = []
        
        # Generar los límites Latitud (forzada) y Longitud (de los datos) para cada sensor
        for _ in range(self.N_SENSORES):
            # Límites mínimos: [Latitud Mínima Forzada, Longitud Mínima de los datos]
            min_b_lat_lon.append(lat_min_real)
            min_b_lat_lon.append(self.dp.min_coords[1]) 
            
            # Límites máximos: [Latitud Máxima Forzada, Longitud Máxima de los datos]
            max_b_lat_lon.append(lat_max_real)
            max_b_lat_lon.append(self.dp.max_coords[1]) 

        self.limites = (np.array(min_b_lat_lon), np.array(max_b_lat_lon))

    def _calcular_aptitud_individual(self, X):
        """Calcula la aptitud para una única posición (partícula)."""
        sensor_coords = X.reshape(self.N_SENSORES, 2)
        
        distancias = cdist(sensor_coords, self.dp.PUNTOS_REF)
        indices_ref_mas_cercano = np.argmin(distancias, axis=1)

        # --- A. FACTOR CULTIVO (Bucle for tradicional) ---
        closest_cultivos = self.dp.REF_CULTIVOS[indices_ref_mas_cercano]
        
        puntuaciones_cultivo_lista = []
        for c in closest_cultivos:
            puntuaciones_cultivo_lista.append(self.dp.MAPA_CRITICIDAD[c])

        puntuaciones_cultivo = np.array(puntuaciones_cultivo_lista)

        F_cultivo = np.mean(puntuaciones_cultivo) / max(self.dp.MAPA_CRITICIDAD.values()) 

        # --- B. FACTOR SUELO/TOPOGRAFÍA ---
        puntuaciones_salinidad = self.dp.REF_SALINIDAD_NORM[indices_ref_mas_cercano]
        F_salinidad = np.mean(puntuaciones_salinidad) 

        puntuaciones_elevacion = self.dp.REF_ELEVACION_NORM[indices_ref_mas_cercano]
        F_elevacion_varianza = np.std(puntuaciones_elevacion)
        
        F_suelo = 0.5 * F_salinidad + 0.5 * F_elevacion_varianza 

        # --- C. FACTOR COBERTURA ---
        F_cobertura = 0.0
        if self.N_SENSORES > 1:
            distancias_sensor = cdist(sensor_coords, sensor_coords)
            indices_triangulo_superior = np.triu_indices(self.N_SENSORES, k=1)
            
            if len(indices_triangulo_superior[0]) > 0:
                F_cobertura_promedio = np.mean(distancias_sensor[indices_triangulo_superior])
                F_cobertura = F_cobertura_promedio / self.dp.max_dist_campo
        
        # --- APTITUD TOTAL (Se busca MAXIMIZAR) ---
        Aptitud_Total = (self.W_CULTIVO * F_cultivo) + \
                        (self.W_SUELO * F_suelo) + \
                        (self.W_COBERTURA * F_cobertura)

        return -Aptitud_Total

    def funcion_aptitud(self, X):
        """Función 'envoltorio' para PySwarms, calcula el costo para todas las partículas."""
        costo = np.array([self._calcular_aptitud_individual(X[i]) for i in range(X.shape[0])])
        return costo

    def ejecutar_optimizacion(self, n_particulas=60, iteraciones=150, c1=0.7, c2=0.9, w=0.75):
        """Ejecuta el algoritmo PSO."""
        opciones = {'c1': c1, 'c2': c2, 'w': w}
        optimizador = ps.single.GlobalBestPSO(
            n_particles=n_particulas,
            dimensions=self.D,
            options=opciones,
            bounds=self.limites
        )

        print(f"\n--- Iniciando Optimización PSO con {self.N_SENSORES} Sensores ({self.D} dimensiones) ---")
        historial_costo, pos_mejor_particula = optimizador.optimize(self.funcion_aptitud, iters=iteraciones)
        print("--- Optimización Finalizada ---")
        
        self.gbest_coords = pos_mejor_particula.reshape(self.N_SENSORES, 2)
        self.gbest_cost = optimizador.cost_history[-1] 
        self.historial_costo = optimizador.cost_history 
        self.optimizador = optimizador