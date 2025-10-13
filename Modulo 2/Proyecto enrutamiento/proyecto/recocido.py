# recocido_simulado.py

import random
import math
import copy
from datos import Datos
from solucion import Solucion

class RecocidoSimulado:
    """Implementa el algoritmo de Recocido Simulado para el MDVRP."""
    
    def __init__(self, datos: Datos, temp_inicial, temp_final, factor_enfriamiento, iter_por_temp):
        self.datos = datos
        self.T_inicial = temp_inicial
        self.T_final = temp_final
        self.alpha = factor_enfriamiento
        self.iter_por_temp = iter_por_temp

    def _generar_solucion_inicial(self):
        """Genera una solución inicial (heurística de asignación al CDD más cercano)."""
        clientes_a_asignar = self.datos.clientes[:]
        random.shuffle(clientes_a_asignar)
        
        solucion_mapa = {d: {'deposito': d, 'clientes': []} 
                         for d in self.datos.DEPOSITOS_DISPONIBLES}
        
        for cliente in clientes_a_asignar:
            demanda = self.datos.DEMANDAS[cliente]
            mejor_deposito = None
            mejor_costo = float('inf')
            
            for d in self.datos.DEPOSITOS_DISPONIBLES:
                costo = self.datos.COSTO_MATRIX[d][cliente] 
                
                capacidad_usada = sum(self.datos.DEMANDAS[c] for c in solucion_mapa[d]['clientes'])
                
                if capacidad_usada + demanda <= self.datos.CAPACIDAD_VEHICULO:
                    if costo < mejor_costo:
                        mejor_costo = costo
                        mejor_deposito = d
            
            if mejor_deposito:
                solucion_mapa[mejor_deposito]['clientes'].append(cliente)
        
        rutas_formateadas = [{'deposito': d_info['deposito'], 'clientes': d_info['clientes']} 
                             for d_info in solucion_mapa.values() if d_info['clientes']]
        
        return Solucion(rutas_formateadas, self.datos)

    def _generar_vecino_aleatorio(self, solucion_actual: Solucion):
        """Genera un vecino aleatorio con movimientos inter-depósito o intra-ruta."""
        
        sol = solucion_actual.rutas
        
        # 1. Movimiento Inter-Depósito (Swap) - 60% probabilidad
        if len(sol) >= 1 and random.random() < 0.6: 
            r1_idx = random.randint(0, len(sol) - 1)
            r1_info = sol[r1_idx]
            r1_clientes = r1_info['clientes']
            
            if r1_clientes:
                c1_idx = random.randint(0, len(r1_clientes) - 1)
                cliente_movido = r1_clientes[c1_idx]
                
                depositos_destino = self.datos.DEPOSITOS_DISPONIBLES 
                d2 = random.choice(depositos_destino)

                nuevas_rutas = copy.deepcopy(sol)
                r1_nueva_clientes = r1_clientes[:c1_idx] + r1_clientes[c1_idx+1:]
                
                r2_info = next((r for r in nuevas_rutas if r['deposito'] == d2), None)
                
                if r1_info['deposito'] != d2:
                    if r2_info:
                        r2_idx = nuevas_rutas.index(r2_info)
                        r2_nueva_clientes = r2_info['clientes'][:]
                        c2_idx = random.randint(0, len(r2_nueva_clientes))
                        r2_nueva_clientes.insert(c2_idx, cliente_movido)
                        
                        nuevas_rutas[r1_idx]['clientes'] = r1_nueva_clientes
                        nuevas_rutas[r2_idx]['clientes'] = r2_nueva_clientes
                    else:
                        nuevas_rutas[r1_idx]['clientes'] = r1_nueva_clientes
                        nuevas_rutas.append({'deposito': d2, 'clientes': [cliente_movido]})
                
                nuevas_rutas_limpia = [r for r in nuevas_rutas if r['clientes']]
                vecino = Solucion(nuevas_rutas_limpia, self.datos)
                if vecino.es_valida: return vecino

        # 2. Movimiento Intra-Ruta (2-opt) - 40% probabilidad
        if len(sol) > 0 and random.random() < 0.8: 
            r_idx = random.randint(0, len(sol) - 1)
            ruta_info = sol[r_idx]
            ruta = ruta_info['clientes']
            L = len(ruta)
            
            if L >= 2:
                i, j = sorted(random.sample(range(L), 2))
                
                nueva_ruta_clientes = ruta[:i] + ruta[i:j+1][::-1] + ruta[j+1:]
                
                nuevas_rutas = copy.deepcopy(sol)
                nuevas_rutas[r_idx]['clientes'] = nueva_ruta_clientes
                
                vecino = Solucion(nuevas_rutas, self.datos)
                return vecino
        
        return solucion_actual.copiar() 

    def optimizar(self):
        """Ejecuta el algoritmo de Recocido Simulado con la impresión solicitada."""
        
        solucion_actual = self._generar_solucion_inicial()
        mejor_solucion_global = solucion_actual.copiar()
        T = self.T_inicial

        paso_total = 0 
        IMPRESION_INTERVALO = 1000 # Imprimir cada 1000 pasos

        # 1. Impresión del encabezado
        print(f"--- INICIO DEL RECOCIDO SIMULADO (Factor de Enfriamiento: {self.alpha}) ---")

        while T > self.T_final:
            
            for _ in range(self.iter_por_temp):
                
                vecino = self._generar_vecino_aleatorio(solucion_actual)
                delta_E = vecino.costo - solucion_actual.costo 
                
                paso_total += 1
                
                # --- CONTROL DE IMPRESIÓN PERSONALIZADO (Primeros 10 y luego cada 1000) ---
                imprimir_paso = False
                
                if paso_total <= 10:
                    imprimir_paso = True
                elif (paso_total > 10) and ((paso_total - 10) % IMPRESION_INTERVALO == 0):
                    imprimir_paso = True

                if imprimir_paso:
                    # LÍNEA DE IMPRESIÓN MODIFICADA: Solo muestra Costo y T
                    print(f"Paso {paso_total:<5} -> Costo=${solucion_actual.costo_base:,.2f} | T={T:.2f}")

                # --- Lógica de Aceptación/Mejora ---
                if delta_E < 0:
                    solucion_actual = vecino
                    
                    if solucion_actual.costo < mejor_solucion_global.costo:
                        mejor_solucion_global = solucion_actual.copiar()
                else:
                    probabilidad_aceptacion = math.exp(-delta_E / T)
                    
                    if random.random() < probabilidad_aceptacion:
                        solucion_actual = vecino

            T *= self.alpha
        
        # 2. Impresión de la finalización
        print(f"--- FIN DEL RECOCIDO SIMULADO (Total Pasos: {paso_total}) ---")

        return mejor_solucion_global

# ==============================================================================
# EJECUCIÓN DEL PROGRAMA PRINCIPAL Y REPORTE POR DISTRIBUIDOR
# ==============================================================================

if __name__ == "__main__":
    
    # 1. Inicializar datos
    datos = Datos()
    
    # Parámetros del Recocido Simulado
    T_INICIAL = 500.0          
    T_FINAL = 0.5            
    FACTOR_ENFRIAMIENTO = 0.98 
    ITER_POR_TEMP = 100        
    
    # 2. Inicializar y ejecutar el optimizador
    sa = RecocidoSimulado(
        datos, 
        T_INICIAL, 
        T_FINAL, 
        FACTOR_ENFRIAMIENTO, 
        ITER_POR_TEMP
    )
    
    final_solution = sa.optimizar()

    # 3. Generar Reporte Final con el formato exacto solicitado
    print(f"\nREPORTE FINAL DE DISTRIBUCIÓN (Ruta Óptima por Gasto de Gasolina)")
    print("=======================================================================================================================")
    
    print(f" Gasto Total de Gasolina: ${final_solution.costo_base:,.2f}") 
    print(f"Tiendas Surtidas: {len(datos.clientes)} | Distribuidores Utilizados: {len(final_solution.rutas)} / {len(datos.DEPOSITOS_DISPONIBLES)}")
    print("-----------------------------------------------------------------------------------------------------------------------")
    
    rutas_ordenadas = sorted(final_solution.rutas, key=lambda r: r['deposito'])

    for i, ruta_info in enumerate(rutas_ordenadas):
        deposito = ruta_info['deposito']
        ruta_clientes = ruta_info['clientes']
        
        costo_ruta = Solucion([ruta_info], datos).costo_base
        
        print(f"\nDistribuidor: {deposito} (Ruta {i+1})")
        print(f"    - Costo de Gasolina: ${costo_ruta:,.2f}")
        print(f"    - Tiendas a Surtir: {len(ruta_clientes)}")
        print(f"    - Ruta Óptima: {deposito} -> {' -> '.join(ruta_clientes)} -> {deposito}")