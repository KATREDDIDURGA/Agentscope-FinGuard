# create_dummy_model.py
import pickle
import os
from sklearn.linear_model import LogisticRegression
import numpy as np

# Define the path where the model will be saved
# Get the absolute path to the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Assume 'models' directory is a sibling of 'app' directory, directly in the project root
PROJECT_ROOT = script_dir # If create_dummy_model.py is in the root
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "fraud_model.pkl")

# Ensure the models directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

def create_dummy_model():
    """
    Creates a simple dummy Logistic Regression model and saves it.
    This model will predict based on dummy features.
    """
    print("Creating a dummy fraud detection model...")
    print(f"Script directory: {script_dir}")
    print(f"Target model directory: {MODEL_DIR}")
    print(f"Target model path: {MODEL_PATH}")

    # Create dummy data for training
    X = np.array([
        [100, 0, 0, 0],
        [5000, 1, 0, 1],
        [200, 0, 1, 0],
        [1000, 0, 0, 1],
        [50, 0, 0, 0],
        [4000, 1, 1, 1],
        [150, 0, 0, 0],
        [3500, 1, 0, 0]
    ])
    y = np.array([0, 1, 1, 0, 0, 1, 0, 1])

    # Train a simple Logistic Regression model
    model = LogisticRegression(random_state=42)
    model.fit(X, y)

    # Save the trained model
    try:
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        print(f"Dummy fraud_model.pkl created successfully at: {MODEL_PATH}")
    except Exception as e:
        print(f"ERROR: Failed to save model to {MODEL_PATH}. Reason: {e}")
        print("Please check directory permissions.")

if __name__ == "__main__":
    create_dummy_model()
