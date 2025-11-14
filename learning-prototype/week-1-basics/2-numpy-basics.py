"""
Week 1, Day 2: NumPy Basics for Machine Learning
=================================================

NumPy is the foundation of ML in Python. You'll use it everywhere!

Topics covered:
- Array creation and basic operations
- Indexing and slicing
- Array manipulation (reshape, transpose)
- Mathematical operations
- Broadcasting
- Random number generation

Estimated time: 2-3 hours
"""

import numpy as np

# =============================================================================
# SECTION 1: Creating NumPy Arrays
# =============================================================================

print("=" * 60)
print("SECTION 1: Creating NumPy Arrays")
print("=" * 60)

# From Python lists
list_1d = [1, 2, 3, 4, 5]
arr_1d = np.array(list_1d)
print(f"1D array: {arr_1d}")
print(f"Type: {type(arr_1d)}")
print(f"Shape: {arr_1d.shape}")
print(f"Data type: {arr_1d.dtype}")

# 2D array (matrix)
list_2d = [[1, 2, 3], [4, 5, 6]]
arr_2d = np.array(list_2d)
print(f"\n2D array:\n{arr_2d}")
print(f"Shape: {arr_2d.shape}")  # (rows, columns)

# Special array creation functions
zeros = np.zeros((3, 4))  # 3x4 array of zeros
ones = np.ones((2, 3))    # 2x3 array of ones
full = np.full((2, 2), 7) # 2x2 array filled with 7
identity = np.eye(3)      # 3x3 identity matrix

print(f"\nZeros array:\n{zeros}")
print(f"\nOnes array:\n{ones}")
print(f"\nFull array:\n{full}")
print(f"\nIdentity matrix:\n{identity}")

# Range arrays
arange_arr = np.arange(0, 10, 2)  # Start, stop, step
linspace_arr = np.linspace(0, 1, 5)  # Start, stop, num_points

print(f"\nArange (0 to 10, step 2): {arange_arr}")
print(f"Linspace (0 to 1, 5 points): {linspace_arr}")

# TODO: Create a 1D array with numbers from 1 to 10
# Use np.arange()

# Your code here:
arr_1_to_10 = None  # TODO: Replace None

# Uncomment to test:
# print(f"\nArray 1-10: {arr_1_to_10}")

# TODO: Create a 2D array of zeros with shape (5, 3)

# Your code here:
zeros_5x3 = None  # TODO: Replace None

# Uncomment to test:
# print(f"\nZeros 5x3:\n{zeros_5x3}")

# EXERCISE: Create a 4x4 identity matrix
# Your code here:

# EXERCISE: Create an array of 10 evenly spaced numbers between 0 and 100
# Your code here:

# =============================================================================
# SECTION 2: Array Attributes
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 2: Array Attributes")
print("=" * 60)

sample_array = np.array([[1, 2, 3, 4],
                         [5, 6, 7, 8],
                         [9, 10, 11, 12]])

print(f"Array:\n{sample_array}")
print(f"\nShape (rows, cols): {sample_array.shape}")
print(f"Number of dimensions: {sample_array.ndim}")
print(f"Total elements: {sample_array.size}")
print(f"Data type: {sample_array.dtype}")
print(f"Item size (bytes): {sample_array.itemsize}")
print(f"Total bytes: {sample_array.nbytes}")

# TODO: Create a 3D array and print all its attributes
# Shape should be (2, 3, 4)
# Hint: Use np.zeros(), np.ones(), or np.arange().reshape()

# Your code here:
arr_3d = None  # TODO: Create 3D array

# Print attributes (uncomment when ready):
# print(f"\n3D Array shape: {arr_3d.shape}")
# print(f"Dimensions: {arr_3d.ndim}")
# print(f"Size: {arr_3d.size}")

# =============================================================================
# SECTION 3: Indexing and Slicing
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 3: Indexing and Slicing")
print("=" * 60)

arr = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

# Basic indexing
print(f"Array: {arr}")
print(f"First element: {arr[0]}")
print(f"Last element: {arr[-1]}")
print(f"Third element: {arr[2]}")

# Slicing [start:stop:step]
print(f"\nFirst 3 elements: {arr[:3]}")
print(f"Last 3 elements: {arr[-3:]}")
print(f"Every other element: {arr[::2]}")
print(f"Elements from index 2 to 6: {arr[2:7]}")

# 2D array indexing
arr_2d = np.array([[1, 2, 3, 4],
                   [5, 6, 7, 8],
                   [9, 10, 11, 12]])

print(f"\n2D Array:\n{arr_2d}")
print(f"Element at row 0, col 1: {arr_2d[0, 1]}")
print(f"Element at row 2, col 3: {arr_2d[2, 3]}")

# Row and column selection
print(f"\nFirst row: {arr_2d[0, :]}")  # or just arr_2d[0]
print(f"Second column: {arr_2d[:, 1]}")
print(f"First 2 rows, last 2 columns:\n{arr_2d[:2, -2:]}")

# Boolean indexing
arr = np.array([10, 25, 30, 15, 40])
mask = arr > 20  # Boolean array
print(f"\nArray: {arr}")
print(f"Mask (arr > 20): {mask}")
print(f"Elements > 20: {arr[mask]}")

# TODO: From arr_2d, get all elements in the last column

# Your code here:
last_col = None  # TODO: Extract last column

# Uncomment to test:
# print(f"\nLast column: {last_col}")

# TODO: From arr_2d, get middle 2 rows (rows 1-2)

# Your code here:
middle_rows = None  # TODO: Extract middle rows

# Uncomment to test:
# print(f"\nMiddle rows:\n{middle_rows}")

# EXERCISE: Create an array of numbers 1-20
# Use boolean indexing to get only even numbers
# Your code here:

# EXERCISE: From arr_2d, extract elements > 6
# Your code here:

# =============================================================================
# SECTION 4: Array Operations
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 4: Array Operations")
print("=" * 60)

a = np.array([1, 2, 3, 4])
b = np.array([5, 6, 7, 8])

# Element-wise operations
print(f"a: {a}")
print(f"b: {b}")
print(f"\na + b: {a + b}")
print(f"a - b: {a - b}")
print(f"a * b: {a * b}")  # Element-wise multiplication!
print(f"a / b: {a / b}")
print(f"a ** 2: {a ** 2}")

# Scalar operations (broadcasting)
print(f"\na * 10: {a * 10}")
print(f"a + 100: {a + 100}")

# Aggregation functions
data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
print(f"\nData: {data}")
print(f"Sum: {data.sum()}")
print(f"Mean: {data.mean()}")
print(f"Std: {data.std()}")
print(f"Min: {data.min()}")
print(f"Max: {data.max()}")
print(f"Median: {np.median(data)}")

# Axis-specific operations (2D)
arr_2d = np.array([[1, 2, 3],
                   [4, 5, 6],
                   [7, 8, 9]])

print(f"\n2D Array:\n{arr_2d}")
print(f"Sum of all elements: {arr_2d.sum()}")
print(f"Sum along axis 0 (columns): {arr_2d.sum(axis=0)}")
print(f"Sum along axis 1 (rows): {arr_2d.sum(axis=1)}")
print(f"Mean along axis 0: {arr_2d.mean(axis=0)}")

# TODO: Calculate the product of all elements in data array
# Hint: Use .prod()

# Your code here:
product = None  # TODO: Calculate product

# Uncomment to test:
# print(f"\nProduct of all elements: {product}")

# TODO: Calculate variance of data array
# Hint: Use .var()

# Your code here:
variance = None  # TODO: Calculate variance

# EXERCISE: Create a 3x3 array with random integers from 1 to 100
# Calculate min, max, and mean
# Your code here:

# =============================================================================
# SECTION 5: Reshaping Arrays
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 5: Reshaping Arrays")
print("=" * 60)

# Reshape - change dimensions without changing data
arr = np.arange(12)  # [0, 1, 2, ..., 11]
print(f"Original array: {arr}")
print(f"Shape: {arr.shape}")

reshaped = arr.reshape(3, 4)  # 3 rows, 4 columns
print(f"\nReshaped to 3x4:\n{reshaped}")

reshaped2 = arr.reshape(2, 6)  # 2 rows, 6 columns
print(f"\nReshaped to 2x6:\n{reshaped2}")

# Can use -1 to let NumPy figure out one dimension
reshaped3 = arr.reshape(4, -1)  # 4 rows, auto-calculate columns
print(f"\nReshaped to 4x? (auto):\n{reshaped3}")

# Flatten - convert to 1D
arr_2d = np.array([[1, 2, 3], [4, 5, 6]])
flattened = arr_2d.flatten()
print(f"\n2D Array:\n{arr_2d}")
print(f"Flattened: {flattened}")

# Transpose - swap rows and columns
arr = np.array([[1, 2, 3],
                [4, 5, 6]])
print(f"\nOriginal (2x3):\n{arr}")
print(f"Transposed (3x2):\n{arr.T}")

# TODO: Create an array [0, 1, 2, ..., 23]
# Reshape it to 4x6

# Your code here:
arr_24 = None  # TODO: Create array 0-23
arr_4x6 = None  # TODO: Reshape to 4x6

# Uncomment to test:
# print(f"\n4x6 array:\n{arr_4x6}")

# EXERCISE: Create a 2x3x4 array (any values)
# Reshape it to 6x4
# Your code here:

# EXERCISE: Create a 5x5 matrix, transpose it, verify shapes
# Your code here:

# =============================================================================
# SECTION 6: Broadcasting
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 6: Broadcasting")
print("=" * 60)

# Broadcasting allows operations on arrays of different shapes
arr = np.array([[1, 2, 3],
                [4, 5, 6],
                [7, 8, 9]])

# Add scalar (broadcasts to all elements)
result = arr + 10
print(f"Original:\n{arr}")
print(f"\nAfter adding 10:\n{result}")

# Add 1D array to each row
row_arr = np.array([10, 20, 30])
result = arr + row_arr  # row_arr broadcasts across rows
print(f"\nAdd [10, 20, 30] to each row:\n{result}")

# Add column vector
col_arr = np.array([[10], [20], [30]])  # 3x1 shape
result = arr + col_arr  # col_arr broadcasts across columns
print(f"\nAdd column [10, 20, 30]:\n{result}")

# TODO: Create a 3x3 array of ones
# Multiply each row by [1, 2, 3]
# Result should be: [[1, 2, 3], [1, 2, 3], [1, 2, 3]]

# Your code here:
ones_arr = None  # TODO: Create 3x3 ones
multiplier = None  # TODO: Create [1, 2, 3]
result = None  # TODO: Multiply with broadcasting

# Uncomment to test:
# print(f"\nBroadcast multiplication result:\n{result}")

# =============================================================================
# SECTION 7: Random Numbers (Important for ML)
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 7: Random Number Generation")
print("=" * 60)

# Set random seed for reproducibility
np.random.seed(42)

# Random float between 0 and 1
random_val = np.random.random()
print(f"Random float: {random_val}")

# Array of random floats
random_arr = np.random.random((3, 4))  # 3x4 array
print(f"\nRandom 3x4 array:\n{random_arr}")

# Random integers
random_ints = np.random.randint(1, 100, size=10)  # 10 integers between 1-100
print(f"\nRandom integers (1-100): {random_ints}")

# Normal distribution (mean=0, std=1)
normal_arr = np.random.randn(5)
print(f"\nNormal distribution: {normal_arr}")

# Normal distribution with custom mean and std
custom_normal = np.random.normal(loc=100, scale=15, size=10)  # mean=100, std=15
print(f"\nCustom normal (mean=100, std=15): {custom_normal}")

# Choice from array (sampling)
arr = np.array([1, 2, 3, 4, 5])
sample = np.random.choice(arr, size=3, replace=False)  # Sample 3 without replacement
print(f"\nRandom sample: {sample}")

# TODO: Generate a 5x5 matrix of random integers between 1 and 10
# Set seed to 42 first

# Your code here:
np.random.seed(42)
random_matrix = None  # TODO: Generate random matrix

# Uncomment to test:
# print(f"\nRandom 5x5 matrix:\n{random_matrix}")

# EXERCISE: Generate 1000 random numbers from normal distribution
# Calculate their mean and std (should be close to 0 and 1)
# Your code here:

# =============================================================================
# SECTION 8: Universal Functions (ufuncs)
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 8: Universal Functions")
print("=" * 60)

arr = np.array([1, 4, 9, 16, 25])

# Mathematical functions
print(f"Array: {arr}")
print(f"Square root: {np.sqrt(arr)}")
print(f"Exponential: {np.exp([1, 2, 3])}")
print(f"Logarithm: {np.log([1, 10, 100])}")

# Trigonometric functions
angles = np.array([0, np.pi/4, np.pi/2, np.pi])
print(f"\nAngles: {angles}")
print(f"Sine: {np.sin(angles)}")
print(f"Cosine: {np.cos(angles)}")

# Rounding
arr = np.array([1.234, 2.567, 3.891])
print(f"\nArray: {arr}")
print(f"Round: {np.round(arr, 2)}")
print(f"Floor: {np.floor(arr)}")
print(f"Ceil: {np.ceil(arr)}")

# Element-wise maximum/minimum
a = np.array([1, 5, 3, 7])
b = np.array([2, 4, 6, 2])
print(f"\na: {a}")
print(f"b: {b}")
print(f"Element-wise max: {np.maximum(a, b)}")
print(f"Element-wise min: {np.minimum(a, b)}")

# TODO: Create an array of negative and positive numbers
# Use np.abs() to get absolute values

# Your code here:
numbers = np.array([-5, 3, -2, 7, -9])  # Example array
abs_values = None  # TODO: Apply absolute value

# Uncomment to test:
# print(f"\nAbsolute values: {abs_values}")

# =============================================================================
# SECTION 9: Linear Algebra (Essential for ML)
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 9: Linear Algebra")
print("=" * 60)

# Dot product
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])
dot_product = np.dot(a, b)  # 1*4 + 2*5 + 3*6 = 32
print(f"a: {a}")
print(f"b: {b}")
print(f"Dot product: {dot_product}")

# Matrix multiplication
A = np.array([[1, 2],
              [3, 4]])
B = np.array([[5, 6],
              [7, 8]])

result = np.dot(A, B)  # or A @ B
print(f"\nMatrix A:\n{A}")
print(f"\nMatrix B:\n{B}")
print(f"\nA × B:\n{result}")

# Matrix transpose
print(f"\nA transpose:\n{A.T}")

# Inverse (if exists)
try:
    A_inv = np.linalg.inv(A)
    print(f"\nA inverse:\n{A_inv}")
    print(f"\nA × A_inv (should be identity):\n{np.dot(A, A_inv)}")
except:
    print("Matrix is singular (no inverse)")

# Determinant
det = np.linalg.det(A)
print(f"\nDeterminant of A: {det}")

# Eigenvalues and eigenvectors
eigenvalues, eigenvectors = np.linalg.eig(A)
print(f"\nEigenvalues: {eigenvalues}")
print(f"Eigenvectors:\n{eigenvectors}")

# TODO: Create two matrices and multiply them
# Matrix C: 2x3, Matrix D: 3x2
# Result should be 2x2

# Your code here:
C = None  # TODO: Create 2x3 matrix
D = None  # TODO: Create 3x2 matrix
result = None  # TODO: Multiply C and D

# Uncomment to test:
# print(f"\nC × D:\n{result}")

# =============================================================================
# PRACTICE CHALLENGES
# =============================================================================

print("\n" + "=" * 60)
print("PRACTICE CHALLENGES")
print("=" * 60)

# CHALLENGE 1: Normalize Data
# Create a function that normalizes data to 0 mean and 1 std
# Formula: (x - mean) / std

def normalize_data(data):
    """Normalize data to have mean=0 and std=1."""
    # TODO: Implement normalization
    pass

# Test (uncomment when ready):
# data = np.random.randint(1, 100, size=20)
# normalized = normalize_data(data)
# print(f"Original mean: {data.mean():.2f}, std: {data.std():.2f}")
# print(f"Normalized mean: {normalized.mean():.2f}, std: {normalized.std():.2f}")

# CHALLENGE 2: Create Checkerboard Pattern
# Create an 8x8 checkerboard pattern (0s and 1s)
# Should look like a chess board

def create_checkerboard(size=8):
    """Create a checkerboard pattern."""
    # TODO: Implement
    # Hint: Use slicing or mathematical operations
    pass

# Test (uncomment when ready):
# board = create_checkerboard(8)
# print(f"\nCheckerboard:\n{board}")

# CHALLENGE 3: Moving Average
# Implement a function that calculates moving average
# moving_avg([1,2,3,4,5], window=3) -> [2, 3, 4]

def moving_average(data, window):
    """Calculate moving average with given window size."""
    # TODO: Implement
    pass

# Test (uncomment when ready):
# data = np.array([10, 20, 30, 40, 50, 60, 70])
# avg = moving_average(data, window=3)
# print(f"Moving average: {avg}")

# CHALLENGE 4: Correlation Matrix
# Calculate correlation between columns of a 2D array

def correlation_matrix(data):
    """Calculate correlation matrix for columns."""
    # TODO: Implement
    # Hint: Use np.corrcoef() or implement manually
    pass

# Test (uncomment when ready):
# data = np.random.randn(100, 3)  # 100 samples, 3 features
# corr = correlation_matrix(data)
# print(f"Correlation matrix:\n{corr}")

# =============================================================================
# SUMMARY & NEXT STEPS
# =============================================================================

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print("""
Great job! You've learned NumPy fundamentals:

✓ Array creation and basic operations
✓ Indexing, slicing, and boolean indexing
✓ Reshaping and transposing
✓ Mathematical operations
✓ Broadcasting
✓ Random number generation
✓ Linear algebra operations

Next steps:
1. Complete all TODO exercises
2. Attempt the CHALLENGE problems
3. Check solutions in solutions/2-numpy-basics-solution.py
4. Move on to 3-pandas-intro.py

NumPy is the foundation - practice until you're comfortable!
""")
