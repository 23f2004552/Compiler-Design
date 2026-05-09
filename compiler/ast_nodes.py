from dataclasses import dataclass
from typing import List, Optional, Any

@dataclass(kw_only=True)
class ASTNode:
    line: int = 0
    col: int = 0

    def to_dict(self) -> dict:
        result = {"type": self.__class__.__name__, "line": self.line, "col": self.col}
        for key, value in self.__dict__.items():
            if key in ["line", "col"]: continue
            if isinstance(value, ASTNode):
                result[key] = value.to_dict()
            elif isinstance(value, list):
                result[key] = [v.to_dict() if isinstance(v, ASTNode) else v for v in value]
            else:
                result[key] = value
        return result

@dataclass
class Program(ASTNode):
    statements: List['Statement']

@dataclass
class Statement(ASTNode):
    pass

@dataclass
class Expression(ASTNode):
    pass

@dataclass
class Assignment(Statement):
    identifier: str
    expression: Expression
    var_type: Optional[str] = None # 'int', 'float', 'char', 'string', etc. (if explicit)

@dataclass
class PrintStmt(Statement):
    expression: Expression

@dataclass
class Condition(Expression): # make it an expression to support && ||
    left: Expression
    operator: str
    right: Expression

@dataclass
class Conditional(Statement):
    condition: Expression
    if_body: List[Statement]
    else_body: Optional[List[Statement]]

@dataclass
class WhileLoop(Statement):
    condition: Expression
    body: List[Statement]

@dataclass
class Block(Statement):
    statements: List[Statement]

@dataclass
class BinOp(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class Number(Expression):
    value: float

@dataclass
class StringLit(Expression):
    value: str

@dataclass
class CharLit(Expression):
    value: str

@dataclass
class Identifier(Expression):
    name: str

@dataclass
class IntToFloat(Expression):
    expression: Expression
