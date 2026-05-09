import re

class CodeOptimizer:
    def optimize(self, tac_lines):
        """Runs multiple optimization passes until a fixed point is reached."""
        prev = []
        curr = tac_lines.copy()
        
        while prev != curr:
            prev = curr.copy()
            curr = self.constant_folding(curr)
            curr = self.constant_propagation(curr)
            curr = self.copy_propagation(curr)
            curr = self.strength_reduction(curr)
            curr = self.common_subexpression_elimination(curr)
            curr = self.dead_code_elimination(curr)
            
        return curr

    def constant_folding(self, lines):
        optimized = []
        for line in lines:
            match = re.match(r"^(\w+)\s*=\s*(-?\d+)\s*([\+\-\*\/])\s*(-?\d+)$", line)
            if match:
                var, left, op, right = match.groups()
                left, right = int(left), int(right)
                res = 0
                if op == '+': res = left + right
                elif op == '-': res = left - right
                elif op == '*': res = left * right
                elif op == '/': res = left // right if right != 0 else 0
                optimized.append(f"{var} = {res}")
            else:
                optimized.append(line)
        return optimized

    def constant_propagation(self, lines):
        optimized = []
        constants = {} 
        for line in lines:
            if line.endswith(":"): 
                constants.clear()
                optimized.append(line)
                continue
            
            match_const = re.match(r"^(\w+)\s*=\s*(-?\d+)$", line)
            if match_const:
                constants[match_const.group(1)] = match_const.group(2)
                optimized.append(line)
                continue
                
            match_op = re.match(r"^(\w+)\s*=\s*([a-zA-Z_]\w*|-?\d+)\s*([\+\-\*\/])\s*([a-zA-Z_]\w*|-?\d+)$", line)
            if match_op:
                var, left, op, right = match_op.groups()
                new_left = constants.get(left, left)
                new_right = constants.get(right, right)
                optimized.append(f"{var} = {new_left} {op} {new_right}")
                if var in constants: del constants[var]
                continue
                
            match_assign = re.match(r"^(\w+)\s*=\s*([a-zA-Z_]\w*)$", line)
            if match_assign:
                var, val = match_assign.groups()
                if val in constants:
                    optimized.append(f"{var} = {constants[val]}")
                    constants[var] = constants[val]
                else:
                    optimized.append(line)
                    if var in constants: del constants[var]
                continue
                
            match_print = re.match(r"^print\s+([a-zA-Z_]\w*)$", line)
            if match_print:
                var = match_print.group(1)
                new_var = constants.get(var, var)
                optimized.append(f"print {new_var}")
                continue
                
            match_if = re.match(r"^if\s+([a-zA-Z_]\w*)\s+goto\s+(\w+)$", line)
            if match_if:
                var, label = match_if.groups()
                new_var = constants.get(var, var)
                optimized.append(f"if {new_var} goto {label}")
                continue
                
            optimized.append(line)
        return optimized

    def copy_propagation(self, lines):
        optimized = []
        copies = {} 
        for line in lines:
            if line.endswith(":"):
                copies.clear()
                optimized.append(line)
                continue
                
            match_assign = re.match(r"^(\w+)\s*=\s*([a-zA-Z_]\w*)$", line)
            if match_assign and match_assign.group(1) != match_assign.group(2):
                var, val = match_assign.groups()
                copies[var] = copies.get(val, val)
                optimized.append(line)
                continue
                
            match_op = re.match(r"^(\w+)\s*=\s*([a-zA-Z_]\w*|-?\d+)\s*([\+\-\*\/])\s*([a-zA-Z_]\w*|-?\d+)$", line)
            if match_op:
                var, left, op, right = match_op.groups()
                new_left = copies.get(left, left)
                new_right = copies.get(right, right)
                optimized.append(f"{var} = {new_left} {op} {new_right}")
                if var in copies: del copies[var]
                continue
                
            match_print = re.match(r"^print\s+([a-zA-Z_]\w*)$", line)
            if match_print:
                var = match_print.group(1)
                new_var = copies.get(var, var)
                optimized.append(f"print {new_var}")
                continue
                
            match_if = re.match(r"^if\s+([a-zA-Z_]\w*)\s+goto\s+(\w+)$", line)
            if match_if:
                var, label = match_if.groups()
                new_var = copies.get(var, var)
                optimized.append(f"if {new_var} goto {label}")
                continue

            optimized.append(line)
        return optimized

    def strength_reduction(self, lines):
        optimized = []
        for line in lines:
            match1 = re.match(r"^(\w+)\s*=\s*([a-zA-Z_]\w*)\s*\*\s*2$", line)
            if match1:
                optimized.append(f"{match1.group(1)} = {match1.group(2)} + {match1.group(2)}")
                continue
            match2 = re.match(r"^(\w+)\s*=\s*2\s*\*\s*([a-zA-Z_]\w*)$", line)
            if match2:
                optimized.append(f"{match2.group(1)} = {match2.group(2)} + {match2.group(2)}")
                continue
            optimized.append(line)
        return optimized

    def common_subexpression_elimination(self, lines):
        optimized = []
        expressions = {} 
        for line in lines:
            if line.endswith(":"):
                expressions.clear()
                optimized.append(line)
                continue
            
            match = re.match(r"^(\w+)\s*=\s*([a-zA-Z_]\w*|-?\d+)\s*([\+\-\*\/])\s*([a-zA-Z_]\w*|-?\d+)$", line)
            if match:
                var, left, op, right = match.groups()
                expr = f"{left} {op} {right}"
                alt_expr = f"{right} {op} {left}" if op in ['+', '*'] else expr
                
                if expr in expressions:
                    optimized.append(f"{var} = {expressions[expr]}")
                elif alt_expr in expressions:
                    optimized.append(f"{var} = {expressions[alt_expr]}")
                else:
                    expressions[expr] = var
                    optimized.append(line)
            else:
                match_assign = re.match(r"^(\w+)\s*=", line)
                if match_assign:
                    var = match_assign.group(1)
                    keys_to_del = [k for k, v in expressions.items() if v == var or var in k.split()]
                    for k in keys_to_del:
                        del expressions[k]
                optimized.append(line)
        return optimized

    def dead_code_elimination(self, lines):
        used = set()
        optimized = []
        for line in reversed(lines):
            if line.endswith(":"):
                optimized.append(line)
                continue
                
            match_print = re.match(r"^print\s+([a-zA-Z_]\w*)$", line)
            if match_print:
                used.add(match_print.group(1))
                optimized.append(line)
                continue
                
            match_if = re.match(r"^if\s+([a-zA-Z_]\w*)\s+goto\s+(\w+)$", line)
            if match_if:
                used.add(match_if.group(1))
                optimized.append(line)
                continue
                
            if line.startswith("goto "):
                optimized.append(line)
                continue
                
            match_assign = re.match(r"^(\w+)\s*=\s*(.*)$", line)
            if match_assign:
                var, expr = match_assign.groups()
                # A variable is dead if it is never used (temp variables starting with 't' are safe to kill if unused)
                # To be completely safe and generic, any variable not in 'used' set is technically dead
                # EXCEPT we might want to keep the final output variables. 
                # For compiler simplicity, if var not in used, we drop it. 
                # (Unless the user expects variables to persist, but TAC has no side effects)
                if var not in used:
                    continue
                else:
                    for part in expr.split():
                        if re.match(r"^[a-zA-Z_]\w*$", part):
                            used.add(part)
                    optimized.append(line)
                    continue
            
            optimized.append(line)
            
        return list(reversed(optimized))
