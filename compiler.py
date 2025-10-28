#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Compilador BrickScript en Python
Realiza el análisis léxico, sintáctico y genera JSON
Compatible con Python 2.7 y Python 3.x
"""

import sys
import re
import json

# Compatibilidad Python 2/3
if sys.version_info[0] >= 3:
    unicode = str

# Lista de palabras clave del lenguaje BrickScript
KEYWORDS = ['String', 'Float', 'Int', 'Bool', 'thing', 'tHing', 'True', 'False']

class Token(object):
    """Representa un token del lenguaje"""
    def __init__(self, tipo, valor):
        self.tipo = tipo
        self.valor = valor
    
    def __repr__(self):
        if isinstance(self.valor, str):
            return '({}, "{}")'.format(self.tipo, self.valor)
        return '({}, {})'.format(self.tipo, self.valor)

class Tokenizador(object):
    """Analizador léxico - convierte código fuente en tokens"""
    def __init__(self, codigo):
        self.codigo = codigo
        self.tokens = []
    
    def tokenizar(self):
        """Procesa el código y genera la lista de tokens"""
        # Patrón regex para reconocer tokens
        # Grupos: (espacios)|(strings)|(números)|(operadores)|(identificadores)
        patron = re.compile(r'(\s+)|"([^"]*)"|(\d+\.?\d*)|([\{\}\[\]=,#&:\(\);])|(\w+)')
        
        lineas = self.codigo.split('\n')
        for linea in lineas:
            # Eliminar comentarios (después de # o &)
            if '#' in linea:
                linea = linea.split('#')[0]
            if '&' in linea:
                linea = linea.split('&')[0]
            
            linea = linea.strip()
            if not linea:
                continue
            
            ultima_pos = 0
            for match in patron.finditer(linea):
                # Verificar caracteres inesperados
                if match.start() > ultima_pos:
                    fragmento = linea[ultima_pos:match.start()].strip()
                    if fragmento:
                        raise ValueError('Error léxico: Caracteres inesperados: ' + fragmento)
                
                # Espacios en blanco (ignorar)
                if match.group(1):
                    pass
                # Strings
                elif match.group(2) is not None:
                    self.tokens.append(Token('STRING', match.group(2)))
                # Números
                elif match.group(3):
                    num_str = match.group(3)
                    if '.' in num_str:
                        self.tokens.append(Token('NUMBER', float(num_str)))
                    else:
                        self.tokens.append(Token('NUMBER', int(num_str)))
                # Operadores
                elif match.group(4):
                    self.tokens.append(Token('OPERATOR', match.group(4)))
                # Identificadores y palabras clave
                elif match.group(5):
                    palabra = match.group(5)
                    if palabra in KEYWORDS:
                        self.tokens.append(Token('KEYWORD', palabra))
                    else:
                        self.tokens.append(Token('IDENTIFIER', palabra))
                
                ultima_pos = match.end()
            
            # Verificar caracteres al final de la línea
            if ultima_pos < len(linea):
                fragmento = linea[ultima_pos:].strip()
                if fragmento:
                    raise ValueError('Error léxico: Caracteres inesperados al final: ' + fragmento)
        
        return self.tokens

class Parser(object):
    """Analizador sintáctico - construye el AST a partir de tokens"""
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.tabla_simbolos = {}
    
    def parse(self):
        """Procesa los tokens y construye el AST/Tabla de símbolos"""
        while self.pos < len(self.tokens):
            token_actual = self.peek()
            if token_actual is None:
                break
            
            # Consumir palabra clave de tipo opcional
            if token_actual.tipo == 'KEYWORD':
                self.get_token()  # Consumir KEYWORD
                
                # Manejar arrays (Int[], String[], etc.)
                if self.peek() and self.peek().tipo == 'OPERATOR' and self.peek().valor == '[':
                    self.get_token()  # Consumir '['
                    cierre = self.get_token()  # Consumir ']'
                    if not cierre or cierre.valor != ']':
                        raise SyntaxError("Error: Se esperaba ']'")
                
                # Manejar arrays bidimensionales
                if self.peek() and self.peek().tipo == 'OPERATOR' and self.peek().valor == '[':
                    self.get_token()  # Consumir '['
                    if self.peek() and self.peek().valor == '[':
                        self.get_token()  # Consumir segundo '['
                        cierre = self.get_token()  # Consumir ']'
                        if not cierre or cierre.valor != ']':
                            raise SyntaxError("Error: Se esperaba ']'")
            
            # Obtener identificador
            token_key = self.get_token()
            if token_key.tipo != 'IDENTIFIER':
                raise SyntaxError('Error: Se esperaba un identificador, se encontró ' + str(token_key.valor))
            
            # Obtener '='
            token_eq = self.get_token()
            if token_eq.valor != '=':
                raise SyntaxError('Error: Se esperaba "=", se encontró ' + str(token_eq.valor))
            
            # Parsear valor
            valor = self.parse_valor()
            
            # Consumir punto y coma opcional
            if self.peek() and self.peek().valor == ';':
                self.get_token()
            
            # Agregar a la tabla de símbolos
            self.tabla_simbolos[token_key.valor] = valor
        
        return self.tabla_simbolos
    
    def get_token(self):
        """Obtiene el token actual y avanza la posición"""
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return None
    
    def peek(self):
        """Observa el token actual sin avanzar"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def parse_valor(self):
        """Parsea un valor (string, número, booleano, array u objeto)"""
        token = self.peek()
        if token is None:
            raise SyntaxError('Error: Se esperaba un valor después de "="')
        
        # String o número
        if token.tipo in ['STRING', 'NUMBER']:
            self.pos += 1
            return token.valor
        
        # Operadores: { o [
        if token.tipo == 'OPERATOR':
            if token.valor == '{':
                return self.parse_bloque()
            elif token.valor == '[':
                return self.parse_lista()
        
        # Booleanos
        if token.tipo == 'KEYWORD':
            if token.valor == 'True':
                self.pos += 1
                return True
            elif token.valor == 'False':
                self.pos += 1
                return False
        
        # Identificador sin definir
        if token.tipo == 'IDENTIFIER':
            raise SyntaxError('Error: Valor inesperado "' + token.valor + '"')
        
        raise SyntaxError('Error: Valor inesperado "' + str(token.valor) + '"')
    
    def parse_bloque(self):
        """Parsea un bloque (objeto/thing) delimitado por {}"""
        self.get_token()  # Consumir '{'
        contenido = {}
        
        while self.peek() and self.peek().valor != '}':
            # Consumir palabra clave de tipo opcional
            if self.peek().tipo == 'KEYWORD':
                self.get_token()
                
                # Manejar arrays
                if self.peek() and self.peek().tipo == 'OPERATOR' and self.peek().valor == '[':
                    self.get_token()  # '['
                    cierre = self.get_token()  # ']'
                    if not cierre or cierre.valor != ']':
                        raise SyntaxError("Error: Se esperaba ']'")
            
            # Obtener identificador
            token_key = self.get_token()
            if not token_key or token_key.tipo != 'IDENTIFIER':
                raise SyntaxError('Error en bloque: Se esperaba un identificador')
            
            # Obtener '='
            token_eq = self.get_token()
            if not token_eq or token_eq.valor != '=':
                raise SyntaxError('Error en bloque: Se esperaba "="')
            
            # Parsear valor
            valor = self.parse_valor()
            
            # Consumir punto y coma opcional
            if self.peek() and self.peek().valor == ';':
                self.get_token()
            
            contenido[token_key.valor] = valor
        
        # Consumir '}'
        cierre = self.get_token()
        if not cierre or cierre.valor != '}':
            raise SyntaxError('Error: Se esperaba "}"')
        
        return contenido
    
    def parse_lista(self):
        """Parsea una lista (array) delimitada por []"""
        self.get_token()  # Consumir '['
        contenido = []
        
        while self.peek() and self.peek().valor != ']':
            token_actual = self.peek()
            
            # Si es un identificador, buscar en la tabla de símbolos
            if token_actual.tipo == 'IDENTIFIER':
                self.get_token()
                identificador = token_actual.valor
                if identificador not in self.tabla_simbolos:
                    raise NameError('Error semántico: "' + identificador + '" no definido')
                contenido.append(self.tabla_simbolos[identificador])
            else:
                # Parsear valor normal
                valor = self.parse_valor()
                contenido.append(valor)
            
            # Procesar coma separadora
            if self.peek() and self.peek().valor == ',':
                self.get_token()
            elif self.peek() and self.peek().valor != ']':
                raise SyntaxError('Error en lista: Se esperaba "," o "]"')
        
        # Consumir ']'
        cierre = self.get_token()
        if not cierre or cierre.valor != ']':
            raise SyntaxError('Error: Se esperaba "]"')
        
        return contenido

def cargar_archivo(ruta):
    """Lee el contenido de un archivo"""
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            return f.read()
    except IOError:
        try:
            # Python 2 fallback sin encoding
            with open(ruta, 'r') as f:
                return f.read().decode('utf-8')
        except IOError:
            print('Error: No se pudo leer el archivo: ' + ruta)
            return None

def guardar_json(ast, ruta):
    """Guarda el AST en formato JSON"""
    try:
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(ast, f, indent=2, ensure_ascii=False)
        print('AST guardado en: ' + ruta)
    except:
        # Python 2 fallback
        with open(ruta, 'w') as f:
            json.dump(ast, f, indent=2, ensure_ascii=False)
        print('AST guardado en: ' + ruta)

def main():
    """Función principal del compilador"""
    if len(sys.argv) > 1:
        archivo_entrada = sys.argv[1]
    else:
        # Modo interactivo
        if sys.version_info[0] >= 3:
            archivo_entrada = input('Ingresa la dirreción del archivo:  ')
        else:
            archivo_entrada = raw_input('Ingresa la dirreción del archivo:  ')
    
    # Cargar código fuente
    codigo = cargar_archivo(archivo_entrada)
    if codigo is None:
        return
    
    try:
        # Análisis léxico
        print('\n--- Analisis Lexico (Lexer) ---')
        tokenizador = Tokenizador(codigo)
        tokens = tokenizador.tokenizar()
        print('Tokens reconocidos:')
        for token in tokens:
            print(token)
        
        # Análisis sintáctico
        print('\n--- Analisis Sintactico (Parser) ---')
        parser = Parser(tokens)
        ast = parser.parse()
        print('Sintaxis correcta. AST construido.')
        
        # Guardar AST
        archivo_salida = archivo_entrada.replace('.brik', '.json')
        guardar_json(ast, archivo_salida)
        
        print('\nCompilacion exitosa!')
        print('Archivo generado: ' + archivo_salida)
        
    except (ValueError, SyntaxError, NameError) as e:
        print('\nError: ' + str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()
