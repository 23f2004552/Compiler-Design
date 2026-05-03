class TACGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instruction):
        self.instructions.append(instruction)

    def generate(self, ast):
        self.visit(ast)
        return self.instructions

    def visit(self, node):
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'No visit_{node.__class__.__name__} method')

    def visit_Program(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_Assignment(self, node):
        val = self.visit(node.expression)
        self.emit(f"{node.identifier} = {val}")

    def visit_PrintStmt(self, node):
        val = self.visit(node.expression)
        self.emit(f"print {val}")

    def visit_Conditional(self, node):
        cond_val = self.visit(node.condition)
        l_true = self.new_label()
        l_end = self.new_label()
        l_false = self.new_label() if node.else_body else l_end
        
        self.emit(f"if {cond_val} goto {l_true}")
        self.emit(f"goto {l_false}")
        self.emit(f"{l_true}:")
        
        for stmt in node.if_body:
            self.visit(stmt)
            
        if node.else_body:
            self.emit(f"goto {l_end}")
            self.emit(f"{l_false}:")
            for stmt in node.else_body:
                self.visit(stmt)
                
        if l_end != l_false:
            self.emit(f"{l_end}:")
        else:
            self.emit(f"{l_end}:")

    def visit_Condition(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return f"{left} {node.operator} {right}"

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        temp = self.new_temp()
        self.emit(f"{temp} = {left} {node.operator} {right}")
        return temp

    def visit_Number(self, node):
        return str(node.value)

    def visit_Identifier(self, node):
        return node.name
