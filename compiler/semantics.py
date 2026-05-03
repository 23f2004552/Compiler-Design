from compiler.ast_nodes import *
from compiler.errors import SemanticError

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = set()

    def analyze(self, node):
        if isinstance(node, Program):
            for stmt in node.statements:
                self.analyze(stmt)
        
        elif isinstance(node, Assignment):
            # Check the expression first
            self.analyze(node.expression)
            # Then mark the variable as declared
            self.symbol_table.add(node.identifier)
            
        elif isinstance(node, PrintStmt):
            self.analyze(node.expression)
            
        elif isinstance(node, Conditional):
            self.analyze(node.condition)
            # Analyze both branches
            for stmt in node.if_body:
                self.analyze(stmt)
            if node.else_body:
                for stmt in node.else_body:
                    self.analyze(stmt)
                    
        elif isinstance(node, Condition):
            self.analyze(node.left)
            self.analyze(node.right)
            
        elif isinstance(node, BinOp):
            self.analyze(node.left)
            self.analyze(node.right)
            
        elif isinstance(node, Identifier):
            if node.name not in self.symbol_table:
                raise SemanticError(f"Variable '{node.name}' used before declaration.", node.line, node.col)
            
        elif isinstance(node, Number):
            pass
