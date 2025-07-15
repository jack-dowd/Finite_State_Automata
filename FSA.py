import multiprocessing as mp
import time
import argparse
import math
import random

class Matrix:
    def __init__(self, rows, cols, num_processes):
        # main array for cells
        #   use list for serial execution
        #   use mp.RawArray for parallel execution (mp.RawArray seems a bit faster than mp.Array)
        self.array = mp.RawArray('u', rows*cols) if(num_processes > 1) else ['']*(rows*cols)
        # neighbor sums array
        #   use list for serial execution
        #   use mp.RawArray for parallel execution (mp.RawArray seems a bit faster than mp.Array)
        self.sums = mp.RawArray('i', rows*cols) if(num_processes > 1) else [0]*(rows*cols)
        # rows and cols values for convenience
        self.rows = rows
        self.cols = cols
        
def printMatrix(matrix):
    for i in range(matrix.rows):
        for j in range(matrix.cols):
            print(matrix.array[i*matrix.cols + j], end='')
        # next line
        print()

# [unused] set the cell to alive ('O')
def setAliveCell(matrix, row, col):
    matrix.array[row*matrix.cols + col] = 'O'
    
# [unused] set the cell to dead ('.')
def setDeadCell(matrix, row, col):
    matrix.array[row*matrix.cols + col] = '.'

# find whether the value is prime or not
def isPrime(n):
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n))+1):
        if n % i == 0:
            return False
    return True

# return the sum of alive neighbor cells for a certain cell
def getNeighborSum(matrix, row, col):
    arr = [0]*8
    n = 0
    for i in range(row-1, row+2):
        for j in range(col-1, col+2):
            if(i == row and j == col):
                continue
            new_i = i
            new_j = j
            if(new_i < 0 or new_i >= matrix.rows):
                new_i = new_i % matrix.rows
            if(new_j < 0 or new_j >= matrix.cols):
                new_j = new_j % matrix.cols
            if(matrix.array[new_i*matrix.cols + new_j] == 'O'):
                arr[n] = 1
            n += 1
    return sum(arr)

# fill the neighbor sums array for a range of rows
def getNeighborSumsRange(matrix, start_row, end_row):
    for i in range(start_row, end_row):
        for j in range(matrix.cols):
            matrix.sums[i*matrix.cols + j] = getNeighborSum(matrix, i, j)

# fill the neighbor sums array for serial execution (1 process)
def getNeighborSumsSerial(matrix):
    getNeighborSumsRange(matrix, 0, matrix.rows)

# fill the neighbor sums array using multiple processes
def getNeighborSumsParallel(matrix, num_processes):
    # get rows per process
    num_rows_per_process = int(matrix.rows / num_processes)
    # start each process
    processes = []
    for i in range(num_processes):
        # assign row range to current process
        start_row = i * num_rows_per_process
        end_row = (i+1) * num_rows_per_process
        if(i == num_processes-1):
            end_row = matrix.rows
        # start current process
        current = mp.Process(target=getNeighborSumsRange, args=(matrix, start_row, end_row))
        current.start()
        processes.append(current)
    # join processes
    for i in range(num_processes):
        processes[i].join()

# update cells for a range of rows, used for updateParallel()
def updateRange(matrix, start_row, end_row):
    for i in range(start_row, end_row):
        for j in range(matrix.cols):
            cellChar = matrix.array[i*matrix.cols + j]
            neighborSum = matrix.sums[i*matrix.cols + j]
            # if alive
            if(cellChar == 'O'):
                if(isPrime(neighborSum) == False):
                    matrix.array[i*matrix.cols + j] = '.'
            # if dead
            elif(cellChar == '.'):
                if(neighborSum != 0 and neighborSum % 2 == 0):
                    matrix.array[i*matrix.cols + j] = 'O'

# update cells for serial execution (1 process)
def updateSerial(matrix):
    updateRange(matrix, 0, matrix.rows)

# update matrix using multiple processes
def updateParallel(matrix, num_processes):
    # get rows per process
    num_rows_per_process = int(matrix.rows / num_processes)
    # start each process
    processes = []
    for i in range(num_processes):
        # assign row range to current process
        start_row = i * num_rows_per_process
        end_row = (i+1) * num_rows_per_process
        if(i == num_processes-1):
            end_row = matrix.rows
        # start current process
        current = mp.Process(target=updateRange, args=(matrix, start_row, end_row))
        current.start()
        processes.append(current)
    # join processes
    for i in range(num_processes):
        processes[i].join()    

# return the number of rows of the input file
def getRows(file_name):
    rows = 0
    with open(file_name, 'r', newline='\n') as file:
        for row in file:
            if(row.endswith('\n')):
                rows += 1
    return rows

# return the number of columns of the input file
def getCols(file_name):
    cols = 0
    with open(file_name, 'r', newline='\n') as file:
        while True:
            char = file.read(1)
            if(char == '\n'):
                break
            cols += 1
    return cols

# [unused] generate random dead/alive char
def getRandomCell():
    return random.choice(['.', 'O'])

# fill matrix with input file data
def fillMatrix(matrix, file_name):
    with open(file_name, 'r', newline='\n') as file:
        i = 0
        len = matrix.rows*matrix.cols
        while True:
            char = file.read(1)
            if(char == '\n'):
                continue
            matrix.array[i] = char
            i += 1
            if(i >= len):
                break

# create output file
def generateOutputFile(matrix, file_name):
    with open(file_name, 'w', newline='\n') as file:
        for i in range(matrix.rows):
            for j in range(matrix.cols):
                file.write(matrix.array[i*matrix.cols + j])
            file.write('\n')

def main():   
    # get start time
    #start_time = time.time_ns()
    
    # print R number
    print("Project :: R11690912")
    
    # arg parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_file', type=str, required=True)
    parser.add_argument('-o', '--output_file', type=str, required=True)
    parser.add_argument('-p', '--num_processes', type=int, default=1)
    
    # get args
    args = parser.parse_args()
    input_file = args.input_file
    output_file = args.output_file
    num_processes = args.num_processes
    
    # raise error if num_processes is not a positive integer
    if(num_processes <= 0):
        raise ValueError("num_processes must be greater than 0.")
        
    # get rows and columns
    rows = getRows(input_file)
    cols = getCols(input_file)
    #print(rows, cols)
    
    # create matrix (iteration 0)
    matrix = Matrix(rows, cols, num_processes)
    fillMatrix(matrix, input_file)

    # print time step 0
    print()
    print("time_step_0")
    printMatrix(matrix)
    
    # iterations 1 to 100
    # if serial
    if(num_processes == 1):
        for i in range(100):
            getNeighborSumsSerial(matrix)
            updateSerial(matrix)
            print()
            print(f"time_step_{i+1}")
            printMatrix(matrix)
    # if parallel
    elif(num_processes > 1):
        for i in range(100):
            getNeighborSumsParallel(matrix, num_processes)
            updateParallel(matrix, num_processes)
            print()
            print(f"time_step_{i+1}")
            printMatrix(matrix)
            
    # generate output file (iteration 100)
    generateOutputFile(matrix, output_file)
    
    # get total run time
    #end_time = time.time_ns()
    #total_time = (end_time - start_time) / 1000000000
    #print(total_time)

if __name__ == '__main__':
    try:
        main()
    except ValueError as e:
        print("Error:", e)
