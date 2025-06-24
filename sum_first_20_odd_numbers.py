# Code a function that will take the sum of the first 20 odd numbers in an array.

def sum_first_20_odd(arr_numbers):
    odd_numbers = [num for num in arr_numbers if num % 2 != 0]
    if len(odd_numbers) < 20:
        print(f"(Warning: odd numbers in array is less than 20, adding all available odd numbers)\n")
    else: 
        print(f"(Total odd numbers is equal or more than 20)\n")
    return odd_numbers, len(odd_numbers), sum(odd_numbers[:20])


# arr = [3, 4, 7, 10, 15, 18, 21, 23, 25, 27, 30, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 60, 63, 67, 80, 88, 91, 93]
arr = [3, 4, 7, 10, 15, 18, 21, 23, 25, 27, 30, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51]
extracted_off_numbers, num_odd_numbers, sum_result = sum_first_20_odd(arr)

print(f"odd numbers are: {extracted_off_numbers}")
print(f"Total odd numbers in the array: {num_odd_numbers}")
print(f"Sum of first 20 odd numbers: {sum_result}")