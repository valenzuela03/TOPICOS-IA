# solucion_vrp.py

import copy
# Importar la clase DatosVRP del archivo datos_vrp.py
from datos_vrp import DatosVRP 

# Definición de la penalización por no usar 10 CDDs. Valor muy alto.
PENALIZACION_RUTAS_INCOMPLETAS = 1_000_000_000 

class SolucionVRP:
    """
    Representa una solución de MDVRP. Incluye una restricción suave (penalización)
    para forzar el uso de los 10 CDDs.
    """
    
    
    def __init__(self, rutas: list, datos: DatosVRP): 
        self.rutas = rutas  
        self.datos = datos
        self.costo_base = self._calcular_costo_base() 
        self.es_valida = self._es_solucion_valida()
        # El costo total incluye la penalización
        self.costo = self._aplicar_penalizacion_rutas() 

    def _calcular_costo_base(self):
        """Calcula el costo total (gasto de gasolina) de las rutas activas."""
        costo_total = 0
        cost_matrix = self.datos.COSTO_MATRIX 
        
        for ruta_info in self.rutas:
            deposito = ruta_info['deposito']
            clientes = ruta_info['clientes']
            
            # Si el CDD está activo pero sin clientes, el costo es 0 (no hay viaje)
            if not clientes:
                continue
            
            # Ruta completa: Depósito -> ... -> Depósito
            ruta_completa = [deposito] + clientes + [deposito]
            for i in range(len(ruta_completa) - 1):
                costo_total += cost_matrix[ruta_completa[i]][ruta_completa[i+1]]
        return costo_total
    
    def _aplicar_penalizacion_rutas(self):
        """Aplica la penalización si no se usan exactamente 10 rutas con clientes."""
        costo = self.costo_base
        
        # Contar el número de rutas activas (con clientes)
        num_rutas_activas = len([r for r in self.rutas if r['clientes']])
        
        if num_rutas_activas != len(self.datos.DEPOSITOS_DISPONIBLES):
            # Penalización muy alta para que el Recocido Simulado evite esta solución
            costo += PENALIZACION_RUTAS_INCOMPLETAS 
        
        return costo

    def _es_solucion_valida(self):
        """Verifica la restricción de capacidad (hard constraint) para cada ruta."""
        demandas = self.datos.DEMANDAS
        capacidad = self.datos.CAPACIDAD_VEHICULO
        
        for ruta_info in self.rutas:
            clientes = ruta_info['clientes']
            demanda_ruta = sum(demandas.get(nodo, 0) for nodo in clientes)
            
            if demanda_ruta > capacidad:
                return False
        return True

    def copiar(self):
        """Devuelve una copia profunda de la solución."""
        return SolucionVRP(copy.deepcopy(self.rutas), self.datos)