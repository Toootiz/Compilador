from globalTypes import *
from lexer import *
f = open('sample.c-', 'r')

programa = f.read()
progLong = len(programa)
programa = programa + '$'
posicion = 0

# lee todo el archivo a compilar
# longitud original del programa
# agregar un caracter $ que represente EOF
# posición del caracter actual del string
# función para pasar los valores iniciales de las variables globales
globales(programa, posicion, progLong)
token, tokenString = getToken(True)
while (token != TokenType.ENDFILE):
    token, tokenString = getToken(True)