import re

class TargetCodeGenerator:
    def generate(self, tac_lines):
        """
        Converts TAC into simple x86-like Assembly instructions.
        """
        machine_code = []
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
                
            # Binary operation: res = a op b
            match = re.match(r"^(\w+)\s*=\s*(.*?)\s+([\+\-\*\/])\s+(.*)$", line)
            if match:
                res, left, op, right = match.groups()
                machine_code.append(f"MOV AX, {left}")
                if op == '+':
                    machine_code.append(f"ADD AX, {right}")
                elif op == '-':
                    machine_code.append(f"SUB AX, {right}")
                elif op == '*':
                    machine_code.append(f"MUL AX, {right}")
                elif op == '/':
                    machine_code.append(f"DIV {right}") # Simplified
                machine_code.append(f"MOV {res}, AX")
                continue
                
            # Simple assignment: res = a
            match = re.match(r"^(\w+)\s*=\s*(.*)$", line)
            if match:
                res, val = match.groups()
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
