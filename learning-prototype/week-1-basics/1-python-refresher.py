"""
Week 1, Day 1: Python Refresher for Machine Learning
=====================================================

This file reviews Python fundamentals you'll use throughout ML projects.
Complete the TODO sections to practice each concept.

Topics covered:
- Variables and data types
- Functions and lambda functions
- List comprehensions
- File I/O
- Classes and objects
- Error handling

Estimated time: 2-3 hours
"""

# =============================================================================
# SECTION 1: Variables and Data Types
# =============================================================================

print("=" * 60)
print("SECTION 1: Variables and Data Types")
print("=" * 60)

# Basic data types in Python
integer_num = 42
float_num = 3.14
string_text = "Machine Learning"
boolean_val = True
none_val = None

print(f"Integer: {integer_num}, Type: {type(integer_num)}")
print(f"Float: {float_num}, Type: {type(float_num)}")
print(f"String: {string_text}, Type: {type(string_text)}")
print(f"Boolean: {boolean_val}, Type: {type(boolean_val)}")
print(f"None: {none_val}, Type: {type(none_val)}")

# TODO: Create variables for a simple ML dataset
# Create a variable 'num_samples' with value 1000
# Create a variable 'num_features' with value 10
# Create a variable 'dataset_name' with value "Customer Data"
# Create a variable 'is_cleaned' with value False

# Your code here:
num_samples = None  # TODO: Replace None with 1000
num_features = None  # TODO: Replace None
dataset_name = None  # TODO: Replace None
is_cleaned = None  # TODO: Replace None

print(f"\nDataset: {dataset_name}, Samples: {num_samples}, Features: {num_features}, Cleaned: {is_cleaned}")

# =============================================================================
# SECTION 2: Lists and List Comprehensions
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 2: Lists and List Comprehensions")
print("=" * 60)

# Basic list operations
features = ["age", "income", "education", "experience"]
print(f"Features: {features}")
print(f"First feature: {features[0]}")
print(f"Last feature: {features[-1]}")
print(f"First two features: {features[:2]}")

# Adding items
features.append("skills")
print(f"After append: {features}")

# List comprehension - square numbers
numbers = [1, 2, 3, 4, 5]
squared = [x**2 for x in numbers]
print(f"\nNumbers: {numbers}")
print(f"Squared: {squared}")

# Filtered list comprehension - only even numbers
even_numbers = [x for x in numbers if x % 2 == 0]
print(f"Even numbers: {even_numbers}")

# TODO: Create a list of accuracy scores
# Create a list called 'scores' with values: 0.85, 0.92, 0.88, 0.95, 0.90

# Your code here:
scores = []  # TODO: Fill with accuracy scores

print(f"\nAccuracy scores: {scores}")

# TODO: Use list comprehension to convert scores to percentages
# Multiply each score by 100
# Store in variable 'percentages'

# Your code here:
percentages = []  # TODO: Use list comprehension

print(f"Percentages: {percentages}")

# EXERCISE: Filter scores above 0.90
# Create 'high_scores' with only scores > 0.90

# Your code here:
high_scores = []  # TODO: Filter scores

print(f"High scores: {high_scores}")

# =============================================================================
# SECTION 3: Dictionaries (Essential for ML)
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 3: Dictionaries")
print("=" * 60)

# Dictionaries store key-value pairs (like JSON)
model_config = {
    "model_type": "RandomForest",
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42
}

print(f"Model config: {model_config}")
print(f"Model type: {model_config['model_type']}")
print(f"Number of estimators: {model_config['n_estimators']}")

# Adding new key-value pair
model_config["min_samples_split"] = 2
print(f"\nUpdated config: {model_config}")

# Looping through dictionary
print("\nConfig parameters:")
for key, value in model_config.items():
    print(f"  {key}: {value}")

# TODO: Create a dictionary for model evaluation metrics
# Keys: "accuracy", "precision", "recall", "f1_score"
# Values: 0.92, 0.89, 0.94, 0.91

# Your code here:
metrics = {}  # TODO: Fill with metric values

print(f"\nModel metrics: {metrics}")

# EXERCISE: Add a new metric "roc_auc" with value 0.95
# Your code here:

print(f"Updated metrics: {metrics}")

# =============================================================================
# SECTION 4: Functions
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 4: Functions")
print("=" * 60)

# Basic function
def calculate_accuracy(correct, total):
    """Calculate accuracy as percentage of correct predictions."""
    if total == 0:
        return 0.0
    return (correct / total) * 100

# Test the function
acc = calculate_accuracy(95, 100)
print(f"Accuracy: {acc}%")

# Function with default parameters
def train_model(data, epochs=10, learning_rate=0.01):
    """Simulate model training (placeholder)."""
    print(f"Training with {epochs} epochs and LR={learning_rate}")
    return f"Model trained on {len(data)} samples"

# Test with defaults
result = train_model([1, 2, 3, 4, 5])
print(result)

# Test with custom parameters
result = train_model([1, 2, 3], epochs=20, learning_rate=0.001)
print(result)

# TODO: Write a function to calculate precision
# precision = true_positives / (true_positives + false_positives)
# Function should be named 'calculate_precision'
# Parameters: true_positives (int), false_positives (int)
# Return: precision as float

# Your code here:
def calculate_precision(true_positives, false_positives):
    """Calculate precision metric."""
    # TODO: Implement the calculation
    pass  # Remove this line when you add your code

# Test your function (uncomment when ready)
# prec = calculate_precision(80, 20)
# print(f"Precision: {prec:.2f}")

# EXERCISE: Write a function to calculate recall
# recall = true_positives / (true_positives + false_negatives)
# Your code here:

def calculate_recall(true_positives, false_negatives):
    """Calculate recall metric."""
    # TODO: Implement the calculation
    pass

# =============================================================================
# SECTION 5: Lambda Functions (One-liners)
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 5: Lambda Functions")
print("=" * 60)

# Lambda function - anonymous function
square = lambda x: x ** 2
print(f"Square of 5: {square(5)}")

# Using lambda with map
numbers = [1, 2, 3, 4, 5]
squared_map = list(map(lambda x: x ** 2, numbers))
print(f"Squared using map: {squared_map}")

# Using lambda with filter
even_filter = list(filter(lambda x: x % 2 == 0, numbers))
print(f"Even numbers using filter: {even_filter}")

# Sorting with lambda (sort by second element)
scores_data = [("model_A", 0.85), ("model_B", 0.92), ("model_C", 0.88)]
sorted_scores = sorted(scores_data, key=lambda x: x[1], reverse=True)
print(f"\nSorted models by score: {sorted_scores}")

# TODO: Create a lambda function that converts accuracy to percentage
# Name it 'to_percentage' and test with 0.95

# Your code here:
to_percentage = None  # TODO: Define lambda

# Uncomment to test:
# print(f"95% accuracy: {to_percentage(0.95)}")

# EXERCISE: Use map() and a lambda to round all scores to 2 decimal places
scores = [0.8532, 0.9187, 0.8845]
# Your code here:
rounded_scores = []  # TODO: Use map and lambda

print(f"Rounded scores: {rounded_scores}")

# =============================================================================
# SECTION 6: Classes and Objects
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 6: Classes and Objects")
print("=" * 60)

# Define a simple class for ML model
class MLModel:
    """A simple ML model class."""

    def __init__(self, name, model_type):
        """Initialize the model."""
        self.name = name
        self.model_type = model_type
        self.is_trained = False
        self.accuracy = 0.0

    def train(self, data):
        """Train the model (placeholder)."""
        print(f"Training {self.name}...")
        self.is_trained = True
        # Simulate training
        self.accuracy = 0.92
        return f"Model trained on {len(data)} samples"

    def predict(self, data):
        """Make predictions (placeholder)."""
        if not self.is_trained:
            return "Error: Model not trained yet!"
        return [0, 1, 0, 1]  # Dummy predictions

    def get_info(self):
        """Get model information."""
        return {
            "name": self.name,
            "type": self.model_type,
            "trained": self.is_trained,
            "accuracy": self.accuracy
        }

# Create model instance
model = MLModel("MyClassifier", "RandomForest")
print(f"Model info: {model.get_info()}")

# Train the model
model.train([1, 2, 3, 4, 5])
print(f"After training: {model.get_info()}")

# Make predictions
predictions = model.predict([6, 7, 8, 9])
print(f"Predictions: {predictions}")

# TODO: Create a class called 'Dataset'
# Attributes: name (string), num_samples (int), num_features (int)
# Methods: __init__, get_shape() which returns (num_samples, num_features)

# Your code here:
class Dataset:
    """Represents an ML dataset."""

    def __init__(self, name, num_samples, num_features):
        # TODO: Initialize attributes
        pass

    def get_shape(self):
        # TODO: Return tuple of (num_samples, num_features)
        pass

# Test your class (uncomment when ready):
# data = Dataset("CustomerData", 1000, 20)
# print(f"Dataset shape: {data.get_shape()}")

# =============================================================================
# SECTION 7: File I/O (Critical for Data Loading)
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 7: File I/O")
print("=" * 60)

# Writing to a file
data_to_save = ["age,income,purchased", "25,50000,1", "30,60000,1", "35,80000,0"]

# Write to CSV file
with open("sample_data.csv", "w") as f:
    for line in data_to_save:
        f.write(line + "\n")

print("✓ Data written to sample_data.csv")

# Reading from a file
with open("sample_data.csv", "r") as f:
    lines = f.readlines()
    print(f"✓ Read {len(lines)} lines from file")
    print("First line:", lines[0].strip())

# TODO: Read the file and count number of data rows (excluding header)
# Hint: Skip the first line, count the rest

# Your code here:
def count_data_rows(filename):
    """Count data rows in CSV file (excluding header)."""
    # TODO: Implement
    pass

# Uncomment to test:
# num_rows = count_data_rows("sample_data.csv")
# print(f"Number of data rows: {num_rows}")

# =============================================================================
# SECTION 8: Error Handling (Essential for Production Code)
# =============================================================================

print("\n" + "=" * 60)
print("SECTION 8: Error Handling")
print("=" * 60)

# Basic try-except
def safe_divide(a, b):
    """Safely divide two numbers."""
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("Error: Cannot divide by zero!")
        return None
    except TypeError:
        print("Error: Invalid input types!")
        return None

# Test error handling
print(f"10 / 2 = {safe_divide(10, 2)}")
print(f"10 / 0 = {safe_divide(10, 0)}")

# File handling with error checking
def load_config(filename):
    """Load configuration from file."""
    try:
        with open(filename, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found!")
        return None
    except PermissionError:
        print(f"Error: No permission to read '{filename}'!")
        return None

# Test file loading
config = load_config("config.txt")  # File doesn't exist

# TODO: Write a function that safely converts a string to int
# Should handle ValueError if string is not a valid number
# Return None on error, otherwise return the integer

# Your code here:
def safe_int_convert(value):
    """Safely convert string to integer."""
    # TODO: Implement with try-except
    pass

# Test cases (uncomment when ready):
# print(safe_int_convert("123"))   # Should return 123
# print(safe_int_convert("abc"))   # Should return None

# =============================================================================
# PRACTICE CHALLENGES
# =============================================================================

print("\n" + "=" * 60)
print("PRACTICE CHALLENGES")
print("=" * 60)

# CHALLENGE 1: Data Statistics Calculator
# Write a function that takes a list of numbers and returns a dictionary with:
# - "mean": average value
# - "min": minimum value
# - "max": maximum value
# - "count": number of values

def calculate_stats(numbers):
    """Calculate basic statistics for a list of numbers."""
    # TODO: Implement this function
    pass

# Test (uncomment when ready):
# data = [23, 45, 67, 12, 89, 34]
# stats = calculate_stats(data)
# print(f"Statistics: {stats}")

# CHALLENGE 2: CSV Parser
# Write a function that reads a CSV file and returns data as a list of dictionaries
# Each dictionary represents a row with column names as keys

def parse_csv(filename):
    """Parse CSV file into list of dictionaries."""
    # TODO: Implement this function
    # Hint: First line is header, use it for keys
    pass

# Test (uncomment when ready):
# data = parse_csv("sample_data.csv")
# print(f"Parsed data: {data}")

# CHALLENGE 3: Model Performance Tracker
# Create a class that tracks multiple model runs
# Should store: model_name, accuracy, timestamp
# Should have method to get best performing model

class ModelTracker:
    """Track performance of multiple model runs."""

    def __init__(self):
        # TODO: Initialize data structure to store runs
        pass

    def add_run(self, model_name, accuracy):
        # TODO: Add a new model run
        pass

    def get_best_model(self):
        # TODO: Return the model with highest accuracy
        pass

    def get_all_runs(self):
        # TODO: Return all recorded runs
        pass

# Test (uncomment when ready):
# tracker = ModelTracker()
# tracker.add_run("RandomForest", 0.92)
# tracker.add_run("LogisticRegression", 0.87)
# tracker.add_run("XGBoost", 0.95)
# print(f"Best model: {tracker.get_best_model()}")

# =============================================================================
# SUMMARY & NEXT STEPS
# =============================================================================

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

print("""
Congratulations! You've reviewed Python fundamentals for ML:

✓ Variables and data types
✓ Lists and list comprehensions
✓ Dictionaries for configuration
✓ Functions and lambdas
✓ Classes and objects
✓ File I/O operations
✓ Error handling

Next steps:
1. Complete all TODO exercises in this file
2. Attempt the CHALLENGE problems
3. Check your solutions against solutions/1-python-refresher-solution.py
4. Move on to 2-numpy-basics.py

Remember: Type out all code yourself for better learning!
""")

# Clean up the test file
import os
if os.path.exists("sample_data.csv"):
    os.remove("sample_data.csv")
    print("✓ Cleaned up test files")
