import os
#os.chdir("/home/carl/DSL-server")
import sys
sys.path.append('/home/carl/DSL-server')

from server.exceptions import *
from pyparsing import ParseException
from server.DSL_parser import parser
from server.operations import Operation, Exit_operation, Default_operation, Response_operation, Var_assignment, Match_operation, Goto_operation, CurrentState

class DFA():
    """
    用于描述客服机器人对话逻辑的有限状态自动机
    """
    def __init__(self, file: str):
        
        self.states: list[str] = [] #用于标记DFA的所有状态
        self.state_operations: dict[str, list] = {} #用于记录对应状态下的一系列操作序列
        self.current = CurrentState()
        # 使用parser解析DSL脚本并获取语法树
        try:
            grammar_tree = parser.parse_script(file)
        except ParseException as err:
            raise GrammarException(err.__str__(), [err.line])
        
        
        for definition in grammar_tree:
            # 处理版本信息
            if definition[0] == "VERSION":
                #TODO
                #此功能是为了后续版本更新设计，使用VERSION字段来实现后续版本的向下兼容
                pass

            # 向变量表添加变量定义
            elif definition[0] == "VAR":
                var_type = definition[1]
                var_name = definition[2]
                var_value = definition[3]
                self.current.var_table[var_name] = {"type": var_type, "value": var_value}

            #添加状态
            elif definition[0] == "STATE":
                # 检查状态定义是否重复
                if definition[1] not in self.states:
                    self.states.append(definition[1])
                    self.state_operations[definition[1]] = []
                elif definition[1] == "EXIT":
                    raise GrammarException("Invalid state id: ", definition[1])
                else:
                    raise GrammarException("Inplicit state definition: ", definition[1])
            elif definition[0] == "EXIT":
                self.exit = Exit_operation(definition[1:], self.current)
        
        self.current.all_states = self.states

        # 检状态数量以及main状态是否存在
        if len(self.states) == 0 or self.states[0] != "main":
                raise GrammarException('Expecting main state at the beginning.',[])

        # 将每一个STATE定义下的操作转化为对应的Operation实例并添加到state_operations字典中
        for definition in grammar_tree:
            if definition[0] == "STATE":
                state_id = definition[1]
                for operation in definition[2:]:
                    if operation[0] == "RESPONSE":
                        self.state_operations[state_id].append(Response_operation(operation[1:], self.current))
                    elif operation[0] == "MATCH":
                        self.state_operations[state_id].append(Match_operation(operation[1], operation[2:], self.current))
                    elif operation[0] == "DEFAULT":
                        self.state_operations[state_id].append(Default_operation(operation[1:], self.current))
        
    def get_state_hint(self):
        """
        获取当前STATE的提示信息（也就是执行MATCH语句前的所有操作），等待用户输入
        """
        response = []
        while (self.current.operation_index == 0):
            cur_state = self.current.state
            for op in self.state_operations[cur_state]:
                if not isinstance(op, Match_operation):
                    result = op.exec(self.current)
                    if result is not None:
                        response.extend(result)
                    if not isinstance(op, Default_operation):
                        self.current.operation_index += 1
                    #print(self.current.state, self.current.operation_index)
                else:
                    return response
        return response


    def state_transition(self, input: str):
        """
        将用户信息提供给DFA，从而使DFA状态发生转移，并返回DFA的输出内容
        """
        cur_state = self.current.state
        response = []
        for operation in self.state_operations[cur_state][self.current.operation_index:]:
            if isinstance(operation, Response_operation):
                response.extend(operation.exec(self.current))
                self.current.operation_index += 1
            elif isinstance(operation, Match_operation):
                result = operation.exec(self.current, input)
                if self.current.operation_index != 0:
                    self.current.operation_index += 1
                if result is not None:
                    response.extend(result)
                    #print("MATCHED:", input)
                    break
            elif isinstance(operation, Default_operation):
                result = operation.exec(self.current)
                if result is not None:
                    response.extend(result)
            #print(self.current.state, self.current.operation_index)
        response.extend(self.get_state_hint())
        return response
                
if __name__ == '__main__':
    a = DFA("scripts/script3.txt")
    hello = a.get_state_hint()
    for r in hello:
        print(f"Agent:{r}")
    while(1):
        msg = input("User:")
        if msg == "status":
            print(a.current.state)
            continue
        if msg == "index":
            print(a.current.operation_index)
            continue
        print(a.current.state, a.current.operation_index)
        responses = a.state_transition(msg)
        
        if not a.current.is_running:
            exit_msg = a.exit.exec(a.current)
            for bye in exit_msg:
                print(f"Agent:{bye}")
            break
        for r in responses:
            print(f"Agent:{r}")