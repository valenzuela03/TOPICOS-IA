# procesador_datos.py

import pandas as pd
import numpy as np
from io import StringIO

class ProcesadorDatos:
    """
    Clase para cargar, preprocesar y normalizar los datos del campo agrícola, 
    preparando los límites para el algoritmo PSO.
    """
    def __init__(self, data_str):
        self.MAPA_CRITICIDAD = {'Tomate': 3, 'Chile': 2, 'Maíz': 1}
        self.df = self._cargar_datos(data_str)
        self._preprocesar_datos()

    def _cargar_datos(self, data_str):
        """Carga los datos de la cadena de texto en un DataFrame."""
        return pd.read_csv(StringIO(data_str))

    def _preprocesar_datos(self):
        """Preprocesa y normaliza las columnas relevantes."""
        df = self.df
        
        self.PUNTOS_REF = df[['Latitud', 'Longitud']].values
        self.REF_CULTIVOS = df['Cultivo'].values

        # Normalización de variables Suelo/Topografía (entre 0 y 1)
        self.REF_ELEVACION_NORM = (df['Elevación (m)'] - df['Elevación (m)'].min()) / \
                                  (df['Elevación (m)'].max() - df['Elevación (m)'].min())
        
        self.REF_SALINIDAD_NORM = (df['Salinidad (dS/m)'] - df['Salinidad (dS/m)'].min()) / \
                                  (df['Salinidad (dS/m)'].max() - df['Salinidad (dS/m)'].min())

        # Límites de Búsqueda para el PSO
        min_lat, max_lat = df['Latitud'].min(), df['Latitud'].max()
        min_lon, max_lon = df['Longitud'].min(), df['Longitud'].max()
        self.min_coords = np.array([min_lat, min_lon])
        self.max_coords = np.array([max_lat, max_lon])
        
        # Distancia Máxima del Campo
        self.max_dist_campo = np.linalg.norm(self.max_coords - self.min_coords)