class CompilerError(Exception):
    def __init__(self, phase, message, line, col):
        self.phase = phase
        self.message = message
        self.line = line
        self.col = col
        super().__init__(f"{phase} Error at {line}:{col} - {message}")

class LexicalError(CompilerError):
    def __init__(self, message, line, col):
        super().__init__("Lexical", message, line, col)

class SyntaxError(CompilerError):
    def __init__(self, message, line, col):
        super().__init__("Syntax", message, line, col)
