package src;
import java.util.Arrays;
import java.util.Random;

public class Recocido {

    static Random rand = new Random();

    // Función de costo: pares fuera de orden

    public static int costo(int[] lista) {
        int c = 0;
        for (int i = 0; i < lista.length; i++) {
            for (int j = i + 1; j < lista.length; j++) {
                if (lista[i] > lista[j]) {
                    c++;
                }
            }
        }
        return c;
    }

    // vecinos intercambiando dos posiciones al azar

    public static int[] vecino(int[] lista) {
        int[] nueva = Arrays.copyOf(lista, lista.length);
        int i = rand.nextInt(lista.length);
        int j = rand.nextInt(lista.length);
        while (j == i) {
            j = rand.nextInt(lista.length);
        }
        int temp = nueva[i];
        nueva[i] = nueva[j];
        nueva[j] = temp;
        return nueva;
    }

    // Algoritmo de Recocido Simulado
    
    public static int[] recocidoSimulado(int[] S0) {
        int[] actual = Arrays.copyOf(S0, S0.length);
        int[] mejor = Arrays.copyOf(actual, actual.length);
        int mejorCosto = costo(actual);

        double T = 100.0;   
        double alpha = 0.95; 
        int paso = 0;

        while (T > 0.1) {
            for (int k = 0; k < 100; k++) {
                paso++;
                int[] candidato = vecino(actual);
                int delta = costo(candidato) - costo(actual);

                if (delta < 0 || rand.nextDouble() < Math.exp(-delta / T)) {
                    actual = candidato;
                }

                int costoActual = costo(actual);
                if (costoActual < mejorCosto) {
                    mejor = Arrays.copyOf(actual, actual.length);
                    mejorCosto = costoActual;
                }

                // Imprimir los primeros 10 pasos
                if (paso <= 10) {
                    System.out.println("Paso " + paso + " -> " +
                            Arrays.toString(actual) + " Costo=" + costoActual + " T=" + String.format("%.2f", T));
                }

                // Imprimir cada 1000 pasos
                if (paso % 1000 == 0) {
                    System.out.println("Paso " + paso + " -> " +
                            Arrays.toString(actual) + " Costo=" + costoActual + " T=" + String.format("%.2f", T));
                }
            }
            T = T * alpha; // enfriar
        }

        System.out.println("\n--- Resultado Final ---");
        return mejor;
    }

    // Main
    public static void main(String[] args) {
        int[] S0 = {9,16, 5,17, 2,18, 8, 1,19, 3, 7,15, 4, 6, 0,14,12,13,11,10};
        System.out.println("Estado inicial: " + Arrays.toString(S0));

        int[] resultado = recocidoSimulado(S0);

        System.out.println("Mejor solucion: " + Arrays.toString(resultado));
        System.out.println("Costo final: " + costo(resultado));
    }
}