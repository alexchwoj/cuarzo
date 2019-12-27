import sys
import interpreter

filename = sys.argv[1]

script = interpreter.open_file(filename)
interpreter.interpret(script, filename)