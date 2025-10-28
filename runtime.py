#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Runtime BrickScript en Python
Motor de juego simple para Tetris y Snake
Compatible con Python 2.7 y Python 3.x
"""

import sys
import json
import time
import os

# Compatibilidad Python 2/3
if sys.version_info[0] >= 3:
    unicode = str

# Intentar importar módulos para input de teclado
try:
    # Windows
    import msvcrt
    def obtener_tecla():
        if msvcrt.kbhit():
            return msvcrt.getch().decode('utf-8').lower()
        return None
except ImportError:
    # Linux/Mac
    import sys, tty, termios
    import select
    def obtener_tecla():
        dr, dw, de = select.select([sys.stdin], [], [], 0)
        if dr:
            return sys.stdin.read(1).lower()
        return None

class Juego(object):
    """Motor de juego básico para BrickScript"""
    def __init__(self, datos_json):
        self.datos = datos_json
        self.nombre = datos_json.get('nombreJuego', 'BrickScript Game')
        self.ancho = datos_json.get('anchoTablero', 20)
        self.alto = datos_json.get('altoTablero', 20)
        self.puntuacion = 0
        self.jugando = True
        
        # Inicializar grid
        self.grid = []
        for i in range(self.alto):
            fila = []
            for j in range(self.ancho):
                fila.append(' ')
            self.grid.append(fila)
    
    def limpiar_pantalla(self):
        """Limpia la pantalla de consola"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def renderizar(self):
        """Dibuja el juego en consola"""
        self.limpiar_pantalla()
        
        print('=' * (self.ancho + 2))
        print('  ' + self.nombre)
        print('  Puntuacion: ' + str(self.puntuacion))
        print('=' * (self.ancho + 2))
        
        # Dibujar borde superior
        print('+' + '-' * self.ancho + '+')
        
        # Dibujar grid
        for fila in self.grid:
            print('|' + ''.join(fila) + '|')
        
        # Dibujar borde inferior
        print('+' + '-' * self.ancho + '+')
        
        # Instrucciones
        controles = self.datos.get('controles', {})
        if controles:
            print('\nControles:')
            if 'moverArriba' in controles:
                print('  Arriba: ' + controles.get('moverArriba', 'w'))
            if 'moverAbajo' in controles:
                print('  Abajo: ' + controles.get('moverAbajo', 's'))
            if 'moverIzquierda' in controles:
                print('  Izquierda: ' + controles.get('moverIzquierda', 'a'))
            if 'moverDerecha' in controles:
                print('  Derecha: ' + controles.get('moverDerecha', 'd'))
            if 'pausar' in controles:
                print('  Pausar: ' + controles.get('pausar', 'p'))
            if 'reiniciar' in controles:
                print('  Reiniciar: ' + controles.get('reiniciar', 'r'))
        
        print('\nPresiona Ctrl+C para salir')
    
    def actualizar(self):
        """Actualiza el estado del juego"""
        # Aquí iría la lógica del juego
        # Por ahora solo mantenemos el grid estático
        pass
    
    def procesar_input(self):
        """Procesa la entrada del usuario"""
        tecla = obtener_tecla()
        if tecla:
            controles = self.datos.get('controles', {})
            
            # Verificar si se presionó pausar o reiniciar
            if tecla == controles.get('pausar', 'p'):
                print('\nJuego pausado. Presiona cualquier tecla para continuar...')
                if sys.version_info[0] >= 3:
                    input()
                else:
                    raw_input()
            elif tecla == controles.get('reiniciar', 'r'):
                self.reiniciar()
    
    def reiniciar(self):
        """Reinicia el juego"""
        self.puntuacion = 0
        self.grid = []
        for i in range(self.alto):
            fila = []
            for j in range(self.ancho):
                fila.append(' ')
            self.grid.append(fila)
    
    def run(self):
        """Loop principal del juego"""
        try:
            while self.jugando:
                self.renderizar()
                self.procesar_input()
                self.actualizar()
                time.sleep(0.1)  # 10 FPS
        except KeyboardInterrupt:
            print('\n\nJuego terminado.')
            print('Puntuacion final: ' + str(self.puntuacion))

def cargar_json(ruta):
    """Carga un archivo JSON"""
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # Python 2 fallback
        with open(ruta, 'r') as f:
            return json.load(f)

def main():
    """Función principal del runtime"""
    if len(sys.argv) < 2:
        print('Uso: python runtime.py <archivo.json>')
        print('\nEjemplo:')
        print('  python runtime.py ../ejemplos/tetris.json')
        sys.exit(1)
    
    archivo_json = sys.argv[1]
    
    try:
        # Cargar datos del juego
        datos = cargar_json(archivo_json)
        
        print('========================================')
        print('BrickScript Runtime Engine')
        print('========================================')
        print('Cargando: ' + archivo_json)
        print('Juego: ' + datos.get('nombreJuego', 'Desconocido'))
        print('\nPresiona Enter para comenzar...')
        
        if sys.version_info[0] >= 3:
            input()
        else:
            raw_input()
        
        # Crear y ejecutar el juego
        juego = Juego(datos)
        juego.run()
        
    except IOError:
        print('Error: No se pudo leer el archivo: ' + archivo_json)
        sys.exit(1)
    except KeyboardInterrupt:
        print('\n\nJuego interrumpido.')
        sys.exit(0)

if __name__ == '__main__':
    main()
