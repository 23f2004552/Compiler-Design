import re

class TargetCodeGenerator:
    def generate(self, tac_lines):
        """
        Converts TAC into simple x86-like Assembly instructions.
        """
        machine_code = []
        float_vars = set()
        
        reg_map = {}
        next_reg = 1
        
        def get_reg(var):
            nonlocal next_reg
            if re.match(r"^[a-zA-Z_]\w*$", var):
                if var not in reg_map:
                    reg_map[var] = f"R{next_reg}"
                    next_reg += 1
                return reg_map[var]
            return var
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
                r_res, r_val = get_reg(res), get_reg(val)
                machine_code.append(f"LDF R0, {r_val}")
                machine_code.append(f"STF {r_res}, R0")
                continue
                
            # Binary operation: res = a op b
            match = re.match(r"^(\w+)\s*=\s*(.*?)\s+([\+\-\*\/]|==|!=|<=|>=|<|>|&&|\|\|)\s+(.*)$", line)
            if match:
                res, left, op, right = match.groups()
                is_float = (left in float_vars or right in float_vars or '.' in left or '.' in right)
                r_res, r_left, r_right = get_reg(res), get_reg(left), get_reg(right)
                
                if op in ('+', '-', '*', '/'):
                    if is_float:
                        float_vars.add(res)
                        machine_code.append(f"LDF R0, {r_left}")
                        if op == '+': machine_code.append(f"ADDF R0, R0, {r_right}")
                        elif op == '-': machine_code.append(f"SUBF R0, R0, {r_right}")
                        elif op == '*': machine_code.append(f"MULF R0, R0, {r_right}")
                        elif op == '/': machine_code.append(f"DIVF R0, R0, {r_right}")
                        machine_code.append(f"STF {r_res}, R0")
                    else:
                        machine_code.append(f"MOV AX, {r_left}")
                        if op == '+': machine_code.append(f"ADD AX, {r_right}")
                        elif op == '-': machine_code.append(f"SUB AX, {r_right}")
                        elif op == '*': machine_code.append(f"MUL AX, {r_right}")
                        elif op == '/': machine_code.append(f"DIV {r_right}")
                        machine_code.append(f"MOV {r_res}, AX")
                else:
                    # Relational or logical operator mock
                    machine_code.append(f"CMP {r_left}, {r_right}")
                    if op == '==': machine_code.append(f"SETE {r_res}")
                    elif op == '!=': machine_code.append(f"SETNE {r_res}")
                    elif op == '<': machine_code.append(f"SETL {r_res}")
                    elif op == '>': machine_code.append(f"SETG {r_res}")
                    elif op == '<=': machine_code.append(f"SETLE {r_res}")
                    elif op == '>=': machine_code.append(f"SETGE {r_res}")
                    elif op == '&&': machine_code.append(f"AND {r_res}, {r_left}, {r_right}")
                    elif op == '||': machine_code.append(f"OR {r_res}, {r_left}, {r_right}")
                continue
                
            # Simple assignment: res = a
            match = re.match(r"^(\w+)\s*=\s*(.*)$", line)
            if match:
                res, val = match.groups()
                r_res, r_val = get_reg(res), get_reg(val)
                if val in float_vars or '.' in val:
                    float_vars.add(res)
                    machine_code.append(f"LDF R0, {r_val}")
                    machine_code.append(f"STF {r_res}, R0")
                else:
                    machine_code.append(f"MOV {r_res}, {r_val}")
                continue
                
            # Print statement
            match = re.match(r"^print\s+(.*)$", line)
            if match:
                r_var = get_reg(match.group(1))
                machine_code.append(f"PRINT {r_var}")
                continue
                
            # Unknown line, keep as is
            machine_code.append(f"; Unrecognized: {line}")
            
        machine_code.append("HALT")
        return machine_code
