import os
import platform
from code_parse import *


class AssemblerFileHandler(object):
    '''Keep generated assembly files'''

    def __init__(self, file_name):
        self.result = ['.data', '.bss', '.lcomm bss_tmp, 4', '.text']
        self.data_pointer = 1
        self.bss_pointer = 3
        self.text_pointer = 4
        self.file_name = file_name

    def insert(self, value, _type):
        # Insert into data field
        if _type == 'DATA':
            self.result.insert(self.data_pointer, value)
            self.data_pointer += 1
            self.bss_pointer += 1
            self.text_pointer += 1
        
        # Insert in bss field
        elif _type == 'BSS':
            self.result.insert(self.bss_pointer, value)
            self.bss_pointer += 1
            self.text_pointer += 1
        
        # Insert in code snippet
        elif _type == 'TEXT':
            self.result.insert(self.text_pointer, value)
            self.text_pointer += 1
        
        else:
            print(f'[Error] Invalid data tpye ({_type})')
            exit()

    # Save the result to a file
    def generate_ass_file(self):
        self.file = open(self.file_name + '.s', 'w+')
        self.file.write('\n'.join(self.result) + '\n')
        self.file.close()

        if platform.system() == 'Linux':
            os.system(f'gcc {self.file_name}.s -m32 -o {self.file_name}')


class Assembler(object):
    '''Compiled into assembly language'''

    def __init__(self, content, file_name):
        # File name
        self.file_name = file_name

        # File content
        self.content = content
        self.parser = Parser(self.content)
        self.parser.main()
        
        # Syntax tree
        self.tree = self.parser.tree
        
        # Assembly file manager to be generated
        self.ass_file_handler = AssemblerFileHandler(self.file_name)
        
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

