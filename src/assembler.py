import os
import platform

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
