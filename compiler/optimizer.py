import re

class CodeOptimizer:
    def optimize(self, tac_lines):
        """
        Performs basic constant folding on Intermediate Code.
        e.g., "t1 = 5 + 3" becomes "t1 = 8"
        """
        optimized = []
        for line in tac_lines:
            # Match pattern: var = num1 op num2
            match = re.match(r"^(\w+)\s*=\s*(\d+)\s*([\+\-\*\/])\s*(\d+)$", line)
            if match:
                var, left, op, right = match.groups()
                left = int(left)
                right = int(right)
                res = 0
                if op == '+': res = left + right
                elif op == '-': res = left - right
                elif op == '*': res = left * right
                elif op == '/': res = left // right if right != 0 else 0
                optimized.append(f"{var} = {res}")
            else:
                optimized.append(line)
        return optimized
