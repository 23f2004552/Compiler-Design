# MiniLang Compiler Studio

MiniLang Compiler Studio is an interactive, web-based compiler for a toy programming language, complete with lexical analysis, syntax parsing, and intermediate code generation.

## Language Specification (MiniLang)
- **Keywords**: `let`, `if`, `else`, `print`, `end`
- **Delimiters**: `(`, `)`, `{`, `}`, `;`
- **Operators**: `+`, `-`, `*`, `/`, `=`, `==`, `!=`, `<`, `>`, `<=`, `>=`

## Features
- Complete Lexer and Parser (Recursive Descent)
- AST Generation
- Intermediate Code Generation
- Precise Error Reporting with line/col tracking
- Beautiful, Modern UI

## Setup & Run Locally
1. `pip install -r requirements.txt`
2. `python app.py`
3. Visit `http://localhost:5000`

## Architecture
Lexer -> Parser (AST) -> Intermediate Code Generator -> JSON -> Frontend UI

## Deploy
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
