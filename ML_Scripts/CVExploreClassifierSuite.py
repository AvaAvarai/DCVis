import pandas as pd
import numpy as np
import sys
import os
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
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from sklearn.ensemble import GradientBoostingClassifier, AdaBoostClassifier, ExtraTreesClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import RidgeClassifier
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, RocCurveDisplay
from sklearn.preprocessing import label_binarize
from itertools import cycle
from sklearn.metrics import roc_auc_score
import os
import datetime

warnings.filterwarnings("ignore")

models = {
    'DT': DecisionTreeClassifier,       # Decision Tree
    'RF': RandomForestClassifier,       # Random Forest
    'XT': ExtraTreesClassifier,         # Extra Trees
    'KNN': KNeighborsClassifier,        # K-Nearest Neighbors
    'SVM': SVC,                         # Support Vector Machine
    'LDA': LinearDiscriminantAnalysis,  # Linear Discriminant Analysis
    'LR': LogisticRegression,           # Logistic Regression
    'Ridge': RidgeClassifier,           # Ridge Classifier
    'NB': GaussianNB,                   # Gaussian Naive Bayes
    'MLP': MLPClassifier,               # Multi-layer Perceptron
    'SGD': SGDClassifier,               # Stochastic Gradient Descent
    'GB': GradientBoostingClassifier,   # Gradient Boosting
    'AB': AdaBoostClassifier,           # AdaBoost
    'XB': XGBClassifier                 # XGBoost
}

models_needing_probability = {'SVM'}


class TrainValidateModels:
    def __init__(self, transformed_dataset, original_dataset, class_column_name, n_runs, n_folds):
        self.transformed_dataset = transformed_dataset
        self.original_dataset = original_dataset
        self.class_column_name = class_column_name
        self.n_runs = n_runs
        self.n_folds = n_folds

    def plot_roc_curves(self, y_test, y_score, n_classes, target_names, output_dir):
        # Binarize the output labels for multi-class plotting
        y_test = label_binarize(y_test, classes=np.arange(n_classes))

        # Compute ROC curve and ROC area for each class
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        for i in range(n_classes):
            fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])

        # Aggregate all false positive rates
        all_fpr = np.unique(np.concatenate([fpr[i] for i in range(n_classes)]))

        # Then interpolate all ROC curves at these points
        mean_tpr = np.zeros_like(all_fpr)
        for i in range(n_classes):
            mean_tpr += np.interp(all_fpr, fpr[i], tpr[i])

        # Average it and compute AUC
        mean_tpr /= n_classes

        fpr["macro"] = all_fpr
        tpr["macro"] = mean_tpr
        roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])

        # Compute micro-average ROC curve and ROC area
        fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_score.ravel())
        roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])

        # Plot
        fig, ax = plt.subplots(figsize=(6, 6))
        plt.plot(fpr["micro"], tpr["micro"],
                label=f"Micro-average ROC curve (AUC = {roc_auc['micro']:.2f})",
                color="deeppink", linestyle=":", linewidth=4)
        plt.plot(fpr["macro"], tpr["macro"],
                label=f"Macro-average ROC curve (AUC = {roc_auc['macro']:.2f})",
                color="navy", linestyle=":", linewidth=4)

        colors = cycle(["aqua", "darkorange", "cornflowerblue"])
        for i, color in zip(range(n_classes), colors):
            plt.plot(fpr[i], tpr[i], color=color, lw=2,
                    label=f'ROC curve for {target_names[i]} (AUC = {roc_auc[i]:.2f})')

        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Extension of Receiver Operating Characteristic to Multi-class')
        plt.legend(loc="lower right")

        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the plot
        output_path = os.path.join(output_dir, f"roc_curves.png")
        plt.savefig(output_path)
        plt.close()


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

        X_train = np.asarray(X_train)
        y_train = np.asarray(y_train)
        X_val = np.asarray(X_val)
        y_val = np.asarray(y_val)

        return X_train, y_train, X_val, y_val
            
    def analyze_roc(self, roc_data, y_val):
        n_classes = len(np.unique(y_val))
        auc_values = {}
        best_worst_indices = {}

        for name, data in roc_data.items():
            auc_scores = []
            for (y_val_run, y_proba_run) in data:
                if y_proba_run is not None:
                    roc_auc = roc_auc_score(y_val_run, y_proba_run, multi_class="ovr")
                    auc_scores.append(roc_auc)
                else:
                    auc_scores.append(float('-inf'))  # Ignore runs without ROC capability

            if auc_scores:
                best_index = np.argmax(auc_scores)
                worst_index = np.argmin(auc_scores)
                best_worst_indices[name] = (best_index, worst_index, max(auc_scores), min(auc_scores))
                auc_values[name] = (max(auc_scores), min(auc_scores))

        auc_df = pd.DataFrame.from_dict(auc_values, orient='index', columns=['Best AUC', 'Worst AUC'])
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        auc_df.to_csv(f'./roc_auc_values_{timestamp}.csv')

        for name, (best_index, worst_index, _, _) in best_worst_indices.items():
            target_names = [f'Class {i}' for i in range(n_classes)]
            y_val_best, y_proba_best = roc_data[name][best_index]
            y_val_worst, y_proba_worst = roc_data[name][worst_index]
            if y_proba_best is not None and y_proba_worst is not None:
                self.save_roc_plot(y_val_best, y_proba_best, n_classes, target_names, name, 'best')
                self.save_roc_plot(y_val_worst, y_proba_worst, n_classes, target_names, name, 'worst')

        return auc_df

    def save_roc_plot(self, y_test, y_score, n_classes, target_names, model_name, label):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            output_dir = f"./roc_plots/{timestamp}"
            os.makedirs(output_dir, exist_ok=True)
            
            y_test = label_binarize(y_test, classes=np.arange(n_classes))
            fpr, tpr, roc_auc = {}, {}, {}
            for i in range(n_classes):
                fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
                roc_auc[i] = auc(fpr[i], tpr[i])
            
            fig, ax = plt.subplots(figsize=(10, 8))
            colors = cycle(["aqua", "darkorange", "cornflowerblue"])
            for i, color in zip(range(n_classes), colors):
                plt.plot(fpr[i], tpr[i], color=color, lw=2, label=f'Class {i} (AUC = {roc_auc[i]:.2f})')

            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title(f'{model_name} ROC Curve ({label})')
            plt.legend(loc="lower right")
            output_path = os.path.join(output_dir, f"{model_name}_{label}_roc.png")
            plt.savefig(output_path)
            plt.close()
        except Exception as e:
            print(f"Failed to save plot: {e}")


    def model_fit_predict(self, name, model, X_train, y_train, X_val, y_val, skf):
        # Fit the model and predict the validation set
        cv_scores = cross_val_score(model, X_train, y_train, cv=skf, scoring='accuracy')
        model.fit(X_train, y_train)  # Refit on the entire training set
        y_pred = model.predict(X_val)  # Predict on the validation set
        val_accuracy = accuracy_score(y_val, y_pred)

        # Check if the model supports probability prediction or decision function
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_val)
        elif hasattr(model, "decision_function"):
            y_scores = model.decision_function(X_val)
            y_proba = np.exp(y_scores) / np.sum(np.exp(y_scores), axis=1, keepdims=True)
        else:
            y_proba = None  # Not available for ROC plotting

        return name, np.mean(cv_scores), val_accuracy, y_proba

    def run_models(self, X_train, y_train, X_val, y_val):
        all_results = {name: [] for name in models.keys()}
        roc_data = {}
        skf = StratifiedKFold(n_splits=self.n_folds, shuffle=True, random_state=42)

        with ProcessPoolExecutor() as executor:
            futures = []
            for _ in range(1, self.n_runs + 1):
                for name, model_cls in models.items():
                    model = model_cls(probability=True) if name in models_needing_probability else model_cls()
                    future = executor.submit(self.model_fit_predict, name, model, X_train, y_train, X_val, y_val, skf)
                    futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                name, cv_score, val_accuracy, y_proba = future.result()
                all_results[name].append((cv_score, val_accuracy))
                if name not in roc_data:
                    roc_data[name] = []
                roc_data[name].append((y_val, y_proba))

        # Capture the AUC DataFrame
        auc_df = self.analyze_roc(roc_data, y_val)

        # Pass the AUC DataFrame to print_results
        self.print_results(all_results, auc_df)

        return all_results

    def print_results(self, results, auc_df):
        plural = 's' if self.n_runs > 1 else ''
        print("\n==============================================================================================")
        print(f"Model Performance over {self.n_runs} independent cycle{plural} with {self.n_folds}-Fold Cross-Validation")
        print(f"Training Dataset: {self.transformed_dataset} Exploration Dataset: {self.original_dataset}")
        print("==============================================================================================")

        headers = ['Model', 'CV Mean Acc.', 'CV STD of Acc.', 'Exp. Mean Acc.', 'Exp. STD of Acc.', 'Best AUC', 'Worst AUC']
        print("{:<8}{:<15}{:<15}{:<15}{:<15}{:<10}{:<10}".format(*headers))

        for model, stats in results.items():
            cv_mean_acc = np.mean([score[0] for score in stats])
            cv_std_acc = np.std([score[0] for score in stats])
            val_mean_acc = np.mean([score[1] for score in stats])
            val_std_acc = np.std([score[1] for score in stats])
            best_auc, worst_auc = auc_df.loc[model]
            print(f"{model:<8}{cv_mean_acc:<15.2f}{cv_std_acc:<15.2f}{val_mean_acc:<15.2f}{val_std_acc:<15.2f}{best_auc:<10.2f}{worst_auc:<10.2f}")
        print("==============================================================================================\n")

    def format_percentage(self, value):
        if np.isclose(value, 0):
            return '0%'
        else:
            formatted = f"{value * 100:.2f}".rstrip('0').rstrip('.')
            return formatted[:-1] + '%' if formatted.endswith('.') else formatted + '%'

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
    # Extracting the filenames without paths and extensions to use in the output file name
    transformed_dataset_base = transformed_dataset.split('\\')[-1].split('.')[0]
    original_dataset_base = original_dataset.split('\\')[-1].split('.')[0]

    # Directory where the results will be saved
    results_dir = f'train_datasets/{transformed_dataset_base}_validate_datasets/{original_dataset_base}'
    # Check if the directory exists, if not, create it
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # Define the full path for the results csv
    results_file_path = os.path.join(results_dir, f'{n_runs}_{n_folds}_results.csv')
    results_df.to_csv(results_file_path)

    print(f'Results saved to {results_file_path}')
