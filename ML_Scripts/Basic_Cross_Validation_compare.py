import pandas as pd
import numpy as np
import sys
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import warnings

warnings.filterwarnings("ignore")

# Define your models here
models = {
    'Decision Tree': DecisionTreeClassifier(),
    'SVM': SVC(),
    'Random Forest': RandomForestClassifier(),
    'KNN': KNeighborsClassifier(),
    'Logistic Regression': LogisticRegression(),
    'Naive Bayes': GaussianNB(),
    'MLP': MLPClassifier(),
    'SGD': SGDClassifier(),
    'Linear Discriminant Analysis': LinearDiscriminantAnalysis(),
}

class TrainValidateModels:
    def __init__(self, transformed_dataset, original_dataset, class_column_name, n_runs, n_folds):
        self.transformed_dataset = transformed_dataset
        self.original_dataset = original_dataset
        self.class_column_name = class_column_name
        self.n_runs = n_runs
        self.n_folds = n_folds

    def prepare_data(self):
        # Load datasets
        transformed_df = pd.read_csv(self.transformed_dataset)
        original_df = pd.read_csv(self.original_dataset)

        # Encode class labels
        le = LabelEncoder()
        transformed_df[self.class_column_name] = le.fit_transform(transformed_df[self.class_column_name])
        original_df[self.class_column_name] = le.transform(original_df[self.class_column_name])

        # Split into features and target for both datasets
        X_train = transformed_df.drop(self.class_column_name, axis=1)
        y_train = transformed_df[self.class_column_name]
        X_val = original_df.drop(self.class_column_name, axis=1)
        y_val = original_df[self.class_column_name]

        return X_train, y_train, X_val, y_val

    def run_models(self, X_train, y_train, X_val, y_val):
        all_results = {name: [] for name in models.keys()}
        skf = StratifiedKFold(n_splits=self.n_folds, shuffle=True, random_state=42)

        for _ in range(self.n_runs):
            for name, model in models.items():
                # Perform cross-validation
                cv_scores = cross_val_score(model, X_train, y_train, cv=skf, scoring='accuracy')
                model.fit(X_train, y_train)  # Refit on the entire training set
                y_pred = model.predict(X_val)  # Predict on the validation set
                val_accuracy = accuracy_score(y_val, y_pred)
                all_results[name].append((np.mean(cv_scores), val_accuracy))

        final_results = {
            name: {'CV Mean Accuracy': np.mean([score[0] for score in acc]),
                   'CV STD of Accuracy': np.std([score[0] for score in acc]),
                   'Validation Accuracy': np.mean([score[1] for score in acc])}
            for name, acc in all_results.items()
        }

        # Print the results
        print("\nModel Performance over {} Runs:".format(self.n_runs))
        print("===================================")
        for model, stats in final_results.items():
            print(f"{model}: CV Mean Accuracy = {stats['CV Mean Accuracy']:.4f}, CV STD of Accuracy = {stats['CV STD of Accuracy']:.4f}, Validation Accuracy = {stats['Validation Accuracy']:.4f}")
        print("===================================")
        
        return final_results

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Usage: python script.py <transformed_dataset.csv> <original_dataset.csv> <class_column_name> <n_runs> <n_folds>")
        sys.exit()

    transformed_dataset = sys.argv[1]
    original_dataset = sys.argv[2]
    class_column_name = sys.argv[3]
    n_runs = int(sys.argv[4])
    n_folds = int(sys.argv[5])

    model_runner = TrainValidateModels(transformed_dataset, original_dataset, class_column_name, n_runs, n_folds)
    X_train, y_train, X_val, y_val = model_runner.prepare_data()
    results = model_runner.run_models(X_train, y_train, X_val, y_val)

    # Convert results to DataFrame and save
    results_df = pd.DataFrame(results).T
    results_df.to_csv('model_validation_results_with_cv_stats.csv')
