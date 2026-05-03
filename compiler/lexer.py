import re
from .errors import LexicalError

class Token:
    def __init__(self, type, value, line, col):
        self.type = type
        self.value = value
        self.line = line
        self.col = col
        
    def to_dict(self):
        return {
            "type": self.type,
            "value": self.value,
            "line": self.line,
            "col": self.col
        }
        
    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}, {self.col})"

KEYWORDS = {'let', 'if', 'else', 'print', 'end'}
REL_OPS = {'==', '!=', '<=', '>=', '<', '>'}
OPS = {'+', '-', '*', '/', '='}
DELIMS = {'(', ')', '{', '}', ';'}

def tokenize(source_code):
    tokens = []
    line = 1
    col = 1
    i = 0
    n = len(source_code)
    
    while i < n:
        char = source_code[i]
        
        if char in ' \t\r':
            if char == '\t':
                col += 4
            else:
                col += 1
            i += 1
            continue
            
        if char == '\n':
            line += 1
            col = 1
            i += 1
            continue
            
        if char == '/' and i + 1 < n and source_code[i+1] == '/':
            while i < n and source_code[i] != '\n':
                i += 1
            continue

        if i + 1 < n and source_code[i:i+2] in REL_OPS:
            tokens.append(Token('RELOP', source_code[i:i+2], line, col))
            i += 2
            col += 2
            continue
            
        if char in REL_OPS:
            tokens.append(Token('RELOP', char, line, col))
            i += 1
            col += 1
            continue
            
        if char in OPS:
            tokens.append(Token('OP', char, line, col))
            i += 1
            col += 1
            continue
            
        if char in DELIMS:
            tokens.append(Token('DELIM', char, line, col))
            i += 1
            col += 1
            continue
            
        if char.isdigit() or (char == '.' and i + 1 < n and source_code[i+1].isdigit()):
            start_i = i
            start_col = col
            has_dot = False
            while i < n and (source_code[i].isdigit() or source_code[i] == '.'):
                if source_code[i] == '.':
                    if has_dot:
                        break
                    has_dot = True
                i += 1
                col += 1
            val_str = source_code[start_i:i]
            val = float(val_str) if has_dot else int(val_str)
            tokens.append(Token('NUMBER', val, line, start_col))
            continue
            
        if char.isalpha() or char == '_':
            start_i = i
            start_col = col
            while i < n and (source_code[i].isalnum() or source_code[i] == '_'):
                i += 1
                col += 1
            val_str = source_code[start_i:i]
            if val_str in KEYWORDS:
                tokens.append(Token('KEYWORD', val_str, line, start_col))
            else:
                tokens.append(Token('IDENTIFIER', val_str, line, start_col))
            continue
            
        raise LexicalError(f"Unexpected character: '{char}'", line, col)
        
    return tokens
