import pandas as pd
import numpy as np
import sys
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import LabelEncoder
import warnings

warnings.filterwarnings("ignore")

class BasicModelsCV:
    def __init__(self, filename, class_column_name, n_folds):
        self.filename = filename
        self.class_column_name = class_column_name
        self.n_folds = n_folds
        self.data = None
        self.X = None
        self.y = None

    def prepare_data(self):
        # Load the dataset
        self.data = pd.read_csv(self.filename)
        
        # Encode class labels if they're not numeric
        le = LabelEncoder()
        self.data[self.class_column_name] = le.fit_transform(self.data[self.class_column_name])

        # Split data into features and target
        self.X = self.data.drop([self.class_column_name], axis=1)
        self.y = self.data[self.class_column_name]

    def run_cv(self):
        # Define the models to test
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

        # Define n-fold stratified cross-validation
        skf = StratifiedKFold(n_splits=self.n_folds, shuffle=True, random_state=42)

        # Dictionary to store results
        results = {}

        # Run cross-validation for each model
        for name, model in models.items():
            cv_scores = cross_val_score(model, self.X, self.y, cv=skf, scoring='accuracy')
            results[name] = np.mean(cv_scores)
            print(f"{name} Accuracy: {results[name]:.2f}")

        return results

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python script.py <filename.csv> <class_column_name> <n_folds>")
        sys.exit()

    filename = sys.argv[1]
    class_column_name = sys.argv[2]
    n_folds = int(sys.argv[3])  # Convert the command-line argument to an integer

    bm = BasicModelsCV(filename, class_column_name, n_folds)
    bm.prepare_data()
    results = bm.run_cv()

    # Optionally, save results to a CSV
    pd.DataFrame.from_dict(results, orient='index', columns=['Accuracy']).to_csv('cross_val_results.csv')
