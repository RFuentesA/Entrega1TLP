# Entrega2TLP

En este repo está el codigo del compilador y runtime necesarios para poder ejecutar los juegos Snake y Tetris.

# Es necesario tener python 2.7 o 3.x

# Uso de compiler.py:

Al ejecutar este archivo se pide ingresar la dirección del archivo.brick que será compilado

Ejemplo: Ingresa la dirreción del archivo: ../ejemplos/tetris.brik

# Ejecutar el juego

Existen 2 formas, la primera es desde la terminal del IDE con el comando

```bash
python runtime.py ../ejemplos/tetris.json
```
La segunda forma consiste en utilizar el script jugar.bat desde el simbolo del sistema (CMD) estando ubicado en la carpeta raiz: Entrega2TLP. Simplemente ejecuta el archivo .bat y te preguntará qué juego deseas jugar:

```cmd
jugar.bat
```

El script te presentará un menú interactivo donde podrás elegir entre Snake (opción 1) o Tetris (opción 2).

# Estructura de Archivos:

```
Entrega1TLP/
├── ejemplos       # Carpeta que guarda archivos brick y JSON
├── compiler.py    # Compilador: Lexer + Parser + Generador JSON
├── jugar.bat      # Script de compilación y ejecución (Windows)
├── README.md      # Este archivo
└── runtime.py     # Motor de juego básico
```
# Componentes:

### compiler.py

Script completo que incluye:

#### Clase Token:
Representa un token del lenguaje.

#### Clase Tokenizador:
Realiza el análisis léxico:
- Usa expresiones regulares para reconocer tokens
- Elimina comentarios (# y &)
- Detecta caracteres inesperados
- Genera lista de tokens

#### Clase Parser:
Realiza el análisis sintáctico:
- Construye el AST (diccionario de Python)
- Maneja variables, arrays y objetos
- Valida referencias a variables
- Detecta errores sintácticos y semánticos

#### Funciones Auxiliares:
- `cargar_archivo()`: Lee archivos .brik
- `guardar_json()`: Guarda el AST en formato JSON
- `main()`: Función principal del compilador

### runtime.py:

Motor de juego simple que incluye:

#### Clase Juego:
Motor básico de juego:
- Carga configuración desde JSON
- Renderiza el grid en consola
- Procesa input del teclado
- Loop principal del juego

#### Funciones de Input:
- Compatible con Windows (msvcrt)
- Compatible con Linux/Mac (termios)
- Detección de teclas sin bloqueo

## Controles de Juego:

### Snake:
- **W**: Mover arriba
- **S**: Mover abajo
- **A**: Mover izquierda
- **D**: Mover derecha
- **P**: Pausar
- **R**: Reiniciar

### Tetris:
- **A**: Mover pieza a la izquierda
- **D**: Mover pieza a la derecha
- **S**: Acelerar caída de la pieza
- **W**: Rotar la pieza
- **P**: Pausar
- **R**: Reiniciar

## Manejo de Errores:

### Errores Léxicos:
```python
raise ValueError('Error léxico: Caracteres inesperados: @#$')
```

### Errores de Sintaxis
```python
raise SyntaxError('Error: Se esperaba un identificador')
```

### Errores Semánticos
```python
raise NameError('Error semántico: "variable" no definido')
```

## Autores:
- Ricardo Armando Fuentes Arevalo
- Jose Mauricio Toscano Aguas
- Luis Carlos Sanchez Florez
