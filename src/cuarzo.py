# Tags
__author__ = "Yahir Vlatko Kozel"
__copyright__ = "Copyright (c) 2020-2021, Hyaxe Technologies Corp. "

__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Yahir Vlatko Kozel"
__email__ = "atom@hyaxe.com"
__status__ = "Production"

# Libs
import os
import re
import sys
import time
import argparse
import platform

# Start compilation time
compilation_start = time.time()

# Modules
from tokenize import *
from syntax import *
from assembler import *
from preprocessor import *
from lexer import *
from compiler_logger import *

# File name
file_name = None

# Document content
content = None


class Parser(object):
    '''Analyzer'''

    def __init__(self):
        global content
        lexer = Lexer(content)
        content = lexer.main()
        # Tokens to analyze
        self.tokens = lexer.tokens
        # Token subscript
        self.index = 0
        # The final syntax tree generated
        self.tree = SyntaxTree()

    # Process the part between braces
    def _block(self, father_tree):
        self.index += 1
        sentence_tree = SyntaxTree()
        sentence_tree.current = sentence_tree.root = SyntaxTreeNode('Sentence')
        father_tree.add_child_node(sentence_tree.root, father_tree.root)
        while True:
            # Prayer pattern
            sentence_pattern = self._judge_sentence_pattern()
            
            # Statement
            if sentence_pattern == 'STATEMENT':
                self._statement(sentence_tree.root)
            
            # Assignment statement
            elif sentence_pattern == 'ASSIGNMENT':
                self._assignment(sentence_tree.root)
            
            # Function call
            elif sentence_pattern == 'FUNCTION_CALL':
                self._function_call(sentence_tree.root)
            
            # Control flow statement
            elif sentence_pattern == 'CONTROL':
                self._control(sentence_tree.root)
            
            # Return statement
            elif sentence_pattern == 'RETURN':
                self._return(sentence_tree.root)
            
            # Locking clamp, end of function
            elif sentence_pattern == 'RB_BRACKET':
                break
            
            else:
                print(f'[Error] Invalid block (sentence: {sentence_pattern})')
                exit()

    # Include sentence pattern
    def _include(self, father = None):
        if not father:
            father = self.tree.root
        include_tree = SyntaxTree()
        include_tree.current = include_tree.root = SyntaxTreeNode('Include')
        self.tree.add_child_node(include_tree.root, father)
        # The number of double quotes in the include statement
        cnt = 0
        # whether the include statement ends
        flag = True
        while flag:
            if self.tokens[self.index] == '\"':
                cnt += 1
            if self.index >= len(self.tokens) or cnt >= 2 or self.tokens[self.index].value == '>':
                flag = False
            include_tree.add_child_node(
                SyntaxTreeNode(self.tokens[self.index].value), include_tree.root)
            self.index += 1

    # Function declaration
    def _function_statement(self, father = None):
        if not father:
            father = self.tree.root
        
        func_statement_tree = SyntaxTree()
        func_statement_tree.current = func_statement_tree.root = SyntaxTreeNode(
            'FunctionStatement')
        self.tree.add_child_node(func_statement_tree.root, father)

        flag = True
        while flag and self.index < len(self.tokens):
            # If it is a function return type
            if self.tokens[self.index].value in keywords[0]:
                return_type = SyntaxTreeNode('Type')
                func_statement_tree.add_child_node(return_type)
                func_statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}))
                self.index += 1
            
            # If it is a function name
            elif self.tokens[self.index].type == 'IDENTIFIER':
                func_name = SyntaxTreeNode('FunctionName')
                func_statement_tree.add_child_node(
                    func_name, func_statement_tree.root)
                # extra_info
                func_statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {'type': 'FUNCTION_NAME'}))
                self.index += 1
            
            # If it is a parameter sequence
            elif self.tokens[self.index].type == 'LL_BRACKET':
                params_list = SyntaxTreeNode('StateParameterList')
                func_statement_tree.add_child_node(
                    params_list, func_statement_tree.root)
                self.index += 1
                while self.tokens[self.index].type != 'RL_BRACKET':
                    if self.tokens[self.index].value in keywords[0]:
                        param = SyntaxTreeNode('Parameter')
                        func_statement_tree.add_child_node(param, params_list)
                        # extra_info
                        func_statement_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}), param)
                        if self.tokens[self.index + 1].type == 'IDENTIFIER':
                            # extra_info
                            func_statement_tree.add_child_node(SyntaxTreeNode(self.tokens[self.index + 1].value, 'IDENTIFIER', {
                                                               'type': 'VARIABLE', 'variable_type': self.tokens[self.index].value}), param)
                        
                        else:
                            print('[Error] An function definition parameter is invalid')
                            exit()
                        
                        self.index += 1
                    self.index += 1
                self.index += 1
            
            # If you met the opening brace
            elif self.tokens[self.index].type == 'LB_BRACKET':
                self._block(func_statement_tree)

    # Declaration statement
    def _statement(self, father = None):
        if not father:
            father = self.tree.root
        statement_tree = SyntaxTree()
        statement_tree.current = statement_tree.root = SyntaxTreeNode(
            'Statement')
        self.tree.add_child_node(statement_tree.root, father)
        # Temporarily used to save the type of the current declaration statement to facilitate the identification of multiple variable declarations
        tmp_variable_type = None
        while self.tokens[self.index].type != 'SEMICOLON':
            # Variable type
            if self.tokens[self.index].value in keywords[0]:
                tmp_variable_type = self.tokens[self.index].value
                variable_type = SyntaxTreeNode('Type')
                statement_tree.add_child_node(variable_type)
                # extra_info
                statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FIELD_TYPE', {'type': self.tokens[self.index].value}))
            
            # Variable name
            elif self.tokens[self.index].type == 'IDENTIFIER':
                # extra_info
                statement_tree.add_child_node(SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {
                                              'type': 'VARIABLE', 'variable_type': tmp_variable_type}), statement_tree.root)
            
            # Array size
            elif self.tokens[self.index].type == 'DIGIT_CONSTANT':
                statement_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'DIGIT_CONSTANT'), statement_tree.root)
                statement_tree.current.left.set_extra_info(
                    {'type': 'LIST', 'list_type': tmp_variable_type})
            
            # Array element
            elif self.tokens[self.index].type == 'LB_BRACKET':
                self.index += 1
                constant_list = SyntaxTreeNode('ConstantList')
                statement_tree.add_child_node(
                    constant_list, statement_tree.root)
                while self.tokens[self.index].type != 'RB_BRACKET':
                    if self.tokens[self.index].type == 'DIGIT_CONSTANT':
                        statement_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, 'DIGIT_CONSTANT'), constant_list)
                    self.index += 1
            
            # Multiple variable declaration
            elif self.tokens[self.index].type == 'COMMA':
                while self.tokens[self.index].type != 'SEMICOLON':
                    if self.tokens[self.index].type == 'IDENTIFIER':
                        tree = SyntaxTree()
                        tree.current = tree.root = SyntaxTreeNode('Statement')
                        self.tree.add_child_node(tree.root, father)
                        # Types of
                        variable_type = SyntaxTreeNode('Type')
                        tree.add_child_node(variable_type)
                        # extra_info
                        # Type of
                        tree.add_child_node(
                            SyntaxTreeNode(tmp_variable_type, 'FIELD_TYPE', {'type': tmp_variable_type}))
                        # Variable name
                        tree.add_child_node(SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER', {
                                            'type': 'VARIABLE', 'variable_type': tmp_variable_type}), tree.root)
                    self.index += 1
                break
            self.index += 1
        self.index += 1

    # Assignment statement-->TODO
    def _assignment(self, father = None):
        if not father:
            father = self.tree.root
        
        assign_tree = SyntaxTree()
        assign_tree.current = assign_tree.root = SyntaxTreeNode('Assignment')
        self.tree.add_child_node(assign_tree.root, father)
        while self.tokens[self.index].type != 'SEMICOLON':
            # Assigned variable
            if self.tokens[self.index].type == 'IDENTIFIER':
                assign_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'IDENTIFIER'))
                self.index += 1
            
            elif self.tokens[self.index].type == 'ASSIGN':
                self.index += 1
                self._expression(assign_tree.root)
        self.index += 1

    # The while statement does not deal with the do-while situation, only the while
    def _while(self, father=None):
        while_tree = SyntaxTree()
        while_tree.current = while_tree.root = SyntaxTreeNode(
            'Control', 'WhileControl')
        self.tree.add_child_node(while_tree.root, father)

        self.index += 1
        if self.tokens[self.index].type == 'LL_BRACKET':
            tmp_index = self.index
            while self.tokens[tmp_index].type != 'RL_BRACKET':
                tmp_index += 1
            self._expression(while_tree.root, tmp_index)

            if self.tokens[self.index].type == 'LB_BRACKET':
                self._block(while_tree)

    # for statement
    def _for(self, father = None):
        for_tree = SyntaxTree()
        for_tree.current = for_tree.root = SyntaxTreeNode(
            'Control', 'ForControl')
        
        self.tree.add_child_node(for_tree.root, father)
        # Mark whether the for statement ends
        while True:
            token_type = self.tokens[self.index].type
            # for tag
            if token_type == 'FOR':
                self.index += 1
            
            # Left parenthesis
            elif token_type == 'LL_BRACKET':
                self.index += 1
                # First find the position of the closing parenthesis
                tmp_index = self.index
                while self.tokens[tmp_index].type != 'RL_BRACKET':
                    tmp_index += 1
                
                # The part before the first semicolon in the for statement
                self._assignment(for_tree.root)
                # The middle part of the two semicolons
                self._expression(for_tree.root)
                self.index += 1
                # The part after the second semicolon
                self._expression(for_tree.root, tmp_index)
                self.index += 1
            
            # If it is an opening brace
            elif token_type == 'LB_BRACKET':
                self._block(for_tree)
                break
        
        # Exchange the third child node and the fourth child node under the for statement
        current_node = for_tree.root.first_son.right.right
        next_node = current_node.right
        for_tree.switch(current_node, next_node)

    # if statement
    def _if_else(self, father = None):
        if_else_tree = SyntaxTree()
        if_else_tree.current = if_else_tree.root = SyntaxTreeNode(
            'Control', 'IfElseControl')
        self.tree.add_child_node(if_else_tree.root, father)

        if_tree = SyntaxTree()
        if_tree.current = if_tree.root = SyntaxTreeNode('IfControl')
        if_else_tree.add_child_node(if_tree.root)

        # if flag
        if self.tokens[self.index].type == 'IF':
            self.index += 1
            # Left parenthesis
            if self.tokens[self.index].type == 'LL_BRACKET':
                self.index += 1
                # Position of closing parenthesis
                tmp_index = self.index
                while self.tokens[tmp_index].type != 'RL_BRACKET':
                    tmp_index += 1
                
                self._expression(if_tree.root, tmp_index)
                self.index += 1
            
            else:
                print(f'[Error] lack of left bracket (index: {self.index})')
                exit()

            # Opening brace
            if self.tokens[self.index].type == 'LB_BRACKET':
                self._block(if_tree)

        # If it is the else keyword
        if self.tokens[self.index].type == 'ELSE':
            self.index += 1
            else_tree = SyntaxTree()
            else_tree.current = else_tree.root = SyntaxTreeNode('ElseControl')
            if_else_tree.add_child_node(else_tree.root, if_else_tree.root)
            # Opening brace
            if self.tokens[self.index].type == 'LB_BRACKET':
                self._block(else_tree)

    def _control(self, father = None):
        token_type = self.tokens[self.index].type
        if token_type == 'WHILE' or token_type == 'DO':
            self._while(father)
        
        elif token_type == 'IF':
            self._if_else(father)
        
        elif token_type == 'FOR':
            self._for(father)
        
        else:
            print('[Error] control style not supported!')
            exit()

    # Expression-->TODO
    def _expression(self, father = None, index = None):
        if not father:
            father = self.tree.root
        
        # Operator precedence
        operator_priority = {'>': 0, '<': 0, '>=': 0, '<=': 0,
                             '+': 1, '-': 1, '*': 2, '/': 2, '++': 3, '--': 3, '!': 3}
        
        # Operator stack
        operator_stack = []
        # Inverse Polish expression result converted into
        reverse_polish_expression = []
        # Infix expression is converted to postfix expression, that is, reverse Polish expression
        while self.tokens[self.index].type != 'SEMICOLON':
            if index and self.index >= index:
                break
            
            # If it is constant
            if self.tokens[self.index].type == 'DIGIT_CONSTANT':
                tree = SyntaxTree()
                tree.current = tree.root = SyntaxTreeNode(
                    'Expression', 'Constant')
                tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, '_Constant'))
                reverse_polish_expression.append(tree)
            
            # If it is a variable or an element of an array
            elif self.tokens[self.index].type == 'IDENTIFIER':
                # Variable
                if self.tokens[self.index + 1].value in operators or self.tokens[self.index + 1].type == 'SEMICOLON':
                    tree = SyntaxTree()
                    tree.current = tree.root = SyntaxTreeNode(
                        'Expression', 'Variable')
                    tree.add_child_node(
                        SyntaxTreeNode(self.tokens[self.index].value, '_Variable'))
                    reverse_polish_expression.append(tree)
                
                # ID of an element of the array[i]
                elif self.tokens[self.index + 1].type == 'LM_BRACKET':
                    tree = SyntaxTree()
                    tree.current = tree.root = SyntaxTreeNode(
                        'Expression', 'ArrayItem')
                    
                    # The name of the array
                    tree.add_child_node(
                        SyntaxTreeNode(self.tokens[self.index].value, '_ArrayName'))
                    
                    self.index += 2
                    if self.tokens[self.index].type != 'DIGIT_CONSTANT' and self.tokens[self.index].type != 'IDENTIFIER':
                        print('[Error] Array table must be constant or identifier')
                        print(self.tokens[self.index].type)
                        exit()
                   
                    else:
                        # Array subscript
                        tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, '_ArrayIndex'), tree.root)
                        reverse_polish_expression.append(tree)
            
            # If it is an operator
            elif self.tokens[self.index].value in operators or self.tokens[self.index].type == 'LL_BRACKET' or self.tokens[self.index].type == 'RL_BRACKET':
                tree = SyntaxTree()
                tree.current = tree.root = SyntaxTreeNode(
                    'Operator', 'Operator')
                tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, '_Operator'))
                
                # If it is a left parenthesis, directly push the stack
                if self.tokens[self.index].type == 'LL_BRACKET':
                    operator_stack.append(tree.root)
                
                # If it is a right parenthesis, pop the stack until you encounter a left parenthesis
                elif self.tokens[self.index].type == 'RL_BRACKET':
                    while operator_stack and operator_stack[-1].current.type != 'LL_BRACKET':
                        reverse_polish_expression.append(operator_stack.pop())
                    
                    # Pop the opening bracket
                    if operator_stack:
                        operator_stack.pop()
                
                # Others can only be operators
                else:
                    while operator_stack and operator_priority[tree.current.value] < operator_priority[operator_stack[-1].current.value]:
                        reverse_polish_expression.append(operator_stack.pop())
                    operator_stack.append(tree)
            self.index += 1
        
        # Finally, the symbol stack is cleared, and finally the reverse Polish expression reverse_polish_expression is obtained
        while operator_stack:
            reverse_polish_expression.append(operator_stack.pop())

        # Operand stack
        operand_stack = []
        child_operators = [['!', '++', '--'], [
            '+', '-', '*', '/', '>', '<', '>=', '<=']]
        for item in reverse_polish_expression:
            if item.root.type != 'Operator':
                operand_stack.append(item)
            
            else:
                # Processing unary operators
                if item.current.value in child_operators[0]:
                    a = operand_stack.pop()
                    new_tree = SyntaxTree()
                    new_tree.current = new_tree.root = SyntaxTreeNode(
                        'Expression', 'SingleOperand')
                    
                    # Add operator
                    new_tree.add_child_node(item.root)
                    # Add operand
                    new_tree.add_child_node(a.root, new_tree.root)
                    operand_stack.append(new_tree)
                
                # Binocular operator
                elif item.current.value in child_operators[1]:
                    b = operand_stack.pop()
                    a = operand_stack.pop()
                    new_tree = SyntaxTree()
                    new_tree.current = new_tree.root = SyntaxTreeNode(
                        'Expression', 'DoubleOperand')
                    # First operand
                    new_tree.add_child_node(a.root)
                    # Operator
                    new_tree.add_child_node(item.root, new_tree.root)
                    # Second operand
                    new_tree.add_child_node(b.root, new_tree.root)
                    operand_stack.append(new_tree)
                
                else:
                    print('[Error] Operator %s not supported' % item.current.value)
                    exit()
        
        self.tree.add_child_node(operand_stack[0].root, father)

    # Function call
    def _function_call(self, father=None):
        if not father:
            father = self.tree.root
        func_call_tree = SyntaxTree()
        func_call_tree.current = func_call_tree.root = SyntaxTreeNode(
            'FunctionCall')
        self.tree.add_child_node(func_call_tree.root, father)

        while self.tokens[self.index].type != 'SEMICOLON':
            # Function name
            if self.tokens[self.index].type == 'IDENTIFIER':
                func_call_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value, 'FUNCTION_NAME'))
            
            # Left parenthesis
            elif self.tokens[self.index].type == 'LL_BRACKET':
                self.index += 1
                params_list = SyntaxTreeNode('CallParameterList')
                func_call_tree.add_child_node(params_list, func_call_tree.root)
                while self.tokens[self.index].type != 'RL_BRACKET':
                    if self.tokens[self.index].type == 'IDENTIFIER' or self.tokens[self.index].type == 'DIGIT_CONSTANT' or self.tokens[self.index].type == 'STRING_CONSTANT':
                        func_call_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, self.tokens[self.index].type), params_list)
                    
                    elif self.tokens[self.index].type == 'DOUBLE_QUOTE':
                        self.index += 1
                        func_call_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, self.tokens[self.index].type), params_list)
                        self.index += 1
                    
                    elif self.tokens[self.index].type == 'ADDRESS':
                        func_call_tree.add_child_node(
                            SyntaxTreeNode(self.tokens[self.index].value, 'ADDRESS'), params_list)
                    
                    self.index += 1
            else:
                LoggerError(f'An function call is invalid ({self.tokens[self.index].type}, {self.tokens[self.index].value})', file_name, 0)
                exit()
            
            self.index += 1
        self.index += 1

    # return statement-->TODO
    def _return(self, father=None):
        if not father:
            father = self.tree.root
        return_tree = SyntaxTree()
        return_tree.current = return_tree.root = SyntaxTreeNode('Return')
        self.tree.add_child_node(return_tree.root, father)
        while self.tokens[self.index].type != 'SEMICOLON':
            # Assigned variable
            if self.tokens[self.index].type == 'RETURN':
                return_tree.add_child_node(
                    SyntaxTreeNode(self.tokens[self.index].value))
                self.index += 1
            
            else:
                self._expression(return_tree.root)
        self.index += 1

    # Determine the sentence pattern according to the sentence beginning of a sentence pattern
    def _judge_sentence_pattern(self):
        token_value = self.tokens[self.index].value
        token_type = self.tokens[self.index].type
        # include sentence pattern
        if token_type == 'SHARP' and self.tokens[self.index + 1].type == 'INCLUDE':
            return 'INCLUDE'
        
        # Control sentence pattern
        elif token_value in keywords[1]:
            return 'CONTROL'
        
        # It may be a declaration statement or a function declaration statement
        elif token_value in keywords[0] and self.tokens[self.index + 1].type == 'IDENTIFIER':
            index_2_token_type = self.tokens[self.index + 2].type
            if index_2_token_type == 'LL_BRACKET':
                return 'FUNCTION_STATEMENT'
            
            elif index_2_token_type == 'SEMICOLON' or index_2_token_type == 'LM_BRACKET' or index_2_token_type == 'COMMA':
                return 'STATEMENT'
            
            else:
                return 'ERROR'
        
        # May be a function call or assignment statement
        elif token_type == 'IDENTIFIER':
            index_1_token_type = self.tokens[self.index + 1].type
            if index_1_token_type == 'LL_BRACKET':
                return 'FUNCTION_CALL'
            
            elif index_1_token_type == 'ASSIGN':
                return 'ASSIGNMENT'
            
            else:
                return 'ERROR'
        
        # return statement
        elif token_type == 'RETURN':
            return 'RETURN'
        
        # The closing brace indicates the end of the function
        elif token_type == 'RB_BRACKET':
            self.index += 1
            return 'RB_BRACKET'
        
        else:
            return 'ERROR'

    # Main program
    def main(self):
        # Root node
        self.tree.current = self.tree.root = SyntaxTreeNode('Sentence')
        while self.index < len(self.tokens):
            # Sentence pattern
            sentence_pattern = self._judge_sentence_pattern()
            # If it is an include sentence
            if sentence_pattern == 'INCLUDE':
                self._include()
            
            # Function declaration statement
            elif sentence_pattern == 'FUNCTION_STATEMENT':
                self._function_statement()
                break
            
            # Declaration statement
            elif sentence_pattern == 'STATEMENT':
                self._statement()
            
            # Function call
            elif sentence_pattern == 'FUNCTION_CALL':
                self._function_call()
            
            else:
                print('[Error] main broken')
                exit()

    # DFS traverses the syntax tree
    def display(self, node):
        if not node:
            return
        print('( self: %s %s, father: %s, left: %s, right: %s )' % (node.value, node.type, node.father.value if node.father else None, node.left.value if node.left else None, node.right.value if node.right else None))
        child = node.first_son
        while child:
            self.display(child)
            child = child.right


class Assembler(object):
    '''Compiled into assembly language'''

    def __init__(self):
        self.parser = Parser()
        self.parser.main()
        # Syntax tree
        self.tree = self.parser.tree
        # Assembly file manager to be generated
        self.ass_file_handler = AssemblerFileHandler(file_name)
        # Symbol table
        self.symbol_table = {}
        # Grammar type
        self.sentence_type = ['Sentence', 'Include', 'FunctionStatement',
                              'Statement', 'FunctionCall', 'Assignment', 'Control', 'Expression', 'Return']
        # Symbol stack in expression
        self.operator_stack = []
        # Operator stack in expression
        self.operand_stack = []
        # How many labels have been declared
        self.label_cnt = 0
        # label in if else
        self.labels_ifelse = {}

    # include sentence pattern
    def _include(self, node = None):
        pass

    # Function definition sentence pattern
    def _function_statement(self, node = None):
        # First son
        current_node = node.first_son
        while current_node:
            if current_node.value == 'FunctionName':
                if current_node.first_son.value != 'main':
                    print(f'[Error] Function statement is not supported (function: {current_node.first_son.value})')
                    exit()
                
                else:
                    self.ass_file_handler.insert('.globl main', 'TEXT')
                    self.ass_file_handler.insert('main:', 'TEXT')
                    self.ass_file_handler.insert('finit', 'TEXT')
            
            elif current_node.value == 'Sentence':
                self.traverse(current_node.first_son)
            
            current_node = current_node.right

    # Simple sizeof
    def _sizeof(self, _type):
        size = -1
        if _type == 'int' or _type == 'float' or _type == 'long':
            size = 4
        
        elif _type == 'char':
            size = 1
        
        elif _type == 'double':
            size = 8
        return str(size)

    # Declaration statement
    def _statement(self, node = None):
        # The declaration statement in the corresponding assembly code
        line = None
        # 1: initialized, 0: not initialized
        flag = 0
        # Variable data type
        variable_field_type = None
        # Variable type, is it an array or a single variable
        variable_type = None
        # variable name
        variable_name = None
        current_node = node.first_son
        while current_node:
            # Types of
            if current_node.value == 'Type':
                variable_field_type = current_node.first_son.value
            
            # variable name
            elif current_node.type == 'IDENTIFIER':
                variable_name = current_node.value
                variable_type = current_node.extra_info['type']
                line = '.lcomm ' + variable_name + \
                    ', ' + self._sizeof(variable_field_type)
            
            # Array element
            elif current_node.value == 'ConstantList':
                line = variable_name + ': .' + variable_field_type + ' '
                tmp_node = current_node.first_son
                # Save the array
                array = []
                while tmp_node:
                    array.append(tmp_node.value)
                    tmp_node = tmp_node.right
                
                line += ', '.join(array)
            current_node = current_node.right
        self.ass_file_handler.insert(
            line, 'BSS' if variable_type == 'VARIABLE' else 'DATA')
        
        # Save the variable in the symbol table
        self.symbol_table[variable_name] = {
            'type': variable_type, 'field_type': variable_field_type}

    # Function call
    def _function_call(self, node = None):
        current_node = node.first_son
        func_name = None
        parameter_list = []
        while current_node:
            # Function name
            if current_node.type == 'FUNCTION_NAME':
                func_name = current_node.value
                if func_name != 'scanf' and func_name != 'printf':
                    print(f'[Error] Function call not supported (function: {func_name})')
                    exit()
            
            # Function parameters
            elif current_node.value == 'CallParameterList':
                tmp_node = current_node.first_son
                while tmp_node:
                    # Is a constant
                    if tmp_node.type == 'DIGIT_CONSTANT' or tmp_node.type == 'STRING_CONSTANT':
                        # The name of the parameter in the assembly
                        label = 'label_' + str(self.label_cnt)
                        self.label_cnt += 1
                        if tmp_node.type == 'STRING_CONSTANT':
                            # Add the parameter definition in the data segment
                            line = label + ': .asciz "' + tmp_node.value + '"'
                            self.ass_file_handler.insert(line, 'DATA')
                        
                        else:
                            print(f'[Error] In functionc_call digital constant parameter is not supported (type: {tmp_node.type})')
                            exit()
                        
                        self.symbol_table[label] = {
                            'type': 'STRING_CONSTANT', 'value': tmp_node.value}
                        parameter_list.append(label)
                    
                    # Is a variable
                    elif tmp_node.type == 'IDENTIFIER':
                        parameter_list.append(tmp_node.value)
                    
                    elif tmp_node.type == 'ADDRESS':
                        pass
                    
                    else:
                        print(f'[Error] Parameter type is not supported (type: {tmp_node.type}, value: {tmp_node.value})')
                        exit()
                    
                    tmp_node = tmp_node.right
            current_node = current_node.right
        
        # Add to code snippet
        if func_name == 'printf':
            #%esp to + value
            num = 0
            for parameter in parameter_list[::-1]:
                # If the type of the parameter is a string constant
                if self.symbol_table[parameter]['type'] == 'STRING_CONSTANT':
                    line = 'pushl $' + parameter
                    self.ass_file_handler.insert(line, 'TEXT')
                    num += 1
                
                elif self.symbol_table[parameter]['type'] == 'VARIABLE':
                    field_type = self.symbol_table[parameter]['field_type']
                    if field_type == 'int':
                        line = 'pushl ' + parameter
                        self.ass_file_handler.insert(line, 'TEXT')
                        num += 1
                    
                    elif field_type == 'float':
                        line = 'flds ' + parameter
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = r'subl $8, %esp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = r'fstpl (%esp)'
                        self.ass_file_handler.insert(line, 'TEXT')
                        num += 2
                    
                    else:
                        print('[Error] Field type except int and float is not supported')
                        exit()
                
                else:
                    print('[Error] Parameter type not supported')
                    exit()
            
            line = 'call printf'
            self.ass_file_handler.insert(line, 'TEXT')
            line = 'add $' + str(num * 4) + ', %esp'
            self.ass_file_handler.insert(line, 'TEXT')
        
        elif func_name == 'scanf':
            num = 0
            for parameter in parameter_list[::-1]:
                parameter_type = self.symbol_table[parameter]['type']
                if parameter_type == 'STRING_CONSTANT' or parameter_type == 'VARIABLE':
                    num += 1
                    line = 'pushl $' + parameter
                    self.ass_file_handler.insert(line, 'TEXT')
                
                else:
                    print('[Error] Parameter type not supported')
                    exit()
            
            line = 'call scanf'
            self.ass_file_handler.insert(line, 'TEXT')
            line = 'add $' + str(num * 4) + ', %esp'
            self.ass_file_handler.insert(line, 'TEXT')
    
    # Assignment statement
    def _assignment(self, node = None):
        current_node = node.first_son
        if current_node.type == 'IDENTIFIER' and current_node.right.value == 'Expression':
            expres = self._expression(current_node.right)
            # The type of the variable
            field_type = self.symbol_table[current_node.value]['field_type']
            if field_type == 'int':
                # constant
                if expres['type'] == 'CONSTANT':
                    line = 'movl $' + \
                        expres['value'] + ', ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                
                elif expres['type'] == 'VARIABLE':
                    line = 'movl ' + expres['value'] + ', ' + '%edi'
                    self.ass_file_handler.insert(line, 'TEXT')
                    line = 'movl %edi, ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                
                else:
                    pass
            
            elif field_type == 'float':
                if expres['type'] == 'CONSTANT':
                    line = 'movl $' + \
                        expres['value'] + ', ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                    line = 'filds ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                    line = 'fstps ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
                
                else:
                    line = 'fstps ' + current_node.value
                    self.ass_file_handler.insert(line, 'TEXT')
            else:
                print('[Error] Field type except int and float not supported')
                exit()
        
        else:
            print('[Error] Assignment wrong')
            exit()

    # for statement
    def _control_for(self, node = None):
        current_node = node.first_son
        # Traverse is the part in the for loop
        cnt = 2
        while current_node:
            # for the first part
            if current_node.value == 'Assignment':
                self._assignment(current_node)
            
            # for the second and third part
            elif current_node.value == 'Expression':
                if cnt == 2:
                    cnt += 1
                    line = 'label_' + str(self.label_cnt) + ':'
                    self.ass_file_handler.insert(line, 'TEXT')
                    self.label_cnt += 1
                    self._expression(current_node)
                
                else:
                    self._expression(current_node)
            
            # for statement part
            elif current_node.value == 'Sentence':
                self.traverse(current_node.first_son)
            current_node = current_node.right
        
        line = 'jmp label_' + str(self.label_cnt - 1)
        self.ass_file_handler.insert(line, 'TEXT')
        line = 'label_' + str(self.label_cnt) + ':'
        self.ass_file_handler.insert(line, 'TEXT')
        self.label_cnt += 1

    # if else statement
    def _control_if(self, node = None):
        current_node = node.first_son
        self.labels_ifelse['label_else'] = 'label_' + str(self.label_cnt)
        self.label_cnt += 1
        self.labels_ifelse['label_end'] = 'label_' + str(self.label_cnt)
        self.label_cnt += 1
        
        while current_node:
            if current_node.value == 'IfControl':
                if current_node.first_son.value != 'Expression' or current_node.first_son.right.value != 'Sentence':
                    print(f'[Error] Invalid control_if (node value: {current_node.first_son.value})')
                    exit()
                
                self._expression(current_node.first_son)
                self.traverse(current_node.first_son.right.first_son)
                line = 'jmp ' + self.labels_ifelse['label_end']
                self.ass_file_handler.insert(line, 'TEXT')
                line = self.labels_ifelse['label_else'] + ':'
                self.ass_file_handler.insert(line, 'TEXT')
            
            elif current_node.value == 'ElseControl':
                self.traverse(current_node.first_son)
                line = self.labels_ifelse['label_end'] + ':'
                self.ass_file_handler.insert(line, 'TEXT')
            current_node = current_node.right

    # while statement
    def _control_while(self, node = None):
        print('[Error] while not supported')

    # return statement
    def _return(self, node = None):
        current_node = node.first_son
        if current_node.value != 'return' or current_node.right.value != 'Expression':
            print('[Error] Invalid return')
            exit()
        
        else:
            current_node = current_node.right
            expres = self._expression(current_node)
            if expres['type'] == 'CONSTANT':
                line = 'pushl $' + expres['value']
                self.ass_file_handler.insert(line, 'TEXT')
                line = 'call exit'
                self.ass_file_handler.insert(line, 'TEXT')
            
            else:
                print(f'[Error] return type not supported (type: {expres["type"]})')
                exit()

    # Traversal expression
    def _traverse_expression(self, node = None):
        if not node:
            return
        if node.type == '_Variable':
            self.operand_stack.append(
                {'type': 'VARIABLE', 'operand': node.value})
        
        elif node.type == '_Constant':
            self.operand_stack.append(
                {'type': 'CONSTANT', 'operand': node.value})
        
        elif node.type == '_Operator':
            self.operator_stack.append(node.value)
        
        elif node.type == '_ArrayName':
            self.operand_stack.append(
                {'type': 'ARRAY_ITEM', 'operand': [node.value, node.right.value]})
            return
        
        current_node = node.first_son
        while current_node:
            self._traverse_expression(current_node)
            current_node = current_node.right

    # Determine whether a variable is of type float
    def _is_float(self, operand):
        return operand['type'] == 'VARIABLE' and self.symbol_table[operand['operand']]['field_type'] == 'float'
    # Determine whether the two operands contain a float type number

    def _contain_float(self, operand_a, operand_b):
        return self._is_float(operand_a) or self._is_float(operand_b)

    # expression
    def _expression(self, node=None):
        if node.type == 'Constant':
            return {'type': 'CONSTANT', 'value': node.first_son.value}
        
        # Empty first
        self.operator_priority = []
        self.operand_stack = []
        # Traverse the expression
        self._traverse_expression(node)

        # Binocular operator
        double_operators = ['+', '-', '*', '/', '>', '<', '>=', '<=']
        # Unary operator
        single_operators = ['++', '--']
        # Operator mapping to assembly instructions
        operator_map = {'>': 'jbe', '<': 'jae', '>=': 'jb', '<=': 'ja'}
        
        while self.operator_stack:
            operator = self.operator_stack.pop()
            if operator in double_operators:
                operand_b = self.operand_stack.pop()
                operand_a = self.operand_stack.pop()
                contain_float = self._contain_float(operand_a, operand_b)
                if operator == '+':
                    if contain_float:
                        line = 'flds ' if self._is_float(
                            operand_a) else 'filds '
                        line += operand_a['operand']
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'fadd ' if self._is_float(
                            operand_b) else 'fiadd '
                        line += operand_b['operand']
                        self.ass_file_handler.insert(line, 'TEXT')

                        # The calculation result is saved to bss_tmp
                        line = 'fstps bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'flds bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        
                        # The calculation result is pushed onto the stack
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        
                        # Record to symbol table
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'float'}
                    
                    else:
                        # First operand
                        if operand_a['type'] == 'ARRAY_ITEM':
                            line = 'movl ' + \
                                operand_a['operand'][1] + r', %edi'
                            self.ass_file_handler.insert(line, 'TEXT')
                            line = 'movl ' + \
                                operand_a['operand'][0] + r'(, %edi, 4), %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        
                        elif operand_a['type'] == 'VARIABLE':
                            line = 'movl ' + operand_a['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        
                        elif operand_a['type'] == 'CONSTANT':
                            line = 'movl $' + operand_a['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        
                        # Plus the second operand
                        if operand_b['type'] == 'ARRAY_ITEM':
                            line = 'movl ' + \
                                operand_b['operand'][1] + r', %edi'
                            self.ass_file_handler.insert(line, 'TEXT')
                            line = 'addl ' + \
                                operand_b['operand'][0] + r'(, %edi, 4), %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        
                        elif operand_b['type'] == 'VARIABLE':
                            line = 'addl ' + operand_b['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        
                        elif operand_b['type'] == 'CONSTANT':
                            line = 'addl $' + operand_b['operand'] + r', %eax'
                            self.ass_file_handler.insert(line, 'TEXT')
                        
                        # Assign to temporary operand
                        line = 'movl %eax, bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        
                        # The calculation result is pushed onto the stack
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        
                        # Record to symbol table
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'int'}

                elif operator == '-':
                    if contain_float:
                        # v
                        if self._is_float(operand_a):
                            if operand_a['type'] == 'VARIABLE':
                                line = 'flds ' if self._is_float(
                                    operand_a) else 'filds '
                                line += operand_a['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            
                            else:
                                pass
                        
                        else:
                            if operand_a['type'] == 'CONSTANT':
                                line = 'movl $' + \
                                    operand_a['operand'] + ', bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                            
                            else:
                                pass
                        
                        # Operand b
                        if self._is_float(operand_b):
                            if operand_b['type'] == 'VARIABLE':
                                line = 'flds ' if self._is_float(
                                    operand_b) else 'filds '
                                line += operand_b['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = 'fsub ' + operand_b['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            
                            else:
                                pass
                        
                        else:
                            if operand_b['type'] == 'CONSTANT':
                                line = 'movl $' + \
                                    operand_b['operand'] + ', bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = 'fisub bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                            
                            else:
                                pass
                        
                        # The calculation result is saved to bss_tmp
                        line = 'fstps bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'flds bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        
                        # The calculation result is pushed onto the stack
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        
                        # Record to symbol table
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'float'}
                    else:
                        print('[Error] Operator type not supported')
                        exit()
                
                # Floating point has not been considered, only integer multiplication is considered
                elif operator == '*':
                    if operand_a['type'] == 'ARRAY_ITEM':
                        line = 'movl ' + operand_a['operand'][1] + r', %edi'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'movl ' + \
                            operand_a['operand'][0] + r'(, %edi, 4), %eax'
                        self.ass_file_handler.insert(line, 'TEXT')
                    
                    else:
                        print('[Error] Operator not supported')
                        exit()

                    if operand_b['type'] == 'ARRAY_ITEM':
                        line = 'movl ' + operand_b['operand'][1] + r', %edi'
                        self.ass_file_handler.insert(line, 'TEXT')
                        # Multiply
                        line = 'mull ' + \
                            operand_b['operand'][0] + '(, %edi, 4)'
                        self.ass_file_handler.insert(line, 'TEXT')
                    
                    else:
                        print('[Error] Operator not supported')
                        exit()
                    
                    # Push the result into the stack
                    line = r'movl %eax, bss_tmp'
                    self.ass_file_handler.insert(line, 'TEXT')
                    self.operand_stack.append(
                        {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                    self.symbol_table['bss_tmp'] = {
                        'type': 'IDENTIFIER', 'field_type': 'int'}
                
                elif operator == '/':
                    if contain_float:
                        line = 'flds ' if self._is_float(
                            operand_a) else 'filds '
                        line += operand_a['operand']
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = 'fdiv ' if self._is_float(
                            operand_b) else 'fidiv '
                        line += operand_b['operand']
                        self.ass_file_handler.insert(line, 'TEXT')

                        # The calculation result is saved to bss_tmp
                        line = 'fstps bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        line = 'flds bss_tmp'
                        self.ass_file_handler.insert(line, 'TEXT')
                        
                        # The calculation result is pushed onto the stack
                        self.operand_stack.append(
                            {'type': 'VARIABLE', 'operand': 'bss_tmp'})
                        # Record to symbol table
                        self.symbol_table['bss_tmp'] = {
                            'type': 'IDENTIFIER', 'field_type': 'float'}
                    
                    else:
                        pass
                
                elif operator == '>=':
                    if contain_float:
                        if self._is_float(operand_a):
                            if operand_a['type'] == 'VARIABLE':
                                line = 'flds ' if self._is_float(
                                    operand_a) else 'filds '
                                line += operand_a['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            
                            else:
                                print('[Error] Array item not supported (>=)')
                                exit()
                        else:
                            pass

                        if self._is_float(operand_b):
                            if operand_b['type'] == 'VARIABLE':
                                line = 'fcom ' + operand_b['operand']
                                self.ass_file_handler.insert(line, 'TEXT')
                            
                            else:
                                print('[Error] Array item not supported (>=)')
                                exit()
                        
                        else:
                            if operand_b['type'] == 'CONSTANT':
                                line = 'movl $' + \
                                    operand_b['operand'] + ', bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = 'fcom bss_tmp'
                                self.ass_file_handler.insert(line, 'TEXT')
                                line = operator_map[
                                    '>='] + ' ' + self.labels_ifelse['label_else']
                                self.ass_file_handler.insert(line, 'TEXT')
                            
                            else:
                                pass
                    
                    else:
                        pass
                
                elif operator == '<':
                    if contain_float:
                        pass
                    
                    else:
                        line = 'movl $' if operand_a[
                            'type'] == 'CONSTANT' else 'movl '
                        line += operand_a['operand'] + ', %edi'
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = 'movl $' if operand_b[
                            'type'] == 'CONSTANT' else 'movl '
                        line += operand_b['operand'] + ', %esi'
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = r'cmpl %esi, %edi'
                        self.ass_file_handler.insert(line, 'TEXT')

                        line = operator_map[
                            '<'] + ' ' + 'label_' + str(self.label_cnt)
                        self.ass_file_handler.insert(line, 'TEXT')

            elif operator in single_operators:
                operand = self.operand_stack.pop()
                if operator == '++':
                    line = 'incl ' + operand['operand']
                    self.ass_file_handler.insert(line, 'TEXT')
                
                elif operator == '--':
                    pass
            
            else:
                print('[Error] Operator not supported')
                exit()
        
        result = {'type': self.operand_stack[0]['type'], 'value': self.operand_stack[
            0]['operand']} if self.operand_stack else {'type': '', 'value': ''}
        
        return result

    # Deal with a certain sentence pattern
    def _handler_block(self, node = None):
        if not node:
            return
        
        # The next node to be traversed
        if node.value in self.sentence_type:
            # If it is the root node
            if node.value == 'Sentence':
                self.traverse(node.first_son)
            
            # include statement
            elif node.value == 'Include':
                self._include(node)
            
            # Function declaration
            elif node.value == 'FunctionStatement':
                self._function_statement(node)
            
            # Declaration statement
            elif node.value == 'Statement':
                self._statement(node)
            
            # Function call
            elif node.value == 'FunctionCall':
                self._function_call(node)
            
            # Assignment statement
            elif node.value == 'Assignment':
                self._assignment(node)
            
            # Control statement
            elif node.value == 'Control':
                if node.type == 'IfElseControl':
                    self._control_if(node)
                
                elif node.type == 'ForControl':
                    self._control_for(node)
                
                elif node.type == 'WhileControl':
                    self._control_while()
                
                else:
                    print('[Error] Control type not supported')
                    exit()
            
            # Expression statement
            elif node.value == 'Expression':
                self._expression(node)
            
            # return statement
            elif node.value == 'Return':
                self._return(node)
            
            else:
                print('[Error] Sentenct type not supported')
                exit()

    # Traverse nodes
    def traverse(self, node = None):
        self._handler_block(node)
        next_node = node.right
        while next_node:
            self._handler_block(next_node)
            next_node = next_node.right


def lexer():
    lexer = Lexer(content)
    lexer.main()
    for token in lexer.tokens:
        print('[Lexer] (%s, %s)' % (token.type, token.value))


def parser():
    parser = Parser()
    parser.main()
    parser.display(parser.tree.root)


def assembler():
    assem = Assembler()
    assem.traverse(assem.tree.root)
    assem.ass_file_handler.generate_ass_file()

    print(f'Cuarzo {__version__}\t{__copyright__}')
    print(f'Code size:\t{len(content)} bytes')

    f = open(file_name + '.s', 'r')
    output_file = f.read()

    print(f'Assembly size:\t{len(output_file)} bytes')
    print(f'[Finished in {time.time() - compilation_start}ms]')

    if platform.system() == 'Linux':
        os.remove(file_name + '.s')


def show_help():
    print(f'Cuarzo {__version__}\t{__copyright__}')
    print('Compiler options:\n\t-c | Compile file\n\t-l | Analyze file with the lexical analyzer\n\t-p | Parse file\n\t-h | Show this message')
    print('\nUsage example:\n\tcuarzo test.caz -c')
    exit()


if __name__ == '__main__':
    # Args
    try:
        input_file = sys.argv[1]
        if input_file in ['-help', '-h']:
            show_help()

    except Exception as e:
        print('[Error] You need to enter a file as input!')
        print('Usage example:\n\tcuarzo test.caz -c')
        exit()

    try:
        option = sys.argv[2]
        
    except Exception as e:
        print('[Error] You have to enter an option!')
        print('Usage example:\n\tcuarzo test.caz -c')
        exit()
    
    # Options
    if option in ['-help', '-h']:
        show_help()

    if not os.path.isfile(input_file):
        print('[Error] You have to enter a valid file!')
        exit()

    file_name = sys.argv[1].split('.')[0]
    source_file = open(input_file, 'r')
    #content = source_file.read()
    content = preprocessor(source_file, file_name)

    if option in ['-compile', '-c']:
        assembler()
    
    if option in ['-lexer', '-l']:
        lexer()

    if option in ['-parser', '-p']:
        parser()