
convert problem into questions
add tables for performance_data (using student_id, problem_id, score, update_at, create_at)
change: read from csv to read from database
add: columns questions (id, category, grade)
seed data: for questions

import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split

# Load data
performance_data = pd.read_csv('performance.csv')  # Ensure this CSV has columns: student_id, problem_id, score

# Define a reader
reader = Reader(rating_scale=(0, 100))

# Load the dataset
data = Dataset.load_from_df(performance_data[['student_id', 'problem_id', 'score']], reader)

# Split the dataset into training and testing
trainset, testset = train_test_split(data, test_size=0.25)

# Use SVD for collaborative filtering
algo = SVD()
algo.fit(trainset)

# Function to get recommendations
def get_recommendations(student_id, category, grade, n_recommendations=5):
    # Filter problems by category and grade
    problems = pd.read_csv('problems.csv')  # Ensure this CSV has columns: problem_id, category, grade
    filtered_problems = problems[(problems['category'] == category) & (problems['grade'] == grade)]
    
    # Predict scores for the filtered problems
    predictions = []
    for problem_id in filtered_problems['problem_id']:
        predictions.append((problem_id, algo.predict(student_id, problem_id).est))
    
    # Sort by predicted score and return top N recommendations
    recommendations = sorted(predictions, key=lambda x: x[1], reverse=True)[:n_recommendations]
    return [problem_id for problem_id, _ in recommendations]

# Example usage
student_id = 1
category = 'geometry'
grade = 10
recommendations = get_recommendations(student_id, category, grade)
print(f"Recommended problems for student {student_id}: {recommendations}")