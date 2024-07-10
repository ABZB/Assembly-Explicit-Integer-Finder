from tkinter.filedialog import askopenfilename, asksaveasfilename
import os

def check_two_bytes(offset_0, offset_2, offset_3, offset_4, offset_6, offset_7, high_byte, low_byte):
	#check to see if it is a two-step subtraction check
	#<high byte> <register> <4 | register> <E2> <low byte> <register> <5 | register> <E2>

	return(offset_0 == high_byte and offset_2 >> 4 == 4 and offset_3 == 0xE2 and offset_4 == low_byte and offset_6 >> 4 == 5 and offset_7 == 0xE2)

def check_one_byte(offset_0, offset_2, offset_3, low_byte):
	#<low_byte>, <unused>, <5 | register>, <EE3>
	return(offset_0 == low_byte and offset_2 >> 4 == 5 and offset_3 == 0xE3)

#bitshifted cmp
def check_two_byte_cmp(offset_0, offset_1, offset_2, offset_3, half_nibble_shift, bitshifted_value):

	return(offset_0 == bitshifted_value and offset_1 == (16 - half_nibble_shift) and (offset_2 >> 4) == 5 and offset_3 == 0xE3)

#returns the number of 0 bits at start and end of byte
def zero_bits_at_ends_of_byte(input_value: int):
	
	if(0 <= input_value <= 255):
		temp = bin(input_value)
	else:
		print('Error, input was not a byte, it was', input_value)
		return
	
	start_flag = True
	
	low_zero_count = 0
	high_zero_count = 0

	#bin() has 0b at start of string
	adjusted_length = len(temp) - 2
	
	for x in range(adjusted_length):
		
		#move from least to greatest bit
		z = temp[-1 - x]
		
		if(start_flag):
			if(z in {0,'0'}):
				low_zero_count += 1
			else:
				start_flag = False
		else:
			if(z in {0,'0'}):
				high_zero_count += 1
			else:
				high_zero_count = 0
				
	#if higher bits are not present, we have that many extra bits on the high side
	if(adjusted_length < 8):
		high_zero_count += 8 - (adjusted_length)

	return(high_zero_count, low_zero_count)
	
def check_bitshiftability(target_value, high_byte, low_byte):
	#count the number of 0 bits at the start and end. We have 16 bits total. If we have an even number of 0 bits on either side, and the total number of end-zero bits is at least 8, we can bitshift
	high_bits_of_high, low_bits_of_high = zero_bits_at_ends_of_byte(high_byte)
	high_bits_of_low, low_bits_of_low = zero_bits_at_ends_of_byte(low_byte)

	#see if we can shift rand end up with 1 byte - so the number of zero low bits of the low byte plus high bits of high is at least a byte's worth
	#so if we have k free bits on the right, we create instruction by moving k//2 half-nibbles to the right
	#to recover the value, need to shift k//2 to the left, which is 16 - k//2 to the right, because it circles around modulo 16
	#so the instruction second byte will be 0<16 - half_nibble_shift>
	if(low_bits_of_low + high_bits_of_high >= 8):
		half_nibble_shift = low_bits_of_low//2
		bitshifted_value = target_value >> (half_nibble_shift*2)
	else:
		bitshifted_value = 0
		half_nibble_shift = 0
		
	print(bitshifted_value, hex(bitshifted_value))
	

	return(bitshifted_value, half_nibble_shift)

def print_percent_done(file_length, position):
	print(position/file_length)

def search_binary_file_two_bytes(target_value = -1, source_file = '', output_file_path = '', mode = -1):
	search_array = []
	
	if(target_value == -1):
		#value we are searching for
		target_value = input('What is the base-10 value you are searching for? ')
	
		#file we are looking in
		source_file = askopenfilename(title = 'Select binary file to search in')
	
	try:
		target_value = int(target_value)
	except:
		print(target_value, 'is not an integer, it is ', type(target_value))
		return
	
	
	explicit_address_array = []
	two_subtractions_array = []
	
	#divide into the low and high bytes
	low_byte = target_value % 256
	high_byte = target_value >> 8
	
	#print(low_byte, high_byte)
	
	bitshifted_value = 0
	half_nibble_shift = 0
	cmp_explicit_array = []
	


    #if we are dealing with a two-byte target that only has two non-zero bytes, and they are contiguous (e.g. 0x0BC0 or 0xAB00) we can also see a single-line cmp function that uses a bitshift
	if(high_byte != 0):
		bitshifted_value, half_nibble_shift = check_bitshiftability(target_value, high_byte, low_byte)

	with open(source_file, "r+b") as f:
		f.seek(0, os.SEEK_END)
		file_end = f.tell()
		f.seek(0, 0)
		block = f.read(file_end)
		
		for ch in block:
			search_array.append(ch)
        
    
    
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
				elif(search_array[offset] == low_byte):
					explicit_address_array.append(offset)
				elif(search_array[offset] == low_byte and search_array[offset + 1] == high_byte):
					explicit_address_array.append(offset)
			except:
				print('Error encountered at ', offset, ' 1-byte mode')
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
                #checks for sub followed by subs using the integer one byte at a time
				if(check_two_bytes(search_array[offset + 0], search_array[offset + 2], search_array[offset + 3], search_array[offset + 4], search_array[offset + 6], search_array[offset + 7], high_byte, low_byte)):
					two_subtractions_array.append(offset)
                #checks for the integer written out in little-endian explicitly
				elif(search_array[offset + 0] == low_byte and search_array[offset + 1] == high_byte):
					explicit_address_array.append(offset)
                
                #checks for cmp being used for two bytes at once
				elif(half_nibble_shift != 0):
					if(check_two_byte_cmp(search_array[offset + 0], search_array[offset + 1], search_array[offset + 2], search_array[offset + 3], half_nibble_shift, bitshifted_value)):
						cmp_explicit_array.append(offset)
			except:
				print('Error encountered at ', offset, ' 2-byte mode')
				return
	
	if(not mode in {1, 2}):
		if(output_file_path == ''):
			output_file_path = asksaveasfilename(title = 'Select text file to save output as', defaultextension = '.txt')
	
		output_value_display = ''
	
		if(high_byte == 0):
			output_value_display = hex(low_byte)
		else:
			output_value_display = hex(low_byte) + ' ' + hex(high_byte)
	

		with open(output_file_path, "w") as f:
		
			#explicitly written and loaded by functions
			f.write('The following are the hexadecimal addresses where the value ' + output_value_display + ' was found (written explicitly in little-Endian, presumably loaded by functions pointing to that address):\n')
		
			for address in explicit_address_array:
				f.write(str(hex(address)) + '\n')
		
			#bitshifted cmp function
			if(half_nibble_shift != 0):
				f.write('\nThe following are the hexadecimal addresses where the value ' + output_value_display + ' was found being checked for equality (', bitshifted_value, ' 0' + hex(16 - half_nibble_shift)[-1] + ' 5X E3):\n')
        
			for address in cmp_explicit_array:
				f.write(str(hex(address)) + '\n')
			
			#regular cmp function (one byte) or sub followed by subs (two bytes)
			if(high_byte == 0):
				f.write('\nThe following are the hexadecimal addresses where the value ' + output_value_display + ' was found being checked for equality (low XX 5X E3):\n')
			else:
				f.write('\nThe following are the hexadecimal addresses where the value ' + output_value_display + ' was found being checked for equality (high XX 4X E2 low XX 5X):\n')
		
			for address in two_subtractions_array:
				f.write(str(hex(address)) + '\n')
	
	return(explicit_address_array, cmp_explicit_array, two_subtractions_array)


def main():
	search_binary_file_two_bytes()

if __name__ == '__main__':
	main()