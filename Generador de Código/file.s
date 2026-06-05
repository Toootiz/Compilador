.data
# Variables globales mapeadas estáticamente

.text
.globl main

main:
    j __real_main                  # Saltar directo al cuerpo ejecutable de la funcion main

# --- FUNCIONES NATIVAS DE SISTEMA ---
input:
    li $v0, 5
    syscall
    jr $ra

output:
    lw $a0, 0($sp)
    li $v0, 1
    syscall
    jr $ra

     # --- INICIO FUNCIÓN: gcd ---
gcd:
    subu $sp, $sp, 8               # Espacio para registros de control
    sw $fp, 4($sp)                 # Guardar el $fp anterior
    sw $ra, 0($sp)                 # Guardar la dirección de retorno ($ra)
    move $fp, $sp                  # Establecer el nuevo $fp
     # -> Sentencia IF
    lw $t0, 12($fp)                # Leer parámetro/local 'v'
    subu $sp, $sp, 4               # Stack PUSH (Lado Izquierdo)
    sw $t0, 0($sp)                
    li $t0, 0                      # Cargar constante 0
    move $t1, $t0                  # Mover Lado Derecho a $t1
    lw $t0, 0($sp)                 # Stack POP (Lado Izquierdo)
    addu $sp, $sp, 4              
    seq $t0, $t0, $t1              # Comparación ==
    beq $t0, $zero, else_1         # Condición falsa -> ir al else
     # -> Sentencia RETURN
    lw $t0, 8($fp)                 # Leer parámetro/local 'u'
    move $v0, $t0                  # Resultado a $v0
    move $sp, $fp                  # Destruir variables locales
    lw $fp, 4($sp)                 # Restaurar $fp anterior
    lw $ra, 0($sp)                 # Restaurar la dirección de retorno
    addu $sp, $sp, 8               # Liberar espacio de control
    jr $ra                         # Retornar al llamador
    j endif_2                      # Saltar al final del IF
else_1:
     # -> Sentencia RETURN
     # -> Pasando argumentos para gcd
    lw $t0, 8($fp)                 # Leer parámetro/local 'u'
    subu $sp, $sp, 4               # Stack PUSH (Lado Izquierdo)
    sw $t0, 0($sp)                
    lw $t0, 8($fp)                 # Leer parámetro/local 'u'
    subu $sp, $sp, 4               # Stack PUSH (Lado Izquierdo)
    sw $t0, 0($sp)                
    lw $t0, 12($fp)                # Leer parámetro/local 'v'
    move $t1, $t0                  # Mover Lado Derecho a $t1
    lw $t0, 0($sp)                 # Stack POP (Lado Izquierdo)
    addu $sp, $sp, 4              
    div $t0, $t0, $t1              # División (/)
    subu $sp, $sp, 4               # Stack PUSH (Lado Izquierdo)
    sw $t0, 0($sp)                
    lw $t0, 12($fp)                # Leer parámetro/local 'v'
    move $t1, $t0                  # Mover Lado Derecho a $t1
    lw $t0, 0($sp)                 # Stack POP (Lado Izquierdo)
    addu $sp, $sp, 4              
    mul $t0, $t0, $t1              # Multiplicación (*)
    move $t1, $t0                  # Mover Lado Derecho a $t1
    lw $t0, 0($sp)                 # Stack POP (Lado Izquierdo)
    addu $sp, $sp, 4              
    sub $t0, $t0, $t1              # Resta (-)
    subu $sp, $sp, 4               # Argumento PUSH al Stack
    sw $t0, 0($sp)                
    lw $t0, 12($fp)                # Pasar puntero heredado del arreglo 'v'
    subu $sp, $sp, 4               # Argumento PUSH al Stack
    sw $t0, 0($sp)                
    jal gcd                        # Llamar a la función gcd
    addu $sp, $sp, 8               # Limpiar argumentos pasados
    move $t0, $v0                  # Guardar el valor de retorno en $t0
    move $v0, $t0                  # Resultado a $v0
    move $sp, $fp                  # Destruir variables locales
    lw $fp, 4($sp)                 # Restaurar $fp anterior
    lw $ra, 0($sp)                 # Restaurar la dirección de retorno
    addu $sp, $sp, 8               # Liberar espacio de control
    jr $ra                         # Retornar al llamador
endif_2:
    move $sp, $fp                  # Destruir variables locales
    lw $fp, 4($sp)                 # Restaurar $fp anterior
    lw $ra, 0($sp)                 # Restaurar la dirección de retorno
    addu $sp, $sp, 8               # Liberar espacio de control
    jr $ra                         # Retornar al llamador
     # --- INICIO FUNCIÓN: main ---
__real_main:
    subu $sp, $sp, 8               # Espacio para registros de control
    sw $fp, 4($sp)                 # Guardar el $fp anterior
    sw $ra, 0($sp)                 # Guardar la dirección de retorno ($ra)
    move $fp, $sp                  # Establecer el nuevo $fp
    subu $sp, $sp, 8               # Espacio para 2 variables locales
     # -> Asignación a: x
    jal input                      # Llamar a la función input
    move $t0, $v0                  # Guardar el valor de retorno en $t0
    sw $t0, -4($fp)                # Guardar en local/parámetro 'x'
     # -> Asignación a: y
    jal input                      # Llamar a la función input
    move $t0, $v0                  # Guardar el valor de retorno en $t0
    sw $t0, -8($fp)                # Guardar en local/parámetro 'y'
     # -> Pasando argumentos para output
     # -> Pasando argumentos para gcd
    lw $t0, -8($fp)                # Pasar puntero heredado del arreglo 'y'
    subu $sp, $sp, 4               # Argumento PUSH al Stack
    sw $t0, 0($sp)                
    lw $t0, -4($fp)                # Pasar puntero heredado del arreglo 'x'
    subu $sp, $sp, 4               # Argumento PUSH al Stack
    sw $t0, 0($sp)                
    jal gcd                        # Llamar a la función gcd
    addu $sp, $sp, 8               # Limpiar argumentos pasados
    move $t0, $v0                  # Guardar el valor de retorno en $t0
    subu $sp, $sp, 4               # Argumento PUSH al Stack
    sw $t0, 0($sp)                
    jal output                     # Llamar a la función output
    addu $sp, $sp, 4               # Limpiar argumentos pasados
    move $t0, $v0                  # Guardar el valor de retorno en $t0
     # --- FINALIZACIÓN LIMPIA DE MAIN PARA MARS ---
    move $sp, $fp                  # Destruir variables locales
    lw $fp, 4($sp)                 # Restaurar $fp anterior
    addu $sp, $sp, 8               # Liberar espacio de control
    li $v0, 10                     # Código de servicio 10: Terminar programa
    syscall                        # Ejecutar salida segura sin retornar a $ra
