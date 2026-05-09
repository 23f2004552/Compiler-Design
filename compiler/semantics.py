from compiler.ast_nodes import *
from compiler.errors import SemanticError

class SemanticAnalyzer:
    def __init__(self):
        self.scopes = [{}] # List of dicts: name -> type string

    def current_scope(self):
        return self.scopes[-1]

    def resolve(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def analyze(self, node):
        if isinstance(node, Program):
            for stmt in node.statements:
                self.analyze(stmt)
                
        elif isinstance(node, Block):
            self.scopes.append({}) # Enter new scope
            for stmt in node.statements:
                self.analyze(stmt)
            self.scopes.pop() # Exit scope
        
        elif isinstance(node, Assignment):
            expr_type = self.analyze(node.expression)
            
            if node.var_type: # e.g. int x = 5;
                if node.identifier in self.current_scope():
                    raise SemanticError(f"Duplicate declaration of variable '{node.identifier}' in same scope.", node.line, node.col)
                # Type checking
                if node.var_type == 'int' and expr_type in ('float', 'string'):
                    if expr_type == 'string':
                        raise SemanticError(f"Type Mismatch: Cannot assign string to int '{node.identifier}'.", node.line, node.col)
                if node.var_type == 'string' and expr_type != 'string':
                    raise SemanticError(f"Type Mismatch: Cannot assign non-string to string '{node.identifier}'.", node.line, node.col)
                    
                self.current_scope()[node.identifier] = node.var_type
            else: # e.g. x = 5;
                if self.resolve(node.identifier) is None:
                    raise SemanticError(f"Variable '{node.identifier}' used before declaration.", node.line, node.col)
                # Could add strict type checking here based on resolve(node.identifier)
            return
            
        elif isinstance(node, PrintStmt):
            self.analyze(node.expression)
            
        elif isinstance(node, Conditional):
            self.analyze(node.condition)
            self.scopes.append({})
            for stmt in node.if_body:
                self.analyze(stmt)
            self.scopes.pop()
            
            if node.else_body:
                self.scopes.append({})
                for stmt in node.else_body:
                    self.analyze(stmt)
                self.scopes.pop()
                
        elif isinstance(node, WhileLoop):
            self.analyze(node.condition)
            self.scopes.append({})
            for stmt in node.body:
                self.analyze(stmt)
            self.scopes.pop()
                    
        elif isinstance(node, Condition):
            self.analyze(node.left)
            self.analyze(node.right)
            return 'bool'
            
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
            var_type = self.resolve(node.name)
            if var_type is None:
                raise SemanticError(f"Variable '{node.name}' used before declaration.", node.line, node.col)
            return var_type
            
        elif isinstance(node, Number):
            return 'float' if isinstance(node.value, float) else 'int'
            
        elif isinstance(node, StringLit):
            return 'string'
            
        elif isinstance(node, CharLit):
            return 'char'
            
        elif isinstance(node, IntToFloat):
            return 'float'
