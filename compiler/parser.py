from .errors import SyntaxError
from .ast_nodes import (
    Program, Assignment, Conditional, PrintStmt, 
    BinOp, Number, Identifier, Condition, StringLit, CharLit, WhileLoop, Block
)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def match(self, expected_type, expected_value=None):
        if self.current_token is None:
            line = getattr(self.tokens[-1], 'line', 1) if self.tokens else 1
            col = getattr(self.tokens[-1], 'col', 1) if self.tokens else 1
            raise SyntaxError(f"Expected {expected_type} '{expected_value}' but reached end of file", line, col)
            
        if self.current_token.type == expected_type and (expected_value is None or self.current_token.value == expected_value):
            token = self.current_token
            self.advance()
            return token
        else:
            val = expected_value if expected_value else expected_type
            raise SyntaxError(f"Expected '{val}', got '{self.current_token.value}'", self.current_token.line, self.current_token.col)

    def parse(self):
        first_tok = self.tokens[0] if self.tokens else None
        line, col = (first_tok.line, first_tok.col) if first_tok else (1, 1)
        statements = []
        while self.current_token is not None:
            statements.append(self.parse_statement())
        return Program(statements=statements, line=line, col=col)

    def parse_statement(self):
        if self.current_token.type == 'KEYWORD':
            if self.current_token.value in ('let', 'int', 'float', 'char', 'string'):
                return self.parse_assignment(is_declaration=True)
            elif self.current_token.value == 'if':
                return self.parse_conditional()
            elif self.current_token.value == 'while':
                return self.parse_while()
            elif self.current_token.value == 'print':
                return self.parse_print()
        elif self.current_token.type == 'IDENTIFIER':
            # Could be a function call or assignment. For now just assignment
            return self.parse_assignment(is_declaration=False)
        elif self.current_token.type == 'DELIM' and self.current_token.value == '{':
            return self.parse_block()
            
        raise SyntaxError(f"Expected statement, got '{self.current_token.value}'", self.current_token.line, self.current_token.col)

    def parse_block(self):
        block_tok = self.match('DELIM', '{')
        statements = []
        while self.current_token and not (self.current_token.type == 'DELIM' and self.current_token.value == '}'):
            statements.append(self.parse_statement())
        self.match('DELIM', '}')
        return Block(statements=statements, line=block_tok.line, col=block_tok.col)

    def parse_assignment(self, is_declaration=False):
        var_type = None
        line, col = self.current_token.line, self.current_token.col
        
        if is_declaration:
            type_tok = self.match('KEYWORD')
            var_type = type_tok.value
            
        ident_tok = self.match('IDENTIFIER')
        
        # Handle uninitialized declaration: int a;
        if self.current_token and self.current_token.type == 'DELIM' and self.current_token.value == ';':
            self.match('DELIM', ';')
            # Initialize with 0 implicitly
            expr = Number(value=0, line=ident_tok.line, col=ident_tok.col)
            return Assignment(identifier=ident_tok.value, expression=expr, var_type=var_type, line=line, col=col)
            
        self.match('OP', '=')
        expr = self.parse_expression()
        self.match('DELIM', ';')
        return Assignment(identifier=ident_tok.value, expression=expr, var_type=var_type, line=line, col=col)

    def parse_print(self):
        p_tok = self.match('KEYWORD', 'print')
        self.match('DELIM', '(')
        expr = self.parse_expression()
        self.match('DELIM', ')')
        self.match('DELIM', ';')
        return PrintStmt(expression=expr, line=p_tok.line, col=p_tok.col)

    def parse_conditional(self):
        if_tok = self.match('KEYWORD', 'if')
        self.match('DELIM', '(')
        cond = self.parse_expression()
        self.match('DELIM', ')')
        
        # Support block or single statement
        if self.current_token.type == 'DELIM' and self.current_token.value == '{':
            if_body = self.parse_block().statements
        else:
            if_body = [self.parse_statement()]
        
        else_body = None
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'else':
            self.match('KEYWORD', 'else')
            if self.current_token.type == 'DELIM' and self.current_token.value == '{':
                else_body = self.parse_block().statements
            else:
                else_body = [self.parse_statement()]
            
        # Optional 'end' to maintain compatibility with older minilang scripts
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'end':
            self.advance()
            
        return Conditional(condition=cond, if_body=if_body, else_body=else_body, line=if_tok.line, col=if_tok.col)

    def parse_while(self):
        w_tok = self.match('KEYWORD', 'while')
        self.match('DELIM', '(')
        cond = self.parse_expression()
        self.match('DELIM', ')')
        
        if self.current_token.type == 'DELIM' and self.current_token.value == '{':
            body = self.parse_block().statements
        else:
            body = [self.parse_statement()]
            
        return WhileLoop(condition=cond, body=body, line=w_tok.line, col=w_tok.col)

    def parse_expression(self):
        return self.parse_logical_or()
        
    def parse_logical_or(self):
        node = self.parse_logical_and()
        while self.current_token and self.current_token.type == 'LOGICAL' and self.current_token.value == '||':
            op_tok = self.current_token
            self.advance()
            right = self.parse_logical_and()
            node = Condition(left=node, operator=op_tok.value, right=right, line=op_tok.line, col=op_tok.col)
        return node
        
    def parse_logical_and(self):
        node = self.parse_equality()
        while self.current_token and self.current_token.type == 'LOGICAL' and self.current_token.value == '&&':
            op_tok = self.current_token
            self.advance()
            right = self.parse_equality()
            node = Condition(left=node, operator=op_tok.value, right=right, line=op_tok.line, col=op_tok.col)
        return node
        
    def parse_equality(self):
        node = self.parse_relational()
        while self.current_token and self.current_token.type == 'RELOP' and self.current_token.value in ('==', '!='):
            op_tok = self.current_token
            self.advance()
            right = self.parse_relational()
            node = Condition(left=node, operator=op_tok.value, right=right, line=op_tok.line, col=op_tok.col)
        return node
        
    def parse_relational(self):
        node = self.parse_additive()
        while self.current_token and self.current_token.type == 'RELOP' and self.current_token.value in ('<', '>', '<=', '>='):
            op_tok = self.current_token
            self.advance()
            right = self.parse_additive()
            node = Condition(left=node, operator=op_tok.value, right=right, line=op_tok.line, col=op_tok.col)
        return node

    def parse_additive(self):
        node = self.parse_multiplicative()
        while self.current_token and self.current_token.type == 'OP' and self.current_token.value in ('+', '-'):
            op_tok = self.current_token
            self.advance()
            right = self.parse_multiplicative()
            node = BinOp(left=node, operator=op_tok.value, right=right, line=op_tok.line, col=op_tok.col)
        return node

    def parse_multiplicative(self):
        node = self.parse_factor()
        while self.current_token and self.current_token.type == 'OP' and self.current_token.value in ('*', '/'):
            op_tok = self.current_token
            self.advance()
            right = self.parse_factor()
            node = BinOp(left=node, operator=op_tok.value, right=right, line=op_tok.line, col=op_tok.col)
        return node

    def parse_factor(self):
        if self.current_token.type == 'NUMBER':
            val = self.current_token.value
            line, col = self.current_token.line, self.current_token.col
            self.advance()
            return Number(value=val, line=line, col=col)
        elif self.current_token.type == 'STRING':
            val = self.current_token.value
            line, col = self.current_token.line, self.current_token.col
            self.advance()
            return StringLit(value=val, line=line, col=col)
        elif self.current_token.type == 'CHAR':
            val = self.current_token.value
            line, col = self.current_token.line, self.current_token.col
            self.advance()
            return CharLit(value=val, line=line, col=col)
        elif self.current_token.type == 'IDENTIFIER':
            name = self.current_token.value
            line, col = self.current_token.line, self.current_token.col
            self.advance()
            return Identifier(name=name, line=line, col=col)
        elif self.current_token.type == 'DELIM' and self.current_token.value == '(':
            self.advance()
            expr = self.parse_expression()
            self.match('DELIM', ')')
            return expr
            
        raise SyntaxError(f"Expected expression factor, got '{self.current_token.value}'", self.current_token.line, self.current_token.col)
