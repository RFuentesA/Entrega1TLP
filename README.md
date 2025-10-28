# Entrega1TLP - Python

En este repo esta el codigo del compilador y runtime necesarios para poder ejecutar el snake o el tetris

# Necesario tener python 2.7 o 3.x

para windows descargarlo desde https://www.python.org/downloads/

# Uso de compiler.py

al ejecutar dicho archivo se pide ingresar la dirección del archivo.brick que será compilado

Ejemplo: Ingresa la dirreción del archivo: ../ejemplos/tetris.brik

# Ejecutar el juego

Existen 2 formas, la primera es desde la terminal del IDE con el comando

```bash
python runtime.py ../ejemplos/tetris.json
```
La segunda forma consiste en utilizar el script jugar.bat desde el simbolo del sistema (CMD) estando ubicado en la carpeta raiz: Entrega1TLP y escribiendo el siguiente comando pudiendo cambiar el nombre del juego o no (tetris o snake)

```cmd
jugar.bat tetris
```

# Estructura de Archivos

```
Entrega1TLP/
├── ejemplos       # Carpeta que guarda archivos brick y JSON
├── compiler.py    # Compilador: Lexer + Parser + Generador JSON
├── jugar.bat      # Script de compilación y ejecución (Windows)
├── README.md      # Este archivo
└── runtime.py     # Motor de juego básico
```
# Componentes

### compiler.py

Script completo que incluye:

#### Clase Token
Representa un token del lenguaje.

#### Clase Tokenizador
Realiza el análisis léxico:
- Usa expresiones regulares para reconocer tokens
- Elimina comentarios (# y &)
- Detecta caracteres inesperados
- Genera lista de tokens

#### Clase Parser
Realiza el análisis sintáctico:
- Construye el AST (diccionario de Python)
- Maneja variables, arrays y objetos
- Valida referencias a variables
- Detecta errores sintácticos y semánticos

#### Funciones Auxiliares
- `cargar_archivo()`: Lee archivos .brik
- `guardar_json()`: Guarda el AST en formato JSON
- `main()`: Función principal del compilador

### runtime.py

Motor de juego simple que incluye:

#### Clase Juego
Motor básico de juego:
- Carga configuración desde JSON
- Renderiza el grid en consola
- Procesa input del teclado
- Loop principal del juego

#### Funciones de Input
- Compatible con Windows (msvcrt)
- Compatible con Linux/Mac (termios)
- Detección de teclas sin bloqueo

## Manejo de Errores

### Errores Léxicos
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

## Autores
- Ricardo armando fuentes arevalo
- jose mauricio
- luis