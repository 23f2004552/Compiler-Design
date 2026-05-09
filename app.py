import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from compiler.lexer import tokenize
from compiler.parser import Parser
from compiler.semantics import SemanticAnalyzer
from compiler.codegen import IntermediateCodeGenerator
from compiler.errors import CompilerError

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

def build_symbol_table(tokens):
    """Build a symbol table from IDENTIFIER tokens."""
    table = {}
    idx = 1
    for t in tokens:
        if t.type == 'IDENTIFIER' and t.value not in table:
            table[t.value] = {"index": idx, "name": t.value, "type": "identifier", "line": t.line}
            idx += 1
    return list(table.values())

def format_token_stream(tokens, symbol_table):
    """Format tokens in textbook notation ⟨id,1⟩ ⟨=⟩ ⟨+⟩ etc."""
    sym_index = {entry["name"]: entry["index"] for entry in symbol_table}
    formatted = []
    for t in tokens:
        if t.type == 'IDENTIFIER':
            formatted.append({"notation": "<id,{}>".format(sym_index[t.value]), "raw": t.value, "type": t.type, "line": t.line, "col": t.col})
        elif t.type == 'NUMBER':
            formatted.append({"notation": "<{}>".format(t.value), "raw": str(t.value), "type": t.type, "line": t.line, "col": t.col})
        elif t.type == 'KEYWORD':
            formatted.append({"notation": "<{}>".format(t.value), "raw": t.value, "type": t.type, "line": t.line, "col": t.col})
        elif t.type == 'OP' or t.type == 'RELOP':
            formatted.append({"notation": "<{}>".format(t.value), "raw": t.value, "type": t.type, "line": t.line, "col": t.col})
        elif t.type == 'DELIM':
            formatted.append({"notation": "<{}>".format(t.value), "raw": t.value, "type": t.type, "line": t.line, "col": t.col})
        else:
            formatted.append({"notation": "<{}>".format(t.value), "raw": str(t.value), "type": t.type, "line": t.line, "col": t.col})
    return formatted

def ast_to_tree_lines(node, prefix="", is_last=True):
    """Convert AST dict to indented tree lines for display."""
    lines = []
    connector = "└── " if is_last else "├── "
    node_type = node.get("type", "?")

    # Build label for this node
    label = node_type
    if node_type == "Number":
        label = "Number [{}]".format(node.get("value", ""))
    elif node_type == "Identifier":
        label = "Identifier [{}]".format(node.get("name", ""))
    elif node_type == "BinOp":
        label = "BinOp [{}]".format(node.get("operator", ""))
    elif node_type == "Assignment":
        label = "Assignment [let {} =]".format(node.get("identifier", ""))
    elif node_type == "Condition":
        label = "Condition [{}]".format(node.get("operator", ""))
    elif node_type == "PrintStmt":
        label = "PrintStmt"
    elif node_type == "Then Block":
        label = "Then Block"
    elif node_type == "Else Block":
        label = "Else Block"

    lines.append(prefix + connector + label)
    child_prefix = prefix + ("    " if is_last else "│   ")

    # Collect children to render
    children = []
    
    if node_type == "Conditional":
        # Specific order for Conditional
        if "condition" in node:
            children.append(("condition", node["condition"]))
        if "if_body" in node:
            children.append(("if_body", {"type": "Then Block", "statements": node["if_body"]}))
        if "else_body" in node and node["else_body"]:
            children.append(("else_body", {"type": "Else Block", "statements": node["else_body"]}))
    elif node_type in ["Then Block", "Else Block"]:
        # List statements inside these virtual blocks
        for i, stmt in enumerate(node.get("statements", [])):
            children.append(("stmt", stmt))
    else:
        # Generic handling for other nodes
        for key, val in node.items():
            if key == "type":
                continue
            if isinstance(val, dict) and "type" in val:
                children.append((key, val))
            elif isinstance(val, list):
                for i, item in enumerate(val):
                    if isinstance(item, dict) and "type" in item:
                        children.append(("{}.{}".format(key, i), item))

    for i, (key, child) in enumerate(children):
        is_child_last = (i == len(children) - 1)
        lines += ast_to_tree_lines(child, child_prefix, is_child_last)

    return lines

@app.route('/api/compile', methods=['POST'])
def compile_code():
    data = request.get_json()
    if not data or 'source' not in data:
        return jsonify({"success": False, "error": "No source code provided"}), 400

    source = data['source']
    response = {
        "success": True,
        "tokens": [],
        "token_stream": "",
        "ast": None,
        "ast_tree": [],
        "intermediate_code": [],
        "symbol_table": [],
        "errors": [],
        "semantics": "Pending"
    }

    try:
        # Phase 1: Lexical Analysis
        tokens = tokenize(source)
        response["tokens"] = [t.to_dict() for t in tokens]

        # Build Symbol Table
        symbol_table = build_symbol_table(tokens)
        response["symbol_table"] = symbol_table

        # Format token stream in textbook notation
        formatted = format_token_stream(tokens, symbol_table)
        response["tokens"] = formatted
        
        # Group tokens by line for visualization
        line_map = {}
        for f in formatted:
            l_num = f["line"]
            if l_num not in line_map:
                line_map[l_num] = []
            line_map[l_num].append(f["notation"])
        
        token_stream_lines = []
        for l_num in sorted(line_map.keys()):
            token_stream_lines.append("  ".join(line_map[l_num]))
            
        response["token_stream"] = "\n".join(token_stream_lines)

        # Phase 2: Syntax Analysis
        parser = Parser(tokens)
        ast = parser.parse()
        response["ast"] = ast.to_dict()

        # Convert AST to tree lines
        ast_dict = ast.to_dict()
        tree_lines = ["Program"]
        stmts = ast_dict.get("statements", [])
        for i, stmt in enumerate(stmts):
            is_last = (i == len(stmts) - 1)
            tree_lines += ast_to_tree_lines(stmt, "", is_last)
        response["ast_tree"] = tree_lines

        # Phase 3: Semantic Analysis
        semantics = SemanticAnalyzer()
        semantics.analyze(ast)
        response["semantics"] = "All clear! No scope or declaration issues found."

        # Phase 4: Intermediate Code Generation
        codegen = IntermediateCodeGenerator()
        intermediate_code = codegen.generate(ast)
        response["intermediate_code"] = intermediate_code

    except CompilerError as e:
        response["success"] = False
        response["errors"].append({
            "phase": e.phase,
            "message": e.message,
            "line": e.line,
            "col": e.col
        })
    except Exception as e:
        response["success"] = False
        response["errors"].append({
            "phase": "Internal",
            "message": str(e),
            "line": 0,
            "col": 0
        })

    return jsonify(response)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
