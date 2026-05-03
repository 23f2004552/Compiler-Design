import pytest
from compiler.lexer import tokenize, Token
from compiler.parser import Parser
from compiler.codegen import TACGenerator
from compiler.errors import LexicalError, SyntaxError

def test_lexer_valid():
    source = "let x = 5 + 3;"
    tokens = tokenize(source)
    assert len(tokens) == 7 # let, x, =, 5, +, 3, ;
    assert tokens[0].type == 'KEYWORD' and tokens[0].value == 'let'
    assert tokens[1].type == 'IDENTIFIER' and tokens[1].value == 'x'
    assert tokens[2].type == 'OP' and tokens[2].value == '='
    assert tokens[3].type == 'NUMBER' and tokens[3].value == 5
    assert tokens[4].type == 'OP' and tokens[4].value == '+'
    assert tokens[5].type == 'NUMBER' and tokens[5].value == 3
    assert tokens[6].type == 'DELIM' and tokens[6].value == ';'

def test_lexer_invalid():
    source = "let x@ = 5;"
    with pytest.raises(LexicalError) as excinfo:
        tokenize(source)
    assert "Unexpected character: '@'" in str(excinfo.value)

def test_parser_valid():
    source = "let x = 5 + 3;"
    tokens = tokenize(source)
    parser = Parser(tokens)
    ast = parser.parse()
    assert len(ast.statements) == 1
    assert ast.statements[0].identifier == 'x'

def test_parser_invalid():
    source = "let x = 5"
    tokens = tokenize(source)
    parser = Parser(tokens)
    with pytest.raises(SyntaxError) as excinfo:
        parser.parse()
    assert "Expected 'DELIM', got 'None'" in str(excinfo.value) or "Expected DELIM ';'" in str(excinfo.value)

def test_codegen():
    source = "let x = 5 + 3;"
    tokens = tokenize(source)
    parser = Parser(tokens)
    ast = parser.parse()
    codegen = TACGenerator()
    tac = codegen.generate(ast)
    assert len(tac) == 2
    assert tac[0].startswith("t1 = 5 + 3")
    assert tac[1] == "x = t1"
