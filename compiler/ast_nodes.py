from dataclasses import dataclass
from typing import List, Optional, Any

@dataclass
class ASTNode:
    def to_dict(self) -> dict:
        result = {"type": self.__class__.__name__}
        for key, value in self.__dict__.items():
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

@dataclass
class PrintStmt(Statement):
    expression: Expression

@dataclass
class Condition(ASTNode):
    left: Expression
    operator: str
    right: Expression

@dataclass
class Conditional(Statement):
    condition: Condition
    if_body: List[Statement]
    else_body: Optional[List[Statement]]

@dataclass
class BinOp(Expression):
    left: Expression
    operator: str
    right: Expression

@dataclass
class Number(Expression):
    value: float

@dataclass
class Identifier(Expression):
    name: str
