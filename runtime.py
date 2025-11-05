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
        
        # Detectar tipo de juego e inicializar
        nombre_minusc = self.nombre.lower()
        if 'snake' in nombre_minusc:
            self.tipo_juego = 'snake'
            self.inicializar_snake()
        elif 'tetris' in nombre_minusc:
            self.tipo_juego = 'tetris'
            self.inicializar_tetris()
        else:
            self.tipo_juego = 'generico'
    
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
    
    def inicializar_snake(self):
        """Inicializa el juego Snake"""
        serpiente_config = self.datos.get('serpiente', {})
        self.snake_x = serpiente_config.get('posXInicial', self.ancho // 2)
        self.snake_y = serpiente_config.get('posYInicial', self.alto // 2)
        longitud = serpiente_config.get('longitudInicial', 3)
        
        # Cuerpo de la serpiente (lista de [x, y])
        self.snake_cuerpo = []
        for i in range(longitud):
            self.snake_cuerpo.append([self.snake_x - i, self.snake_y])
        
        # Dirección inicial (derecha)
        self.snake_dir_x = 1
        self.snake_dir_y = 0
        
        # Generar comida
        self.generar_comida()
        
        # Control de velocidad
        self.snake_velocidad = serpiente_config.get('velocidad', 5.0)
        self.snake_tiempo_ultimo_mov = time.time()
        
        # Actualizar grid inicial
        self.actualizar_grid_snake()
    
    def generar_comida(self):
        """Genera comida en posición aleatoria"""
        import random
        while True:
            self.comida_x = random.randint(0, self.ancho - 1)
            self.comida_y = random.randint(0, self.alto - 1)
            # Verificar que no esté en el cuerpo de la serpiente
            if [self.comida_x, self.comida_y] not in self.snake_cuerpo:
                break
    
    def inicializar_tetris(self):
        """Inicializa el juego Tetris"""
        import random
        
        # Obtener figuras disponibles del JSON
        figuras_nombres = []
        for key in self.datos.keys():
            if key.startswith('figura'):
                figuras_nombres.append(key)
        
        self.tetris_figuras = []
        for nombre in figuras_nombres:
            figura = self.datos.get(nombre, {})
            if 'patron' in figura:
                self.tetris_figuras.append(figura)
        
        # Si no hay figuras, crear una básica
        if not self.tetris_figuras:
            self.tetris_figuras = [{
                'color': 'cyan',
                'patron': [[[1, 1, 1, 1]]]
            }]
        
        # Posición de la pieza actual
        self.tetris_pieza_x = self.ancho // 2 - 2
        self.tetris_pieza_y = 0
        self.tetris_pieza_rotacion = 0
        
        # Generar primera pieza
        self.tetris_pieza_actual = random.choice(self.tetris_figuras)
        
        # Control de velocidad
        velocidad = self.datos.get('velocidadInicial', 1.0)
        self.tetris_velocidad = velocidad
        self.tetris_tiempo_ultima_caida = time.time()
        
        # Grid fijo (piezas ya colocadas)
        self.tetris_grid_fijo = []
        for i in range(self.alto):
            fila = []
            for j in range(self.ancho):
                fila.append(' ')
            self.tetris_grid_fijo.append(fila)
        
        # Actualizar grid inicial
        self.actualizar_grid_tetris()
    
    def actualizar(self):
        """Actualiza el estado del juego"""
        if self.tipo_juego == 'snake':
            self.actualizar_snake()
        elif self.tipo_juego == 'tetris':
            self.actualizar_tetris()
    
    def actualizar_snake(self):
        """Actualiza la lógica de Snake"""
        # Control de velocidad
        tiempo_actual = time.time()
        tiempo_entre_movimientos = 1.0 / self.snake_velocidad
        
        if tiempo_actual - self.snake_tiempo_ultimo_mov < tiempo_entre_movimientos:
            return
        
        self.snake_tiempo_ultimo_mov = tiempo_actual
        
        # Nueva posición de la cabeza
        nuevo_x = self.snake_cuerpo[0][0] + self.snake_dir_x
        nuevo_y = self.snake_cuerpo[0][1] + self.snake_dir_y
        
        # Verificar colisión con bordes
        reglas = self.datos.get('reglasJuego', {})
        if reglas.get('chocarConBorde', True):
            if nuevo_x < 0 or nuevo_x >= self.ancho or nuevo_y < 0 or nuevo_y >= self.alto:
                self.jugando = False
                return
        else:
            # Wrap around
            nuevo_x = nuevo_x % self.ancho
            nuevo_y = nuevo_y % self.alto
        
        # Verificar colisión consigo misma
        if reglas.get('chocarConsigoMismo', True):
            if [nuevo_x, nuevo_y] in self.snake_cuerpo:
                self.jugando = False
                return
        
        # Insertar nueva cabeza
        self.snake_cuerpo.insert(0, [nuevo_x, nuevo_y])
        
        # Verificar si comió
        if nuevo_x == self.comida_x and nuevo_y == self.comida_y:
            # Aumentar puntuación
            comida_config = self.datos.get('comida', {})
            self.puntuacion += comida_config.get('puntos', 10)
            # Generar nueva comida
            self.generar_comida()
        else:
            # Eliminar cola si no comió
            self.snake_cuerpo.pop()
        
        # Actualizar grid
        self.actualizar_grid_snake()
    
    def actualizar_grid_snake(self):
        """Actualiza el grid con la serpiente y comida"""
        # Limpiar grid
        for i in range(self.alto):
            for j in range(self.ancho):
                self.grid[i][j] = ' '
        
        # Dibujar comida
        if 0 <= self.comida_y < self.alto and 0 <= self.comida_x < self.ancho:
            self.grid[self.comida_y][self.comida_x] = '*'
        
        # Dibujar serpiente
        for i, segmento in enumerate(self.snake_cuerpo):
            x, y = segmento
            if 0 <= y < self.alto and 0 <= x < self.ancho:
                if i == 0:
                    self.grid[y][x] = 'O'  # Cabeza
                else:
                    self.grid[y][x] = 'o'  # Cuerpo
    
    def actualizar_tetris(self):
        """Actualiza la lógica de Tetris"""
        import random
        
        # Control de velocidad de caída
        tiempo_actual = time.time()
        tiempo_entre_caidas = 1.0 / self.tetris_velocidad
        
        if tiempo_actual - self.tetris_tiempo_ultima_caida < tiempo_entre_caidas:
            return
        
        self.tetris_tiempo_ultima_caida = tiempo_actual
        
        # Intentar mover pieza hacia abajo
        self.tetris_pieza_y += 1
        
        # Verificar colisión
        if self.tetris_colision():
            # Retroceder
            self.tetris_pieza_y -= 1
            
            # Fijar pieza en el grid
            self.tetris_fijar_pieza()
            
            # Eliminar líneas completas
            self.tetris_eliminar_lineas()
            
            # Generar nueva pieza
            self.tetris_pieza_x = self.ancho // 2 - 2
            self.tetris_pieza_y = 0
            self.tetris_pieza_rotacion = 0
            self.tetris_pieza_actual = random.choice(self.tetris_figuras)
            
            # Verificar game over
            if self.tetris_colision():
                self.jugando = False
        
        # Actualizar grid visual
        self.actualizar_grid_tetris()
    
    def tetris_colision(self):
        """Verifica si la pieza actual colisiona"""
        patron = self.tetris_pieza_actual.get('patron', [[[]]])[self.tetris_pieza_rotacion % len(self.tetris_pieza_actual.get('patron', [[[]]]))]
        
        for i, fila in enumerate(patron):
            for j, celda in enumerate(fila):
                if celda:
                    x = self.tetris_pieza_x + j
                    y = self.tetris_pieza_y + i
                    
                    # Verificar bordes
                    if x < 0 or x >= self.ancho or y >= self.alto:
                        return True
                    
                    # Verificar grid fijo
                    if y >= 0 and self.tetris_grid_fijo[y][x] != ' ':
                        return True
        
        return False
    
    def tetris_fijar_pieza(self):
        """Fija la pieza actual en el grid"""
        patron = self.tetris_pieza_actual.get('patron', [[[]]])[self.tetris_pieza_rotacion % len(self.tetris_pieza_actual.get('patron', [[[]]]))]
        
        for i, fila in enumerate(patron):
            for j, celda in enumerate(fila):
                if celda:
                    x = self.tetris_pieza_x + j
                    y = self.tetris_pieza_y + i
                    
                    if 0 <= y < self.alto and 0 <= x < self.ancho:
                        self.tetris_grid_fijo[y][x] = '#'
    
    def tetris_eliminar_lineas(self):
        """Elimina líneas completas"""
        lineas_eliminadas = 0
        y = self.alto - 1
        
        while y >= 0:
            # Verificar si la línea está completa
            if all(self.tetris_grid_fijo[y][x] != ' ' for x in range(self.ancho)):
                # Eliminar línea
                del self.tetris_grid_fijo[y]
                # Agregar línea vacía arriba
                nueva_fila = [' '] * self.ancho
                self.tetris_grid_fijo.insert(0, nueva_fila)
                lineas_eliminadas += 1
                # No incrementar y para revisar la misma posición de nuevo
            else:
                y -= 1
        
        # Actualizar puntuación
        if lineas_eliminadas > 0:
            puntos = [0, 100, 300, 500, 800]
            self.puntuacion += puntos[min(lineas_eliminadas, 4)]
    
    def actualizar_grid_tetris(self):
        """Actualiza el grid con Tetris"""
        # Copiar grid fijo
        for i in range(self.alto):
            for j in range(self.ancho):
                self.grid[i][j] = self.tetris_grid_fijo[i][j]
        
        # Dibujar pieza actual
        patron = self.tetris_pieza_actual.get('patron', [[[]]])[self.tetris_pieza_rotacion % len(self.tetris_pieza_actual.get('patron', [[[]]]))]
        
        for i, fila in enumerate(patron):
            for j, celda in enumerate(fila):
                if celda:
                    x = self.tetris_pieza_x + j
                    y = self.tetris_pieza_y + i
                    
                    if 0 <= y < self.alto and 0 <= x < self.ancho:
                        self.grid[y][x] = '#'
    
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
            # Procesar controles de movimiento para Snake
            elif self.tipo_juego == 'snake':
                if tecla == controles.get('moverArriba', 'w'):
                    # No permitir moverse en dirección opuesta
                    if self.snake_dir_y != 1:
                        self.snake_dir_x = 0
                        self.snake_dir_y = -1
                elif tecla == controles.get('moverAbajo', 's'):
                    if self.snake_dir_y != -1:
                        self.snake_dir_x = 0
                        self.snake_dir_y = 1
                elif tecla == controles.get('moverIzquierda', 'a'):
                    if self.snake_dir_x != 1:
                        self.snake_dir_x = -1
                        self.snake_dir_y = 0
                elif tecla == controles.get('moverDerecha', 'd'):
                    if self.snake_dir_x != -1:
                        self.snake_dir_x = 1
                        self.snake_dir_y = 0
            # Procesar controles para Tetris
            elif self.tipo_juego == 'tetris':
                if tecla == controles.get('moverIzquierda', 'a'):
                    self.tetris_pieza_x -= 1
                    if self.tetris_colision():
                        self.tetris_pieza_x += 1
                elif tecla == controles.get('moverDerecha', 'd'):
                    self.tetris_pieza_x += 1
                    if self.tetris_colision():
                        self.tetris_pieza_x -= 1
                elif tecla == controles.get('acelerarAbajo', 's'):
                    self.tetris_pieza_y += 1
                    if self.tetris_colision():
                        self.tetris_pieza_y -= 1
                elif tecla == controles.get('evitarCaida', 'w'):
                    # Rotar pieza
                    self.tetris_pieza_rotacion += 1
                    if self.tetris_colision():
                        self.tetris_pieza_rotacion -= 1
    
    def reiniciar(self):
        """Reinicia el juego"""
        self.puntuacion = 0
        self.jugando = True
        self.grid = []
        for i in range(self.alto):
            fila = []
            for j in range(self.ancho):
                fila.append(' ')
            self.grid.append(fila)
        
        # Reinicializar según tipo de juego
        if self.tipo_juego == 'snake':
            self.inicializar_snake()
        elif self.tipo_juego == 'tetris':
            self.inicializar_tetris()
    
    def run(self):
        """Loop principal del juego"""
        try:
            while self.jugando:
                self.renderizar()
                self.procesar_input()
                self.actualizar()
                time.sleep(0.05)  # 20 FPS
            
            # Game Over
            print('\n\n¡GAME OVER!')
            print('Puntuacion final: ' + str(self.puntuacion))
            print('\nPresiona cualquier tecla para salir...')
            if sys.version_info[0] >= 3:
                input()
            else:
                raw_input()
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
