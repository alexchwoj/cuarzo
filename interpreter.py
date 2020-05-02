import os
import socket
import platform
from colorama import init, Fore

if platform.system() == 'Windows':
    init(convert = True)

def open_file(filename):
    if not os.path.exists(filename):
        print(f"Cuarzo: can't open file '{filename}': No such file or directory")
    else:
        program = []

        with open(filename, 'r') as file:
            program = [line.strip() for line in file]

        
        modules_to_load = []
        for i in range(len(program)):
            if program[i][:8] == '#include':
                module_name = program[i][10:][:len(program[i][10:]) - 1]

                if not os.path.exists(module_name):
                    print(f"Cuarzo: Error on line {i + 1} ({filename}): Can't open file '{module_name}', no such file or directory")
                    return
                
                modules_to_load.append(module_name)


        program = []
        for i in range(len(modules_to_load)):
            with open(modules_to_load[i], 'r') as file:
                module_content = [line.strip() for line in file]
                program.extend(module_content)


        with open(filename, 'r') as file:
            principal_module = [line.strip() for line in file]
            program.extend(principal_module)


        return program


def interpret(script, filename):
    for i in range(len(script)):
        # Print
        if script[i][:5] == 'print':
            chain = script[i][7:len(script[i]) - 1]
            chain = chain.replace('~n~', '\n')
            chain = chain.replace('~r~', Fore.RED)
            chain = chain.replace('~g~', Fore.GREEN)
            chain = chain.replace('~y~', Fore.YELLOW)
            chain = chain.replace('~b~', Fore.BLUE)
            chain = chain.replace('~m~', Fore.MAGENTA)
            chain = chain.replace('~c~', Fore.CYAN)
            chain = chain.replace('~w~', Fore.WHITE)

            init_var_name = ''

            for x in range(len(chain)):
                if chain[x] == '{':
                    init_var_name = chain[x + 1:]

            for z in range(len(init_var_name)):
                if init_var_name[z] == '}':
                    var_name = init_var_name[:z]
                    chain = chain.replace('{' + var_name + '}', str(vars()[var_name + ' ']))

            print(chain)

        # Variables
        elif script[i][:3] == 'new':
            if script[i][4:9] == 'float':
                for x in range(len(script[i][10:])):
                    if script[i][10:][x] == '=':
                        result = script[i][x:]
                        vars()[script[i][10:][:x]] = float(result[x + 3:])

            elif script[i][4:8] == 'bool':
                for x in range(len(script[i][9:])):
                    if script[i][9:][x] == '=':
                        result = script[i][x:]
                        vars()[script[i][9:][:x]] = str(result[x + 3:])

            elif script[i][4:7] == 'int':
                for x in range(len(script[i][8:])):
                    if script[i][8:][x] == '=':
                        result = script[i][x:]
                        vars()[script[i][8:][:x]] = int(result[x + 3:])
            else:
                print(f'\nCuarzo: Error on line {i + 1} ({filename}): Invalid variable type\n> {script[i]}')
                return

        # Sockets
        elif script[i][:13] == 'socket_packet':
            args = script[i][13:].split()

            for i in range(len(args)):
                args[i] = args[i].replace(",", "")

                if i == 0:
                    args[i] = args[i].replace('"', '')

            if len(args) < 4:
                print(f'\nCuarzo: Error on line {i + 1} ({filename}): Number of arguments does not match definition\n> {script[i]}')
                return

            if args[3] == "udp":
                csocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_DGRAM)

            elif args[3] == "tcp":
                csocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM)

            else:
                print(f'\nCuarzo: Error on line {i + 1} ({filename}): Invalid socket protocol ({args[3]})\n> {script[i]}')
                return

            try:
                csocket.sendto(args[1].encode(), (args[1], int(args[2])))

            except Exception as e:
                print(f'\nCuarzo: Error on line {i + 1} ({filename}): Invalid address ({args[1]}:{args[2]})\n> {script[i]}')
                return


        # Comments
        elif script[i][:2] == '//':
            pass


        # Spaces
        elif script[i] == '' or script[i] == ' ':
            pass


        # Includes
        elif script[i][:8] == '#include':
            pass

        else:
            print(f'\nCuarzo: Error on line {i + 1} ({filename}): Invalid syntax\n> {script[i]}')
            return