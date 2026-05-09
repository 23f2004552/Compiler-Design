import re

class TargetCodeGenerator:
    def generate(self, tac_lines):
        """
        Converts TAC into simple x86-like Assembly instructions.
        """
        machine_code = []
        float_vars = set()
        for line in tac_lines:
            # Label
            if line.endswith(":"):
                machine_code.append(line)
                continue
            
            # Unconditional jump: goto L1
            match = re.match(r"^goto\s+(\w+)$", line)
            if match:
                machine_code.append(f"JMP {match.group(1)}")
                continue
                
            # Conditional jump: if cond goto L1
            match = re.match(r"^if\s+(.*?)\s+goto\s+(\w+)$", line)
            if match:
                cond, label = match.groups()
                machine_code.append(f"CMP {cond}, 0")
                machine_code.append(f"JNE {label}")
                continue
                
            # Int to Float Cast
            match = re.match(r"^(\w+)\s*=\s*inttofloat\((.*)\)$", line)
            if match:
                res, val = match.groups()
                float_vars.add(res)
                machine_code.append(f"LDF R2, {val}")
                machine_code.append(f"STF {res}, R2")
                continue
                
            # Binary operation: res = a op b
            match = re.match(r"^(\w+)\s*=\s*(.*?)\s+([\+\-\*\/]|==|!=|<=|>=|<|>|&&|\|\|)\s+(.*)$", line)
            if match:
                res, left, op, right = match.groups()
                is_float = (left in float_vars or right in float_vars or '.' in left or '.' in right)
                
                if op in ('+', '-', '*', '/'):
                    if is_float:
                        float_vars.add(res)
                        machine_code.append(f"LDF R2, {left}")
                        if op == '+': machine_code.append(f"ADDF R2, R2, {right}")
                        elif op == '-': machine_code.append(f"SUBF R2, R2, {right}")
                        elif op == '*': machine_code.append(f"MULF R2, R2, {right}")
                        elif op == '/': machine_code.append(f"DIVF R2, R2, {right}")
                        machine_code.append(f"STF {res}, R2")
                    else:
                        machine_code.append(f"MOV AX, {left}")
                        if op == '+': machine_code.append(f"ADD AX, {right}")
                        elif op == '-': machine_code.append(f"SUB AX, {right}")
                        elif op == '*': machine_code.append(f"MUL AX, {right}")
                        elif op == '/': machine_code.append(f"DIV {right}")
                        machine_code.append(f"MOV {res}, AX")
                else:
                    # Relational or logical operator mock
                    machine_code.append(f"CMP {left}, {right}")
                    if op == '==': machine_code.append(f"SETE {res}")
                    elif op == '!=': machine_code.append(f"SETNE {res}")
                    elif op == '<': machine_code.append(f"SETL {res}")
                    elif op == '>': machine_code.append(f"SETG {res}")
                    elif op == '<=': machine_code.append(f"SETLE {res}")
                    elif op == '>=': machine_code.append(f"SETGE {res}")
                    elif op == '&&': machine_code.append(f"AND {res}, {left}, {right}")
                    elif op == '||': machine_code.append(f"OR {res}, {left}, {right}")
                continue
                
            # Simple assignment: res = a
            match = re.match(r"^(\w+)\s*=\s*(.*)$", line)
            if match:
                res, val = match.groups()
                if val in float_vars or '.' in val:
                    float_vars.add(res)
                    machine_code.append(f"LDF R2, {val}")
                    machine_code.append(f"STF {res}, R2")
                else:
                    machine_code.append(f"MOV {res}, {val}")
                continue
                
            # Print statement
            match = re.match(r"^print\s+(.*)$", line)
            if match:
                machine_code.append(f"PUSH {match.group(1)}")
                machine_code.append(f"CALL print_sys")
                continue
                
            # Unknown line, keep as is
            machine_code.append(f"; Unrecognized: {line}")
            
        return machine_code
