from syntax import *
from lexer import *

class Parser(object):
    '''Analyzer'''

    def __init__(self, content):
        self.content = content

        lexer = Lexer(self.content)
        self.content = lexer.main()

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

