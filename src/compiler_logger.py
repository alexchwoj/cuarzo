from datetime import datetime

def LoggerError(message, file, line = 0, time = True):
	if time:
		print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] Error in file: {file}, line: {line}: {message}')
	
	else:
		print(f'Error in file: {file}, line: {line}: {message}')

	exit()


def LoggerWarning(message, file, line = 0, time = True):
	if time:
		print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] Warning in file: {file}, line: {line}: {message}')
	
	else:
		print(f'Warning in file: {file}, line: {line}: {message}')


def LoggerInfo(message, file, line = 0, time = True):
	if time:
		print(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] Info (file: {file}, line: {line}): {message}')
	
	else:
		print(f'Info (file: {file}, line: {line}): {message}')