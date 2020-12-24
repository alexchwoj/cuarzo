import re
from tokenize import *

class Lexer(object):
    '''Lexical analyzer'''

    def __init__(self, content):
        # It is used to save the results of the lexical analysis.
        self.tokens = []
        self.content = content

    # Determine if it is a null character
    def is_blank(self, index):
        return (
            self.content[index] == ' ' or
            self.content[index] == '\t' or
            self.content[index] == '\n' or
            self.content[index] == '\r'
        )

    # Skip the null character
    def skip_blank(self, index):
        while index < len(self.content) and self.is_blank(index):
            index += 1
        return index

    # Determine if it's a keyword
    def is_keyword(self, value):
        for item in keywords:
            if value in item:
                return True
        return False

    # Lexical analysis main program
    def main(self):
        i = 0
        while i < len(self.content):
            i = self.skip_blank(i)
            
            # If you are trying to enter a header file, there is another possibility that it is a hexadecimal number, not judging
            if self.content[i] == '#':
                self.tokens.append(Token(4, self.content[i]))
                i = self.skip_blank(i + 1)
                while i < len(self.content):
                    if re.match('include', self.content[i:]):
                        self.tokens.append(Token(0, 'include'))
                        i = self.skip_blank(i + 7)

                    elif self.content[i] == '\"' or self.content[i] == '<':
                        self.tokens.append(Token(4, self.content[i]))
                        i = self.skip_blank(i + 1)
                        close_flag = '\"' if self.content[i] == '\"' else '>'

                        lib = ''
                        while self.content[i] != close_flag:
                            lib += self.content[i]
                            i += 1

                        self.tokens.append(Token(1, lib))
                        
                        # After jumping out of the loop obviously close_flog is found
                        self.tokens.append(Token(4, close_flag))
                        i = self.skip_blank(i + 1)
                        break
                    
                    else:
                        print(f'[Error] Invalid include (index: {i})')
                        exit()
            
            # If it's a letter or starts with an underscore
            elif self.content[i].isalpha() or self.content[i] == '_':
                # Find the index
                temp = ''
                while i < len(self.content) and (
                        self.content[i].isalpha() or
                        self.content[i] == '_' or
                        self.content[i].isdigit()):
                    temp += self.content[i]
                    i += 1
                
                if self.is_keyword(temp):
                    self.tokens.append(Token(0, temp))
                
                else:
                    self.tokens.append(Token(1, temp))
                
                i = self.skip_blank(i)
            
            # If it starts with a number
            elif self.content[i].isdigit():
                temp = ''
                while i < len(self.content):
                    if self.content[i].isdigit() or (
                            self.content[i] == '.' and self.content[i + 1].isdigit()):
                        temp += self.content[i]
                        i += 1
                    
                    elif not self.content[i].isdigit():
                        if self.content[i] == '.':
                            print(f'[Error] Invalid float (index: {i})')
                            exit()
                        
                        else:
                            break

                self.tokens.append(Token(2, temp))
                i = self.skip_blank(i)
            
            # If it is a separator
            elif self.content[i] in delimiters:
                self.tokens.append(Token(4, self.content[i]))
                # If is a string constant
                if self.content[i] == '\"':
                    i += 1
                    temp = ''
                    while i < len(self.content):
                        if self.content[i] != '\"':
                            temp += self.content[i]
                            i += 1
                        
                        else:
                            break
                   
                    else:
                        print('[Error] lack of \"')
                        exit()

                    self.tokens.append(Token(5, temp))
                    self.tokens.append(Token(4, '\"'))
                
                i = self.skip_blank(i + 1)
            
            # If it is an operator
            elif self.content[i] in operators:
                # If it is ++ or --
                if (self.content[i] == '+' or self.content[i] == '-') and (
                        self.content[i + 1] == self.content[i]):

                    self.tokens.append(Token(3, self.content[i] * 2))
                    i = self.skip_blank(i + 2)
                
                # If it is>= or <=
                elif (self.content[i] == '>' or self.content[i] == '<') and self.content[i + 1] == '=':
                    self.tokens.append(Token(3, self.content[i] + '='))
                    i = self.skip_blank(i + 2)
                
                # Other
                else:
                    self.tokens.append(Token(3, self.content[i]))
                    i = self.skip_blank(i + 1)

        return self.content
