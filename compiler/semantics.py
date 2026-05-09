from compiler.ast_nodes import *
from compiler.errors import SemanticError

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {} # name -> type string ('int' or 'float')

    def analyze(self, node):
        if isinstance(node, Program):
            for stmt in node.statements:
                self.analyze(stmt)
        
        elif isinstance(node, Assignment):
            expr_type = self.analyze(node.expression)
            self.symbol_table[node.identifier] = expr_type
            
        elif isinstance(node, PrintStmt):
            self.analyze(node.expression)
            
        elif isinstance(node, Conditional):
            self.analyze(node.condition)
            for stmt in node.if_body:
                self.analyze(stmt)
            if node.else_body:
                for stmt in node.else_body:
                    self.analyze(stmt)
                    
        elif isinstance(node, Condition):
            self.analyze(node.left)
            self.analyze(node.right)
            
        elif isinstance(node, BinOp):
            l_type = self.analyze(node.left)
            r_type = self.analyze(node.right)
            
            if l_type == 'float' and r_type == 'int':
                node.right = IntToFloat(expression=node.right, line=node.right.line, col=node.right.col)
                return 'float'
            elif l_type == 'int' and r_type == 'float':
                node.left = IntToFloat(expression=node.left, line=node.left.line, col=node.left.col)
                return 'float'
            elif l_type == 'float' or r_type == 'float':
                return 'float'
            return 'int'
            
        elif isinstance(node, Identifier):
            if node.name not in self.symbol_table:
                raise SemanticError(f"Variable '{node.name}' used before declaration.", node.line, node.col)
            return self.symbol_table[node.name]
            
        elif isinstance(node, Number):
            return 'float' if isinstance(node.value, float) else 'int'
            
        elif isinstance(node, IntToFloat):
            return 'float'
