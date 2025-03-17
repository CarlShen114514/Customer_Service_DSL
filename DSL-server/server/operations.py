import sys
import os
current_path = os.path.split(os.path.realpath(__file__))[0]
print(current_path)
from server.exceptions import *

class CurrentState():
    """
    用于记录当前状态的类，每个DFA都拥有一个实例作为自身属性
    """
    def __init__(self):
        self.state = 'main'
        self.var_table: dict[str,dict] = {}
        self.operation_index = 0
        self.is_running = True
        self.all_states = []

class Operation():
    """
    所有操作类的父类
    """
    def __init__(self):
        pass

class Response_operation(Operation):
    """
    回复操作语句，用于向用户返回当前状态下的提示信息
    """    
    def __init__(self, phrases: list[str], c: CurrentState):
        self.phrases = phrases
        for phrase in self.phrases:
            if phrase.startswith("$") and phrase.endswith("$"):
                if phrase not in c.var_table:
                    raise GrammarException("Inexplicit variable:", phrase)

    def exec(self, c: CurrentState):
        self.output = ''
        for phrase in self.phrases:
            if phrase.startswith("$") and phrase.endswith("$"):
                if c.var_table[phrase]["type"] == "FLOAT":
                    self.output += str("{:.2f}".format(c.var_table[phrase]["value"]))
                else:
                    self.output += str(c.var_table[phrase]["value"])
            else:
                self.output += phrase
        return [self.output]
    
class Goto_operation(Operation):
    """
    转移操作语句，用于实施状态的转移以及标记DFA的运作状态
    """
    def __init__(self, next_state: str, c: CurrentState):
        if next_state not in c.all_states + ["EXIT"]:
            raise GrammarException("Undefiend state:", next_state)
        else:
            self.next = next_state

    def exec(self, c:CurrentState):
        if self.next != "EXIT":
            c.state = self.next
            c.operation_index = 0
        else:
            c.is_running = False

class Default_operation(Operation):
    """
    默认操作语句，每一个STATE语句下的默认操作
    """
    def __init__(self, ops: list, c: CurrentState):
        self.operations: list[Operation] = []
        for op in ops:
            if op[0] == "RESPONSE":
                self.operations.append(Response_operation(op[1:], c))
            elif op[0] == "ASSIGN":
                self.operations.append(Var_assignment(op[1:], c))
            elif op[0] == "GOTO":
                self.operations.append(Goto_operation(op[1], c))

    def exec(self, c: CurrentState):
        response = []
        for op in self.operations:
            if isinstance(op, Response_operation):
                response.extend(op.exec(c))
            elif isinstance(op, Var_assignment):
                op.exec(c)
            elif isinstance(op,Goto_operation):
                op.exec(c)
                return response
        return response


class Var_assignment(Operation):
    """
    赋值操作语句，用于对变量赋值
    """
    def __init__(self, info: list, c: CurrentState):
        self.var_type = info[0]
        self.var_id = info[1]
        self.expr = info[2]
        if self.var_id not in c.var_table:
            raise GrammarException("Undefined variable.", info[1])
        if self.var_type != c.var_table[self.var_id]["type"]:
            raise TypeException("Conflicted variable type:", f"{self.var_type} and {c.var_table[self.var_id]["type"]}")
        if self.var_type != "STR" and isinstance(self.expr, str):
            raise TypeException("Conflicted variable type:", f"{self.var_type} and {c.var_table[self.var_id]["type"]}")
    
    def evaluate_parsed_expression(self, parsed_expr, c: CurrentState):
        """
        计算表达式在当前状态的值
        """
        if isinstance(parsed_expr, list):
            # 如果解析结果是一个列表则递归处理
            if len(parsed_expr) == 1:
                return self.evaluate_parsed_expression(parsed_expr[0], c)
            elif len(parsed_expr) == 2 and parsed_expr[0] in ('+', '-'):
                # 处理一元操作符
                op = parsed_expr[0]
                operand = self.evaluate_parsed_expression(parsed_expr[1], c)
                if op == '+':
                    return +operand
                elif op == '-':
                    return -operand
            else:
                # 处理二元操作符
                left = self.evaluate_parsed_expression(parsed_expr[0], c)
                idx = 1
                while idx < len(parsed_expr):
                    op = parsed_expr[idx]
                    right = self.evaluate_parsed_expression(parsed_expr[idx + 1], c)
                    if op == '+':
                        left += right
                    elif op == '-':
                        left -= right
                    elif op == '*':
                        left *= right
                    elif op == '/':
                        left /= right
                    idx += 2
                return left
        else:
            # 处理操作数
            if isinstance(parsed_expr, str):
                if parsed_expr.startswith('$') and parsed_expr.endswith('$'):
                    # 变量，查找变量表
                    var_name = parsed_expr
                    if var_name in c.var_table:
                        return c.var_table[var_name]['value']
                    else:
                        raise GrammarException(f"Undefined variable:", var_name)
                else:
                    # 数字字符串，转换为数字
                    if '.' in parsed_expr or 'e' in parsed_expr or 'E' in parsed_expr:
                        return float(parsed_expr)
                    else:
                        return int(parsed_expr)
            else:
                # 数字，直接返回
                return parsed_expr
        

    def exec(self, c: CurrentState):
        if self.var_type == "STR":
            c.var_table[self.var_id]["value"] = self.expr
            return
        expr_value = self.evaluate_parsed_expression(self.expr, c)
        if self.var_type == "INT":
            c.var_table[self.var_id]["value"] = int(expr_value)
        elif self.var_type == "FLOAT":
            c.var_table[self.var_id]["value"] = float(expr_value)

class Exit_operation(Operation):
    """
    退出操作语句，用于DFA结束运行时执行的操作
    """
    def __init__(self, ops: list, c:CurrentState):
        self.operations: list[Operation] = []

        for op in ops:
            if op[0] == "RESPONSE":
                self.operations.append(Response_operation(op[1:], c))
    
    def exec(self, c:CurrentState):
        response = []
        for op in self.operations:
            if isinstance(op, Response_operation):
                response.extend(op.exec(c))
        return response

class Match_operation(Operation):
    """
    匹配操作语句，用于判断用户输入是否与pattern相同。
    """
    def __init__(self, pattern: str, ops: list, c: CurrentState):
        self.pattern = pattern
        self.operations: list[Operation] = []
        for op in ops:
            if op[0] == "RESPONSE":
                self.operations.append(Response_operation(op[1:], c))
            elif op[0] == "ASSIGN":
                self.operations.append(Var_assignment(op[1:], c))
                pass
            elif op[0] == "GOTO":
                self.operations.append(Goto_operation(op[1], c))

    def exec(self, c: CurrentState, input: str):
        if input == self.pattern:
            response = []
            for op in self.operations:
                if isinstance(op, Response_operation):
                    response.extend(op.exec(c))
                elif isinstance(op, Var_assignment):
                    op.exec(c)
                elif isinstance(op,Goto_operation):
                    op.exec(c)
                    return response
            return response
        else: 
            return None

