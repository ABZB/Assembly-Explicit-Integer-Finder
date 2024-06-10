from tkinter.filedialog import askopenfilename, asksaveasfilename
import os

def check_two_bytes(offset_0, offset_2, offset_3, offset_4, offset_6, offset_7, high_byte, low_byte):
	#check to see if it is a two-step subtraction check
			
	#<high byte> <register> <4 | register> <E2> <low byte> <register> <5 | register> <E2>
	return(offset_0 == high_byte and offset_2 >> 4 == 4 and offset_3 == 0xE2 and offset_4 == low_byte and offset_6 >> 4 == 5 and offset_7 == 0xE2)

def check_one_byte(offset_0, offset_2, offset_3, low_byte):
	#<low_byte>, <unused>, <5 | register>, <EE3>
	return(offset_0 == low_byte and offset_2 >> 4 == 5 and offset_3 == 0xE3)

def print_percent_done(file_length, position):
	print(position/file_length)

def main():
	search_array = []
	
	#value we are searching for
	target_value = input('What is the base-10 value you are searching for? ')
	
	try:
		target_value = int(target_value)
	except:
		print(target_value, 'is not an integer, it is ', type(target_value))
		return
	
	#divide into the low and high bytes
	low_byte = target_value%256
	high_byte = target_value >> 8


	#print(low_byte, high_byte)


	#file we are looking in
	source_file = askopenfilename(title = 'Select binary file to search in')
	with open(source_file, "r+b") as f:
		f.seek(0, os.SEEK_END)
		file_end = f.tell()
		f.seek(0, 0)
		block = f.read(file_end)
		
		for ch in block:
			search_array.append(ch)

	explicit_address_array = []
	two_subtractions_array = []

	file_length = len(search_array)

	#version for 1 bytes
	if(high_byte == 0):
		for offset, value in enumerate(search_array):
			if(offset % 250000 == 0):
				print_percent_done(int(file_length), int(offset))
			if(offset + 7 >= file_length):
				print('End of file reached')
				break

			try:
				if(check_one_byte(search_array[offset + 0], search_array[offset + 2], search_array[offset + 3], low_byte)):
					two_subtractions_array.append(offset)
				#check to see if this matches as a regular little-endian integer
				elif(search_array[offset] == low_byte and search_array[offset + 1] == high_byte):
					explicit_address_array.append(offset)
			except:
				print('Error encountered at ', offset)
				break

	
	#version for 2 bytes
	else:
		for offset, value in enumerate(search_array):
			if(offset % 250000 == 0):
				print_percent_done(int(file_length), int(offset))
			
			if(offset + 7 >= file_length):
				print('End of file reached')
				break

			try:
				if(check_two_bytes(search_array[offset + 0], search_array[offset + 2], search_array[offset + 3], search_array[offset + 4], search_array[offset + 6], search_array[offset + 7], high_byte, low_byte)):
					two_subtractions_array.append(offset)
				elif(search_array[offset] == low_byte):
					explicit_address_array.append(offset)
			except:
				print('Error encountered at ', offset)
				break
	


	output_file_path = asksaveasfilename(title = 'Select text file to save output as', defaultextension = '.txt')
	
	output_value_display = ''
	
	if(high_byte == 0):
		output_value_display = hex(low_byte)
	else:
		output_value_display = hex(low_byte) + ' ' + hex(high_byte)
	

	with open(output_file_path, "w") as f:
		f.write('The following are the hexadecimal addresses where the value ' + output_value_display + ' was found:\n')
		
		for address in explicit_address_array:
			f.write(str(hex(address)) + '\n')
		
		if(high_byte == 0):
			f.write('\nThe following are the hexadecimal addresses where the value ', output_value_display, ' was found being checked for equality (low XX 5X E3):\n')
		else:
			f.write('\nThe following are the hexadecimal addresses where the value ' + output_value_display + ' was found being checked for equality (high XX 4X E2 low):\n')
		
		for address in two_subtractions_array:
			f.write(str(hex(address)) + '\n')
		
main()