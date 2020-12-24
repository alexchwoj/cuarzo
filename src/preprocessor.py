import platform
from datetime import datetime
from compiler_logger import *

def preprocessor(file_handler, file_name, debug_output = False):
	lines = [line.strip() for line in file_handler]
	
	# Clean lines
	util_lines = [
		'#include <stdio.h>'
	]

	# Blocks
	opened_comment = False
	opened_if = False
	pass_if = True
	opened_blocks = 0

	# Macros
	defines = [
		['__CUARZO_SYSTEM_NAME__', platform.system()],
		['__CUARZO_SYSTEM_RELEASE__', platform.release()],
		['__CUARZO_SYSTEM_VERSION__', platform.version()],
		['__CUARZO_BUILD_DATE__', datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
	]

	for i in range( len(lines) ):
		try:
			single = lines[i]
			divided = single.split(' ')

			# Null char
			if single == '':
				continue
			
			# Messages tag
			if divided[0] == '#error':
				LoggerError( " ".join(map(str, divided[1:])), file_name, i )
				continue

			if divided[0] == '#warning':
				LoggerWarning( " ".join(map(str, divided[1:])), file_name, i )
				continue

			if divided[0] == '#info':
				LoggerInfo( " ".join(map(str, divided[1:])), file_name, i )
				continue

			# Add defines
			if divided[0] == '#define':
				valor = True
				
				try:
					valor = divided[2]
				
				except Exception as e:
					pass

				try:
					defines.append([ divided[1], valor])
				
				except Exception as e:
					LoggerError('After the "#define" instruction there must be a name to identify the address', file_name, i)
				
				continue

			# Undefine
			if divided[0] == '#undef':
				for define in defines:
					try:
						if define[0] == divided[1]:
							defines.remove(define)
				
					except Exception as e:
						LoggerError('After the "#undef" instruction there must be a name to identify the address', file_name, i)

				continue

			# If sentence
			if divided[0] == '#endif':
				opened_if = False
				pass_if = True
				continue

			if opened_if:
				if pass_if:
					continue

			else:
				if divided[0] == '#if':
					for define in defines:
						if define[0] == divided[2]:
							pass_if = False
					
					opened_if = True
					continue

			# Delete comments
			if divided[len(divided) - 1] == '*/':
				opened_comment = False
				continue

			if opened_comment:
				continue

			else:
				if divided[0] == '/*':
					opened_comment = True
					continue

			if divided[0] == '#':
				continue

			if divided[0] == '//':
				continue

			# Define valors
			for define in defines:
				single = single.replace(define[0], str(define[1]))

			# Set variables types
			if divided[0] == 'main()':
				single = single.replace('main()', 'int main()')

			if divided[0] == 'var':
				var_type = 'int'
				valor = ''

				try:
					valor = divided[3]

					# Float test
					try:
						float(valor)
						var_type = 'float'
					
					except Exception as e:
						pass
				
				except Exception as e:
					pass

				try:
					if not valor == '':
						single = f'{var_type} {divided[1]} = {" ".join(map(str, divided[3:]))}'

					else:
						single = f'{var_type} {divided[1]}'

				except Exception as e:
					LoggerError('The variable name has not been declared', file_name, i)

			# Fix funcs
			single = single.replace('print(', 'printf(')
			single = single.replace('input(', 'scanf(')

			# Put ;
			if divided[0] == '}':
				opened_blocks -= 1

			if opened_blocks:
				valid_line = True
				
				try:
					if divided[0][:4] == 'for(':
						valid_line = False

					if divided[0][0] == '{':
						valid_line = False

					if divided[0][:4] == 'else':
						valid_line = False

					if divided[0][:2] == 'if':
						valid_line = False

					if divided[0][0] == '}':
						valid_line = False
				
				except Exception as e:
					pass

				if valid_line:
					single += ';'

			if divided[0][0] == '{':
				opened_blocks += 1

			util_lines.append(single)

		except Exception as e:
			LoggerError(f'Internal error ({e})', file_name, i)

	if debug_output:
		for line in util_lines:
			LoggerInfo(line, file_name)

	return "".join(map(str, util_lines))