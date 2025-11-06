# main.py

from procesador_datos import ProcesadorDatos
from optimizador_pso import OptimizadorPSO
from datos_entrada import datos_entrada_str

import numpy as np
import matplotlib.pyplot as plt
from pyswarms.utils.plotters import plot_cost_history
from scipy.spatial.distance import cdist 

if __name__ == "__main__":
    
    N_SENSORES = 6
    ITERACIONES = 150 

    # Pesos de la Función de Aptitud (deben sumar 1.0)
    W_CULTIVO = 0.2
    W_SUELO = 0.2
    W_COBERTURA = 0.6
    
    # 1. Procesamiento de Datos
    procesador = ProcesadorDatos(datos_entrada_str)
    
    # 2. Inicialización y Ejecución de PSO
    optimizador = OptimizadorPSO(
        procesador_datos=procesador, 
        n_sensores=N_SENSORES, 
        w_cultivo=W_CULTIVO, 
        w_suelo=W_SUELO, 
        w_cobertura=W_COBERTURA
    )
    
    optimizador.ejecutar_optimizacion(
        n_particulas=60, 
        iteraciones=ITERACIONES,
        c1=0.7, c2=0.9, w=0.75 
    )

    # 3. Mostrar Resultados Finales
    print("\n--- Resultados de la Optimización ---")
    gbest_aptitud = -optimizador.gbest_cost
    print(f"Mejor Aptitud Encontrada: {gbest_aptitud:.4f}")
    print("\nPosiciones Óptimas de los Sensores (Latitud, Longitud):")
    for k, (lat, lon) in enumerate(optimizador.gbest_coords):
        print(f"Sensor {k+1}: Lat={lat:.6f}, Lon={lon:.6f}")

    # 4. Visualización (Solo Mapa Geoespacial)

    # Tamaño de grafica
    plt.figure(figsize=(10, 7))

    # Puntos de referencia (Cultivos)
    df = procesador.df
    mapa_color_cultivo = {'Maíz': 'red', 'Chile': 'blue', 'Tomate': 'green'}
    plt.scatter(df['Longitud'], df['Latitud'], 
                c=df['Cultivo'].apply(lambda x: mapa_color_cultivo.get(x, 'black')), 
                label='Puntos de Referencia', alpha=0.6)

    # Posiciones óptimas de los sensores
    plt.scatter(optimizador.gbest_coords[:, 1], optimizador.gbest_coords[:, 0], 
                marker='*', s=300, color='gold', edgecolor='black', zorder=5, 
                label=f'Ubicación Óptima de {N_SENSORES} Sensores (PSO)')

    # Conectar cada sensor a su punto de referencia más cercano
    distancias_final = cdist(optimizador.gbest_coords, procesador.PUNTOS_REF)
    indices_ref_mas_cercano_final = np.argmin(distancias_final, axis=1)

    for k in range(N_SENSORES):
        ref_lat, ref_lon = procesador.PUNTOS_REF[indices_ref_mas_cercano_final[k]]
        plt.plot([optimizador.gbest_coords[k, 1], ref_lon], [optimizador.gbest_coords[k, 0], ref_lat], 'k--', alpha=0.3)

    plt.title("Mapa Geoespacial de Cultivos y Colocación Óptima de Sensores (Guasave)")
    plt.xlabel("Longitud")
    plt.ylabel("Latitud")
    
    leyenda_cultivos = [plt.Line2D([0], [0], marker='o', color='w', label=c, 
                                  markerfacecolor=mapa_color_cultivo[c], markersize=10) 
                       for c in ['Maíz', 'Chile', 'Tomate']]
    leyenda_sensores = [plt.Line2D([0], [0], marker='*', color='w', label='Sensor Óptimo', 
                                   markerfacecolor='gold', markeredgecolor='black', markersize=15)]
    plt.legend(handles=leyenda_cultivos + leyenda_sensores, title='Cultivo', loc='lower right')
    plt.grid(True)
    plt.show()