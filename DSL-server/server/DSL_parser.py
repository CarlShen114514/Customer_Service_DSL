from pyparsing import *
import os

"""
实现了一个DSL语法的解析器，将用户输入的文件转化为符合以下文法的语法树
DSL语法的EBNF范式：
<DSL_language>  	::= <version_info> {<state_definition> | <var_definition>} <exit_operation>
<version_info>		::= "VERSION" <digit>+ "." <digit>+ "." <digit>+
<digit>				::= "0" | "1" | ... | "9"
<state_definition> 	::= "STATE" <state_id> {<response> ｜ <match_clause>} <default_clause>
<state_id>			::= <letter>+
<letter> 			::= "A" | "B" | ..."Z" | "a" | "b" | ... | "z"
<response>			::= "RESPONSE" (<string> | <var_id>) {"+" (<string> | <var_id>)}
<match_clause>		::= "MATCH" <string> {<response> | <var_assignment>} <goto_clause>
<default_clause>	::= "DEFAULT" {<response> | <var_assignment>} <goto_clause>
<string>			::= " (<letter> | <digit>)+ "
<integer>			::= ["+" | "-"] <digit>+
<float>				::= ["+" | "-"] <digit>+ "." <digit>+
<goto_clause>		::= "GOTO" (<state_id> | "EXIT")
<var_definition>	::= "VAR" ("INT" <var_id> <integer>) | ("FLOAT" <var_id> <float>) | ("STR" <var_id> <string>)
<var_id>			::= "$" (<letter> | <digit>)+ "$" 
<var_assignment>	::= "ASSIGN" ("INT" <var_id> <expr>) | ("FLOAT" <var_id> <expr>) | ("STR" <var_id> <string>)
<expr>				::= <term> { ("+" | "-") <term>}
<term>       		::= <factor> { ("*" | "/") <factor> }
<factor>     		::= <number> | "(" <expr> ")"
<number>			::= <integer> | <float> ｜ <var_id>
<exit_operation>	::= "EXIT" {<response>}
"""


class parser:
    _string = quoted_string('"').setParseAction(removeQuotes) #字符串
    _integer = Regex(r'[+-]?[0-9]+').set_parse_action(lambda tokens: int(tokens[0])) #整型常量
    _float = Regex(r'[+-]?[0-9]+.[0-9]+').set_parse_action(lambda tokens: float(tokens[0])) #浮点型常量
    _var_id = Combine('$' + Regex('[0-9A-Za-z_]+') + '$') #变量标识符
    _state_id = Word(alphas) #状态标识符
    _version_info = Group(Keyword("VERSION") + Regex(r'[0-9]+.[0-9]+.[0-9]+')) #状态信息子句
    _goto_clause = Group(Keyword("GOTO") + (_state_id ^ Keyword("EXIT"))) #goto语句
    _response = Group(Keyword("RESPONSE") + (_string ^ _var_id) + ZeroOrMore(Suppress('+') + (_string ^ _var_id))) #回复语句

    """
    以下六行是有关表达式的定义
    """
    _operand = _integer | _var_id | _float #操作数
    plus, minus, mult, div = map(oneOf, "+ - * /".split())
    _expr = Forward() #表达式
    _factor = Group(_operand | ('(' + _expr + ')')) #因子
    _term = Group(_factor + ZeroOrMore((mult | div) + _factor)) #项
    _expr <<= Group(_term + ZeroOrMore((plus | minus) + _term)) #表达式的递归定义

    
    _var_definition = Group(Keyword("VAR") + ((Keyword("INT") + _var_id + _integer) ^ 
                                              (Keyword("FLOAT") + _var_id + _float) ^ 
                                              (Keyword("STR") + _var_id + _string))) #变量定义语句
    _var_assignment = Group(Keyword("ASSIGN") + ((Keyword("INT") + _var_id + _expr) ^ 
                                              (Keyword("FLOAT") + _var_id + _expr) ^ 
                                              (Keyword("STR") + _var_id + _string))) #变量赋值语句
    
    _match_clause = Group(Keyword("MATCH") + _string + ZeroOrMore(_response ^ _var_assignment) + _goto_clause) #匹配语句
    _default_clause = Group(Keyword("DEFAULT") + ZeroOrMore(_response ^ _var_assignment) + _goto_clause) #默认语句
    _state_definition = Group(Keyword("STATE") + _state_id + _response + ZeroOrMore(_response ^ _match_clause) + _default_clause) # 状态定义语句

    _exit_operation = Group(Keyword("EXIT") + ZeroOrMore(_response)) #退出操作语句
    _DSL_language = _version_info + ZeroOrMore(_var_definition ^ _state_definition) + _exit_operation #DSL语言定义

    @staticmethod
    def parse_script(file: str):
        """
        解析给定的文件
        """
        return parser._DSL_language.parse_file(file, parse_all=True).as_list()
    
    @staticmethod
    def print_tree(tree, indent="", last=True):
        """
        递归打印嵌套列表结构的语法树。
        """
        if isinstance(tree, list):
            for i, item in enumerate(tree):
                is_last = (i == len(tree) - 1)
                if isinstance(item, list):
                    print(f"{indent}{'└───' if is_last else '├───'}" + "┐")
                    parser.print_tree(item, indent + ("    " if is_last else "│   "), True)
                else:
                    print(f"{indent}{'└── ' if is_last else '├── '}{item}")
        else:
            print(f"{indent}{'└── ' if last else '├── '}{tree}")


if __name__  == '__main__':
    os.chdir("/home/carl/DSL-server/server")
    test_file = "../scripts/script3.txt"
    result = parser.parse_script(test_file)
    print(result)

    parser.print_tree(result)