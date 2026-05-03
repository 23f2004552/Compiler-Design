from .errors import SyntaxError
from .ast_nodes import (
    Program, Assignment, Conditional, PrintStmt, 
    BinOp, Number, Identifier, Condition
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
            if self.current_token.value == 'let':
                return self.parse_assignment()
            elif self.current_token.value == 'if':
                return self.parse_conditional()
            elif self.current_token.value == 'print':
                return self.parse_print()
        raise SyntaxError(f"Expected statement (let, if, print), got '{self.current_token.value}'", self.current_token.line, self.current_token.col)

    def parse_assignment(self):
        let_tok = self.match('KEYWORD', 'let')
        ident_tok = self.match('IDENTIFIER')
        self.match('OP', '=')
        expr = self.parse_expression()
        self.match('DELIM', ';')
        return Assignment(identifier=ident_tok.value, expression=expr, line=let_tok.line, col=let_tok.col)

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
        cond = self.parse_condition()
        self.match('DELIM', ')')
        self.match('DELIM', '{')
        
        if_body = []
        while self.current_token and not (self.current_token.type == 'DELIM' and self.current_token.value == '}'):
            if_body.append(self.parse_statement())
            
        self.match('DELIM', '}')
        
        else_body = None
        if self.current_token and self.current_token.type == 'KEYWORD' and self.current_token.value == 'else':
            self.match('KEYWORD', 'else')
            self.match('DELIM', '{')
            else_body = []
            while self.current_token and not (self.current_token.type == 'DELIM' and self.current_token.value == '}'):
                else_body.append(self.parse_statement())
            self.match('DELIM', '}')
            
        self.match('KEYWORD', 'end')
        
        return Conditional(condition=cond, if_body=if_body, else_body=else_body, line=if_tok.line, col=if_tok.col)

    def parse_condition(self):
        left = self.parse_expression()
        line, col = left.line, left.col
        op_tok = self.match('RELOP')
        right = self.parse_expression()
        return Condition(left=left, operator=op_tok.value, right=right, line=line, col=col)

    def parse_expression(self):
        node = self.parse_term()
        while self.current_token and self.current_token.type == 'OP' and self.current_token.value in ('+', '-'):
            op_tok = self.current_token
            self.advance()
            right = self.parse_term()
            node = BinOp(left=node, operator=op_tok.value, right=right, line=op_tok.line, col=op_tok.col)
        return node

    def parse_term(self):
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
            
        raise SyntaxError(f"Expected factor (number, identifier, '('), got '{self.current_token.value}'", self.current_token.line, self.current_token.col)
