import pandas as pd
import numpy as np

# Define the number of cases
num_cases = 250

# Function to generate scores between 70 and 100
def generate_scores():
    # Choose scores only from 70 to 100 to simulate achieving grade 'C' or better
    scores = np.random.choice(range(70, 101), size=6)
    return scores

# Generate data for each course
courses = ['CS110', 'CS111', 'CS301', 'CS302', 'CS311', 'CS361']
data = {course: [] for course in courses}

for _ in range(num_cases):
    scores = generate_scores()
    for i, course in enumerate(courses):
        data[course].append(scores[i])

# Create a DataFrame
df = pd.DataFrame(data)

# Function to calculate letter grade based on average score
def calculate_grade(score):
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    else:
        return 'D'  # This case won't actually occur with the current setup

# Calculate the average score for each student and assign letter grades
average_scores = df.mean(axis=1)
df['class'] = average_scores.apply(calculate_grade)

# Save to CSV with headers
df.to_csv('.\datasets\synthetic_grades_250', index=False)
