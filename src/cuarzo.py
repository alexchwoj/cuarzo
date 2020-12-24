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
from code_parse import *
from compiler_logger import *

# File name
file_name = None

# Document content
content = None

# Main functions
def lexer():
    lexer = Lexer(content)
    lexer.main()
    for token in lexer.tokens:
        print('[Lexer] (%s, %s)' % (token.type, token.value))


def parser():
    parser = Parser(content)
    parser.main()
    parser.display(parser.tree.root)


def assembler():
    assem = Assembler(content, file_name)
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

# Init menu
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
    content = preprocessor(source_file, file_name)

    if option in ['-compile', '-c']:
        assembler()
    
    if option in ['-lexer', '-l']:
        lexer()

    if option in ['-parser', '-p']:
        parser()