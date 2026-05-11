# Copyright 2026 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from typing import Any
import json


import futs
from sandbox import Sandbox
from llm import GeminiLLM


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/playground-series-s3e1")
ORIGINAL_TRAIN_PATH = os.path.join(DATA_DIR, "train.csv")

# Paths for our internal validation split
TRAIN_PATH = os.path.join(DATA_DIR, "local_train.csv")
TEST_PATH = os.path.join(DATA_DIR, "local_test.csv")
# We don't have a separate solution file, the target is in local_test.csv

def prepare_data():
    """Splits original train.csv into local train/test for validation."""
    print("Preparing local validation split...")
    df = pd.read_csv(ORIGINAL_TRAIN_PATH)
    
    # Simple 80/20 split
    train_size = int(0.8 * len(df))
    train_df = df.iloc[:train_size]
    test_df = df.iloc[train_size:]
    
    # Save local files
    train_df.to_csv(TRAIN_PATH, index=False)
    
    # For the test file passed to the model, we ideally shouldn't include the target
    # But standard kaggle test.csv doesn't have it.
    # Let's save the features to TEST_PATH and keep the targets for scoring.
    test_features = test_df.drop('MedHouseVal', axis=1)
    test_features.to_csv(TEST_PATH, index=False)
    
    return test_df['MedHouseVal'].values

# We read the data to provide context in the prompt
def get_data_head():
    df = pd.read_csv(TRAIN_PATH)
    return df.head().to_markdown()

class PlaygroundProblem(futs.Problem):
    pass

class PlaygroundGenerator:
    def __init__(self, llm: GeminiLLM):
        self.llm = llm

    def __call__(self, problem: futs.Problem, parent_solution: futs.Solution, parent_score: float) -> futs.Solution:
        data_preview = get_data_head()
        
        # Convert score back to positive RMSE for display
        rmse = -parent_score
        
        prompt = f"""
{problem.description}

Here is a preview of the training data:
{data_preview}

The goal is to predict 'MedHouseVal'. The metric is RMSE (Root Mean Squared Error).
Lower is better.

The previous solution had a score (RMSE) of: {rmse:.5f}
Previous Solution Code:
```python
{parent_solution.program}
```

Please generate a NEW, IMPROVED Python function named `train_and_predict` that:
1. Accepts `train_path` and `test_path` as strings.
2. Trains a regression model.
3. Returns the predictions for the test set as a numpy array or list.
4. You can use pandas, numpy, scikit-learn.

IMPORTANT: DO NOT use `xgboost` or `lightgbm`.

Your code must look like this:
```python
import pandas as pd
import numpy as np
# ... other imports

def train_and_predict(train_path, test_path):
    # Load data
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    
    # ... Feature Engineering ...
    # ... Training ...
    
    # Predict
    predictions = ... 
    return predictions
```
Provide the full, runnable code including imports.

IMPORTANT CONSTRAINTS FOR SPEED:
1. DO NOT use GridSearchCV or RandomizedSearchCV.
2. If using RandomForest or Boosting, set `n_estimators` to maximum 50.
3. Keep the model lightweight (execution time limit is 60 seconds).
"""
        code = self.llm.draw_sample(prompt)
        return futs.Solution(code)

class PlaygroundExecutor:
    def __init__(self, sandbox: Sandbox, y_true: np.ndarray):
        self.sandbox = sandbox
        self.y_true = y_true

    def __call__(self, problem: futs.Problem, solution: futs.Solution) -> float:
        # ... (setup code remains similar)
        
        # Read data on host (these are the LOCAL files now)
        with open(TRAIN_PATH, 'r') as f:
            train_csv = f.read()
        with open(TEST_PATH, 'r') as f:
            test_csv = f.read()
            
        # We'll inject a setup block into the program
        setup_code = f"""
import os
import tempfile
# Use a local temp dir that is likely to be writable
tmp_data_dir = os.path.join(tempfile.gettempdir(), 'futs_data')
os.makedirs(tmp_data_dir, exist_ok=True)
train_path = os.path.join(tmp_data_dir, 'train.csv')
test_path = os.path.join(tmp_data_dir, 'test.csv')

with open(train_path, 'w') as f:
    f.write({repr(train_csv)})
with open(test_path, 'w') as f:
    f.write({repr(test_csv)})
"""
        full_program = setup_code + "\n" + solution.program
        
        wrapper_code = """
def wrapper(unused_arg):
    return train_and_predict(train_path, test_path)
"""
        final_program = full_program + wrapper_code
        
        result, success = self.sandbox.run(final_program, "wrapper", None)
        
        if not success or result is None:
            print(f"Execution failed: {result}")
            return float('-inf') # Invalid solution
            
        # Result should be the predictions
        try:
            predictions = np.array(result)
            
            # Use stored true values
            y_true = self.y_true
            
            # Ensure predictions shape matches
            if len(predictions) != len(y_true):
                 print(f"Shape mismatch: {len(predictions)} vs {len(y_true)}")
                 return float('-inf')
            
            score = np.sqrt(mean_squared_error(y_true, predictions))
            return -score # FUTS maximizes score, so return negative RMSE
        except Exception as e:
            print(f"Scoring error: {e}")
            return float('-inf')

def run_experiment(iterations=10):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Set GEMINI_API_KEY")
        return

    # Prepare data first
    y_val = prepare_data()

    llm = GeminiLLM(api_key)
    sandbox = Sandbox(timeout_seconds=60) # Give it time to train
    
    problem = PlaygroundProblem("Improve the regression model for the California Housing dataset.")
    
    # Initial naive solution
    initial_code = """
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def train_and_predict(train_path, test_path):
    train = pd.read_csv(train_path)
    test = pd.read_csv(test_path)
    
    X = train.drop('MedHouseVal', axis=1)
    y = train['MedHouseVal']
    
    model = LinearRegression()
    model.fit(X, y)
    
    return model.predict(test)
"""
    initial_solution = futs.Solution(initial_code)
    
    # Evaluate initial
    executor = PlaygroundExecutor(sandbox, y_val)
    print("Evaluating initial solution...")
    initial_score = executor(problem, initial_solution)
    print(f"Initial Score (Neg RMSE): {initial_score}")
    
    generator = PlaygroundGenerator(llm)
    
    print("Starting Search...")
    
    # We need to hook into the search to track progress.
    # Since futs.search doesn't return history, we can wrap the execute_fn to record scores.
    history = []
    
    class TrackingExecutor:
        def __init__(self, inner_executor):
            self.inner = inner_executor
            self.best_so_far = float('-inf')
            self.iteration = 0
            
        def __call__(self, problem, solution):
            score = self.inner(problem, solution)
            self.iteration += 1
            if score > self.best_so_far:
                self.best_so_far = score
            history.append({"iteration": self.iteration, "best_score": self.best_so_far})
            return score

    tracking_executor = TrackingExecutor(executor)
    
    # Record initial state
    history.append({"iteration": 0, "best_score": initial_score})

    best_sol, best_score = futs.search(
        problem=problem,
        initial_solution=initial_solution,
        initial_score=initial_score,
        generate_fn=generator,
        execute_fn=tracking_executor, # Use wrapper
        num_iterations=iterations,
        c_puct=1.0 
    )
    
    # Save history
    output_dir = 'results'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'futs_progress.json')
    with open(output_path, 'w') as f:
        json.dump(history, f)
    print("\nProgress saved to futs_progress.json")
    
    print(f"\nBest Score: {best_score}")
    print("Best Code:")
    print(best_sol.program)

if __name__ == "__main__":
    run_experiment()
