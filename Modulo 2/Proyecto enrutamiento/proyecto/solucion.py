import copy
from datos import Datos 

# Definición de la penalización por no usar 10 CDDs. Valor muy alto.
PENALIZACION_RUTAS_INCOMPLETAS = 1_000_000_000 

# ==============================================================================
# CLASE SOLUCIÓN
# ==============================================================================
class Solucion:
    """
    Representa una solución de MDVRP, con penalización para forzar 10 CDDs.
    """
    
    def __init__(self, rutas: list, datos: Datos):
        self.rutas = rutas  
        self.datos = datos
        self.costo_base = self._calcular_costo_base() 
        self.es_valida = self._es_solucion_valida()
        self.costo = self._aplicar_penalizacion_rutas() 

    def _calcular_costo_base(self):
        """Calcula el costo total (gasto de gasolina) de las rutas activas."""
        costo_total = 0
        cost_matrix = self.datos.COSTO_MATRIX 
        
        for ruta_info in self.rutas:
            deposito = ruta_info['deposito']
            clientes = ruta_info['clientes']
            
            if not clientes:
                continue
            
            ruta_completa = [deposito] + clientes + [deposito]
            for i in range(len(ruta_completa) - 1):
                costo_total += cost_matrix[ruta_completa[i]][ruta_completa[i+1]]
        return costo_total
    
    def _aplicar_penalizacion_rutas(self):
        """Aplica la penalización si no se usan exactamente 10 rutas con clientes."""
        costo = self.costo_base
        
        num_rutas_activas = len([r for r in self.rutas if r['clientes']])
        
        if num_rutas_activas != len(self.datos.DEPOSITOS_DISPONIBLES):
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
        return Solucion(copy.deepcopy(self.rutas), self.datos)