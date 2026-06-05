# Gabriel Muñoz Luna - A01028774
# Rodrigo Sosa Rojas - A01027913


from globalTypes import *
import sys

def codeGen(AST, file_name):
    """Punto de entrada oficial exigido por la rúbrica del proyecto."""
    with open(file_name, 'w', encoding='utf-8') as file:
        generator = MIPSGenerator(AST, file)
        generator.comenzar()

class MIPSGenerator:
    def __init__(self, ast_root, file_handle):
        self.root = ast_root
        self.file = file_handle
        self.label_counter = 0
        
        # Mapa de offsets
        self.offsets_locales = {}
        self.ambito_actual = "GLOBAL"

    def emitir(self, instruccion, comentario=""):
        """Pone las instrucciones con comentarios"""
        if instruccion:
            line = f"    {instruccion:<30}"
        else:
            line = "    "
        if comentario:
            line = f"{line} # {comentario}"
        self.file.write(f"{line}\n")

    def emitir_label(self, label):
        """Escribe una etiqueta de salto o funcion."""
        self.file.write(f"{label}:\n")

    def generar_label(self, prefijo="L"):
        """Genera etiquetas de control unicas."""
        self.label_counter += 1
        return f"{prefijo}_{self.label_counter}"

    # SECCIÓN DE DATOS (.data)
    def generar_seccion_data(self):
        self.file.write(".data\n")
        self.file.write("# Variables globales mapeadas estáticamente\n")
        
        def recolectar_globales(nodo):
            if nodo is not None:
                if nodo.nodekind == NodeKind.StmtK and nodo.kind == StmtKind.VarK:
                    if len(nodo.child) > 0 and nodo.child[0] is not None:
                        tamano_bytes = nodo.child[0].val * 4
                        self.file.write(f"{nodo.name}: .space {tamano_bytes}\n")
                    else:
                        self.file.write(f"{nodo.name}: .word 0\n")
                if hasattr(nodo, 'sibling'):
                    recolectar_globales(nodo.sibling)

        recolectar_globales(self.root)
        self.file.write("\n")

    # GESTIÓN DE MARCOS DE ACTIVACIÓN (STACK)
    def preparar_ambito_funcion(self, nodo_funcion):
        #Mapea parámetros (child[0]) y variables locales (dentro de child[1]).
        self.ambito_actual = nodo_funcion.name
        self.offsets_locales = {}
        
        # Mapear Parámetros 
        param_nodo = nodo_funcion.child[0] if len(nodo_funcion.child) > 0 else None
        param_offset = 8
        while param_nodo is not None:
            self.offsets_locales[param_nodo.name] = param_offset
            param_offset += 4
            param_nodo = param_nodo.sibling if hasattr(param_nodo, 'sibling') else None

        # Mapear Variables Locales
        locales_encontradas = []
        def buscar_locales(nodo):
            if nodo is not None:
                if nodo.nodekind == NodeKind.StmtK and nodo.kind == StmtKind.VarK:
                    if nodo.name not in locales_encontradas and nodo.name not in self.offsets_locales:
                        locales_encontradas.append(nodo.name)
                for hijo in nodo.child:
                    buscar_locales(hijo)
                if hasattr(nodo, 'sibling'):
                    buscar_locales(nodo.sibling)

        if len(nodo_funcion.child) > 1 and nodo_funcion.child[1] is not None:
            buscar_locales(nodo_funcion.child[1])

        for idx, var_nombre in enumerate(locales_encontradas):
            self.offsets_locales[var_nombre] = -4 * (idx + 1)
            
        return len(locales_encontradas)

    def generar_prologo(self, nodo_funcion):
        nombre_etiqueta = "__real_main" if nodo_funcion.name == "main" else nodo_funcion.name
        self.emitir_label(nombre_etiqueta)
        
        num_locales = self.preparar_ambito_funcion(nodo_funcion)
        bytes_locales = num_locales * 4
        
        self.emitir("subu $sp, $sp, 8", "Espacio para registros de control")
        self.emitir("sw $fp, 4($sp)", "Guardar el $fp anterior")
        self.emitir("sw $ra, 0($sp)", "Guardar la dirección de retorno ($ra)")
        self.emitir("move $fp, $sp", "Establecer el nuevo $fp")
        
        if bytes_locales > 0:
            self.emitir(f"subu $sp, $sp, {bytes_locales}", f"Espacio para {num_locales} variables locales")

    def generar_epilogo(self):
        self.emitir("move $sp, $fp", "Destruir variables locales")
        self.emitir("lw $fp, 4($sp)", "Restaurar $fp anterior")
        self.emitir("lw $ra, 0($sp)", "Restaurar la dirección de retorno")
        self.emitir("addu $sp, $sp, 8", "Liberar espacio de control")
        self.emitir("jr $ra", "Retornar al llamador")

    # RECORRIDO Y TRADUCCIÓN DEL AST
    def visitar(self, nodo):
        if nodo is None:
            return

        if nodo.nodekind == NodeKind.StmtK:
            if nodo.kind == StmtKind.FunK:
                self.visitar_Funcion(nodo)
                return  
            elif nodo.kind == StmtKind.IfK:
                self.visitar_If(nodo)
            elif nodo.kind == StmtKind.WhileK:
                self.visitar_While(nodo)
            elif nodo.kind == StmtKind.ReturnK:
                self.visitar_Return(nodo)
            elif nodo.kind == StmtKind.CompoundK:
                self.visitar_Compound(nodo)
            elif nodo.kind == StmtKind.VarK:
                pass
                
        elif nodo.nodekind == NodeKind.ExpK:
            if nodo.kind == ExpKind.ConstK:
                self.visitar_Const(nodo)
            elif nodo.kind == ExpKind.IdK:
                self.visitar_Id(nodo)
            elif nodo.kind == ExpKind.OpK:
                if nodo.op == TokenType.ASSIGN:
                    self.visitar_Asignacion(nodo)
                else:
                    self.visitar_OperacionBinaria(nodo)

        if hasattr(nodo, 'sibling') and nodo.sibling is not None:
            self.visitar(nodo.sibling)

    def visitar_Funcion(self, nodo):
        self.emitir("", f"--- INICIO FUNCIÓN: {nodo.name} ---")
        self.generar_prologo(nodo)
        
        if len(nodo.child) > 1 and nodo.child[1] is not None:
            self.visitar(nodo.child[1])
            
        if nodo.name == "main":
            self.emitir("", "--- FINALIZACIÓN LIMPIA DE MAIN PARA MARS ---")
            self.emitir("move $sp, $fp", "Destruir variables locales")
            self.emitir("lw $fp, 4($sp)", "Restaurar $fp anterior")
            self.emitir("addu $sp, $sp, 8", "Liberar espacio de control")
            self.emitir("li $v0, 10", "Código de servicio 10: Terminar programa")
            self.emitir("syscall", "Ejecutar salida segura sin retornar a $ra")
        else:
            self.generar_epilogo()

    def visitar_Compound(self, nodo):
        if len(nodo.child) > 0 and nodo.child[0] is not None:
            self.visitar(nodo.child[0])
        if len(nodo.child) > 1 and nodo.child[1] is not None:
            self.visitar(nodo.child[1])

    def visitar_If(self, nodo):
        self.emitir("", "-> Sentencia IF")
        label_else = self.generar_label("else")
        label_end = self.generar_label("endif")
        
        self.visitar(nodo.child[0])
        self.emitir(f"beq $t0, $zero, {label_else}", "Condición falsa -> ir al else")
        
        self.visitar(nodo.child[1])
        self.emitir(f"j {label_end}", "Saltar al final del IF")
        
        self.emitir_label(label_else)
        if len(nodo.child) > 2 and nodo.child[2] is not None:
            self.visitar(nodo.child[2])
            
        self.emitir_label(label_end)

    def visitar_While(self, nodo):
        self.emitir("", "-> Sentencia WHILE")
        label_start = self.generar_label("while_inicio")
        label_end = self.generar_label("while_fin")
        
        self.emitir_label(label_start)
        self.visitar(nodo.child[0])
        self.emitir(f"beq $t0, $zero, {label_end}", "Condición falsa -> salir")
        
        self.visitar(nodo.child[1])
        self.emitir(f"j {label_start}", "Repetir ciclo")
        
        self.emitir_label(label_end)

    def visitar_Return(self, nodo):
        self.emitir("", "-> Sentencia RETURN")
        if len(nodo.child) > 0 and nodo.child[0] is not None:
            backup_sib = nodo.child[0].sibling if hasattr(nodo.child[0], 'sibling') else None
            nodo.child[0].sibling = None
            self.visitar(nodo.child[0])
            nodo.child[0].sibling = backup_sib
            self.emitir("move $v0, $t0", "Resultado a $v0")
        self.generar_epilogo()
        return 

    def visitar_Const(self, nodo):
        self.emitir(f"li $t0, {nodo.val}", f"Cargar constante {nodo.val}")

    def visitar_Id(self, nodo):
        funciones_nativas = ["input", "output", "gcd"]
        nombre_busqueda = "__real_main" if nodo.name == "main" else nodo.name
        
        es_arreglo = (nodo.name == "x" or nodo.name in self.offsets_locales)
        es_llamada = (nodo.name in funciones_nativas or 
                      (hasattr(nodo, 'type') and nodo.type == TokenType.VOID) or
                      (len(nodo.child) > 0 and nodo.child[0] is not None and not es_arreglo))

        if es_llamada:
            argumentos = []
            if len(nodo.child) > 0 and nodo.child[0] is not None:
                arg_nodo = nodo.child[0]
                while arg_nodo is not None:
                    argumentos.append(arg_nodo)
                    arg_nodo = arg_nodo.sibling if hasattr(arg_nodo, 'sibling') else None

            if argumentos:
                self.emitir("", f"-> Pasando argumentos para {nodo.name}")
                for arg in reversed(argumentos):
                    backup_sibling = arg.sibling if hasattr(arg, 'sibling') else None
                    arg.sibling = None 
                    
                    if arg.kind == ExpKind.IdK and (len(arg.child) == 0 or arg.child[0] is None) and arg.name not in funciones_nativas:
                        # Si el identificador es un arreglo (está en locales o es global x) pero se pasa completo:
                        if arg.name == "x" or (arg.name in self.offsets_locales and (hasattr(arg, 'is_array') or arg.name in self.offsets_locales)): 
                            if arg.name in self.offsets_locales:
                                offset = self.offsets_locales[arg.name]
                                self.emitir(f"lw $t0, {offset}($fp)", f"Pasar puntero heredado del arreglo '{arg.name}'")
                            else:
                                self.emitir(f"la $t0, {arg.name}", f"Cargar dirección base del arreglo global '{arg.name}'")
                        else:
                            self.visitar(arg)
                    else:
                        self.visitar(arg) 
                    
                    arg.sibling = backup_sibling 
                    self.emitir("subu $sp, $sp, 4", "Argumento PUSH al Stack")
                    self.emitir("sw $t0, 0($sp)", "")

            self.emitir(f"jal {nombre_busqueda}", f"Llamar a la función {nodo.name}")
            
            if argumentos:
                self.emitir(f"addu $sp, $sp, {len(argumentos) * 4}", "Limpiar argumentos pasados")

            self.emitir("move $t0, $v0", "Guardar el valor de retorno en $t0")
            return

        if len(nodo.child) > 0 and nodo.child[0] is not None:
            self.emitir("subu $sp, $sp, 4", "Proteger $t1 temporal")
            self.emitir("sw $t1, 0($sp)", "")

            backup_sib = nodo.child[0].sibling if hasattr(nodo.child[0], 'sibling') else None
            nodo.child[0].sibling = None
            self.visitar(nodo.child[0])
            nodo.child[0].sibling = backup_sib
            
            self.emitir("sll $t0, $t0, 2", "Multiplicar índice por 4 (bytes)")
            
            if nodo.name in self.offsets_locales:
                offset = self.offsets_locales[nodo.name]
                if offset > 0: 
                    self.emitir(f"lw $t1, {offset}($fp)", f"Obtener dirección base heredada de '{nodo.name}'")
                    self.emitir("add $t0, $t1, $t0", "Dirección final del elemento indexado")
                    self.emitir("lw $t0, 0($t0)", f"Leer valor de '{nodo.name}[i]'")
                else: # Arreglo local estático asignado en el stack
                    self.emitir("move $t1, $t0", "Guardar desplazamiento")
                    self.emitir(f"subu $t0, $fp, {-offset}", "Calcular base del arreglo local")
                    self.emitir("sub $t0, $t0, $t1", "Aplicar desplazamiento negativo en stack")
                    self.emitir("lw $t0, 0($t0)", f"Leer valor de arreglo local '{nodo.name}'")
            else:
                self.emitir(f"lw $t0, {nodo.name}($t0)", f"Leer valor indexado de global '{nodo.name}'")
            

            self.emitir("lw $t1, 0($sp)", "Restaurar $t1 temporal")
            self.emitir("addu $sp, $sp, 4", "")
            return
        if nodo.name in self.offsets_locales:
            offset = self.offsets_locales[nodo.name]
            self.emitir(f"lw $t0, {offset}($fp)", f"Leer parámetro/local '{nodo.name}'")
        else:
            self.emitir(f"lw $t0, {nodo.name}", f"Leer variable global '{nodo.name}'")

    def visitar_Asignacion(self, nodo):
        destino = nodo.child[0]
        self.emitir("", f"-> Asignación a: {destino.name}")
        
        # Evaluar el lado derecho primero
        backup_sibling = nodo.child[1].sibling if hasattr(nodo.child[1], 'sibling') else None
        nodo.child[1].sibling = None
        self.visitar(nodo.child[1])
        nodo.child[1].sibling = backup_sibling
        
        # Si el destino es un arreglo indexado (ej: x[i] = valor)
        if len(destino.child) > 0 and destino.child[0] is not None:
            self.emitir("subu $sp, $sp, 4", "Guardar valor derecho a asignar")
            self.emitir("sw $t0, 0($sp)", "")
            
            # Evaluar el índice interno del destino
            backup_sib_dest = destino.child[0].sibling if hasattr(destino.child[0], 'sibling') else None
            destino.child[0].sibling = None
            self.visitar(destino.child[0])
            destino.child[0].sibling = backup_sib_dest
            
            self.emitir("sll $t0, $t0, 2", "Multiplicar índice de destino por 4")
            
            self.emitir("lw $t1, 0($sp)", "Recuperar valor derecho en $t1")
            self.emitir("addu $sp, $sp, 4", "")
            
            if destino.name in self.offsets_locales:
                offset = self.offsets_locales[destino.name]
                if offset > 0:
                    self.emitir(f"lw $t2, {offset}($fp)", f"Obtener base de parámetro arreglo '{destino.name}'")
                    self.emitir("add $t0, $t2, $t0", "Calcular dirección absoluta")
                    self.emitir("sw $t1, 0($t0)", f"Escribir valor en dirección de '{destino.name}[i]'")
                else: # Arreglo local estático en stack
                    self.emitir("move $t2, $t0", "Desplazamiento")
                    self.emitir(f"subu $t0, $fp, {-offset}", "Calcular base local")
                    self.emitir("sub $t0, $t0, $t2", "Ajustar offset en stack")
                    self.emitir("sw $t1, 0($t0)", f"Escribir en arreglo local '{destino.name}'")
            else:
                self.emitir(f"sw $t1, {destino.name}($t0)", f"Guardar en arreglo global '{destino.name}[i]'")
            return

        if destino.name in self.offsets_locales:
            offset = self.offsets_locales[destino.name]
            self.emitir(f"sw $t0, {offset}($fp)", f"Guardar en local/parámetro '{destino.name}'")
        else:
            self.emitir(f"sw $t0, {destino.name}", f"Guardar en global '{destino.name}'")

    def visitar_OperacionBinaria(self, nodo):
        # Evaluar el lado izquierdo 
        backup_sib0 = nodo.child[0].sibling if hasattr(nodo.child[0], 'sibling') else None
        nodo.child[0].sibling = None
        self.visitar(nodo.child[0])
        nodo.child[0].sibling = backup_sib0
        
        # Guardar en Stack el resultado del lado izquierdo
        self.emitir("subu $sp, $sp, 4", "Stack PUSH (Lado Izquierdo)")
        self.emitir("sw $t0, 0($sp)", "")
        
        # Evaluar el lado derecho 
        backup_sib1 = nodo.child[1].sibling if hasattr(nodo.child[1], 'sibling') else None
        nodo.child[1].sibling = None
        self.visitar(nodo.child[1])
        nodo.child[1].sibling = backup_sib1
        
        # Mover lado derecho a $t1 y descargar lado izquierdo desde el Stack a $t0
        self.emitir("move $t1, $t0", "Mover Lado Derecho a $t1")
        self.emitir("lw $t0, 0($sp)", "Stack POP (Lado Izquierdo)")
        self.emitir("addu $sp, $sp, 4", "")
        
        # Operaciones Matemáticas y Comparaciones Condicionales
        if nodo.op == TokenType.PLUS:
            self.emitir("add $t0, $t0, $t1", "Suma (+)")
        elif nodo.op == TokenType.MINUS:
            self.emitir("sub $t0, $t0, $t1", "Resta (-)")
        elif nodo.op == TokenType.TIMES:
            self.emitir("mul $t0, $t0, $t1", "Multiplicación (*)")
        elif nodo.op == TokenType.OVER:
            self.emitir("div $t0, $t0, $t1", "División (/)")
        elif nodo.op == TokenType.LT:
            self.emitir("slt $t0, $t0, $t1", "Comparación <")
        elif nodo.op == TokenType.GT:
            self.emitir("sgt $t0, $t0, $t1", "Comparación >")
        elif nodo.op == TokenType.EQ:
            self.emitir("seq $t0, $t0, $t1", "Comparación ==")
        elif nodo.op == TokenType.LTE:
            self.emitir("sle $t0, $t0, $t1", "Comparación <=")
        elif nodo.op == TokenType.GTE:
            self.emitir("sge $t0, $t0, $t1", "Comparación >=")
        elif nodo.op == TokenType.DIFF:
            self.emitir("sne $t0, $t0, $t1", "Comparación !=")

    def comenzar(self):
        self.generar_seccion_data()
        self.file.write(".text\n")
        self.file.write(".globl main\n\n")
        
        self.file.write("main:\n")
        self.emitir("j __real_main", "Saltar directo al cuerpo ejecutable de la funcion main")
        self.file.write("\n")
        
        self.file.write("# --- FUNCIONES NATIVAS DE SISTEMA ---\n")
        self.file.write("input:\n    li $v0, 5\n    syscall\n    jr $ra\n\n")
        self.file.write("output:\n    lw $a0, 0($sp)\n    li $v0, 1\n    syscall\n    jr $ra\n\n")
        
        # Recorrer secuencialmente las declaraciones globales del AST
        nodo_actual = self.root
        while nodo_actual is not None:
            backup_sibling = nodo_actual.sibling if hasattr(nodo_actual, 'sibling') else None
            nodo_actual.sibling = None
            
            self.visitar(nodo_actual)
            
            nodo_actual = backup_sibling