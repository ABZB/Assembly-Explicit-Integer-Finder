from main import *
from tkinter.filedialog import askdirectory
from pathlib import Path
from glob import *

def multisearch():
	target_value = input('What is the base-10 value you are searching for? ')
	
	try:
		target_value = int(target_value)
	except:
		print(target_value, 'is not an integer, it is ', type(target_value))
		return
	

	
	target_directory = askdirectory(title = 'What directory do you want to search?')
	
	while True:
		mode = int(input('Select mode:\n0 = Create a seperate text file for every file searched: \n1 = Create 1 text file: \n2 = Create 1 text file, and only look for the (much rarer) explicit assembly checks for equality: \n'))
		if(mode in {0, 1, 2}):
			break
		print('Error, mode was not 0, 1, or 2, it was', mode)
		
	while True:
		file_mask = int(input('Select files to search:\n0 = Everything: \n1 = Everything but GARC files: \n2 = Just .bin and .cro files: \n'))
		if(file_mask in {0,1,2}):
			break
		print('Error, search option was not 0, 1, or 2, it was', file_mask)
	
	match file_mask:
		case 0:
			result = list(Path(target_directory).rglob("*"))
		case 1:
			result = list(Path(target_directory).rglob("*.*"))
		case 2:
			result = [*list(Path(target_directory).rglob("*.bin")), *list(Path(target_directory).rglob("*.cro"))]


	match mode:
		case 0:
			target_directory = askdirectory(title = 'What directory do you want to save the results in?')
			for x in result:
				if(os.path.isfile(x)):
					output_file_name = x.replace('/', '_')
					search_binary_file_two_bytes(target_value, x, output_file_name)
			return
		case 1:
			explicit_address_array = []
			cmp_explicit_array = []
			two_subtractions_array = []
			
			for x in result:
				if(os.path.isfile(x)):
					temp_1, temp_2, temp_3 = search_binary_file_two_bytes(target_value, x, '', mode)
					explicit_address_array = [*explicit_address_array, '\n' + x.replace('/', '_') + '\n', *temp_1]
					cmp_explicit_array = [*explicit_address_array, '\n' + x.replace('/', '_') + '\n', *temp_2]
					two_subtractions_array = [*explicit_address_array, '\n' + x.replace('/', '_') + '\n', *temp_3]
		case 2:
			cmp_explicit_array = []
			two_subtractions_array = []
			for x in result:
				if(os.path.isfile(x)):
					print('Now searching: ', x)
					temp_1, temp_2, temp_3 = search_binary_file_two_bytes(target_value, x, '', mode)
					if(temp_2 != []):
						cmp_explicit_array = [*explicit_address_array, '\n' + x.replace('/', '_') + '\n', *temp_2]
					if(temp_3 != []):
						two_subtractions_array = [*explicit_address_array, '\n' + x.replace('/', '_') + '\n', *temp_3]
			
	low_byte = target_value % 256
	high_byte = target_value >> 8
				
	if(high_byte == 0):
		output_value_display = hex(low_byte)
	else:
		output_value_display = hex(low_byte) + ' ' + hex(high_byte)
	
	
	output_file_path = asksaveasfilename(title = 'Select text file to save output as', defaultextension = '.txt')
	
	with open(output_file_path, "w") as f:
		if(mode != 2):
			#explicitly written and loaded by functions
			f.write('The following are the hexadecimal addresses where the value ' + output_value_display + ' was found (written explicitly in little-Endian, presumably loaded by functions pointing to that address):\n')
		
			for address in explicit_address_array:
				f.write(str(hex(address)) + '\n')
		
		#bitshifted cmp function
		f.write('\nThe following are the hexadecimal addresses where the value ' + output_value_display + ' was found being checked for equality (<low nibble of high + high nibble of low> 0E 5X E3) or (high 0C 5X E3):\n')
        
		for address in cmp_explicit_array:
			f.write(str(hex(address)) + '\n')
			
		#regular cmp function (one byte) or sub followed by subs (two bytes)
		if(high_byte == 0):
			f.write('\nThe following are the hexadecimal addresses where the value ' + output_value_display + ' was found being checked for equality (low XX 5X E3):\n')
		else:
			f.write('\nThe following are the hexadecimal addresses where the value ' + output_value_display + ' was found being checked for equality (high XX 4X E2 low XX 5X):\n')
		
		for address in two_subtractions_array:
			f.write(str(hex(address)) + '\n')
			
multisearch()