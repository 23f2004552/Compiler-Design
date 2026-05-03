from compiler.ast_nodes import *

class ConstantFolder:
    def optimize(self, node):
        if isinstance(node, Program):
            optimized_stmts = [self.optimize(stmt) for stmt in node.statements]
            return Program(statements=optimized_stmts, line=node.line, col=node.col)
        
        elif isinstance(node, Assignment):
            node.expression = self.optimize(node.expression)
            return node
            
        elif isinstance(node, PrintStmt):
            node.expression = self.optimize(node.expression)
            return node
            
        elif isinstance(node, Conditional):
            node.condition = self.optimize(node.condition)
            node.if_body = [self.optimize(stmt) for stmt in node.if_body]
            if node.else_body:
                node.else_body = [self.optimize(stmt) for stmt in node.else_body]
            return node
            
        elif isinstance(node, Condition):
            node.left = self.optimize(node.left)
            node.right = self.optimize(node.right)
            return node
            
        elif isinstance(node, BinOp):
            node.left = self.optimize(node.left)
            node.right = self.optimize(node.right)
            
            # Constant folding logic
            if isinstance(node.left, Number) and isinstance(node.right, Number):
                lval = node.left.value
                rval = node.right.value
                op = node.operator
                
                if op == '+': result = lval + rval
                elif op == '-': result = lval - rval
                elif op == '*': result = lval * rval
                elif op == '/': result = lval / rval if rval != 0 else 0
                else: return node
                
                return Number(value=result, line=node.line, col=node.col)
            
            return node
            
        return node
