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
from sklearn.calibration import CalibratedClassifierCV
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

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

# Define sigmoid function for binary case
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Classifier Explorer")
        self.geometry("800x350")  # Increased height to accommodate the new labels
        
        # Center the window on the screen
        self.center_window()
        
        self.transformed_dataset = ""
        self.original_dataset = ""
        self.class_column_name = ""
        self.n_runs = 0
        self.n_folds = 0
        
        self.create_widgets()
        
        # Bind the Escape key to close the window
        self.bind("<Escape>", lambda event: self.destroy())
        
    def center_window(self):
        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate the position coordinates to center the window
        x = (screen_width - self.winfo_reqwidth()) / 2
        y = (screen_height - self.winfo_reqheight()) / 2
        
        # Set the window position
        self.geometry("+%d+%d" % (x, y))
        
    def create_widgets(self):
        self.label = tk.Label(self, text="Select datasets and parameters:")
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        self.transformed_button = tk.Button(self, text="Select Transformed Dataset", command=self.select_transformed_dataset)
        self.transformed_button.grid(row=1, column=0, padx=(50, 10), pady=5)  # Adjusted padx to create space between buttons

        self.original_button = tk.Button(self, text="Select Original Dataset", command=self.select_original_dataset)
        self.original_button.grid(row=1, column=1, padx=(10, 50), pady=5)  # Adjusted padx to create space between buttons

        # Label for class column name entry
        self.class_label = tk.Label(self, text="Class Column Name:")
        self.class_label.grid(row=2, column=0, pady=5)

        # Text entry for class column name
        self.class_entry = tk.Entry(self, width=10, font=("Helvetica", 10))
        self.class_entry.insert(0, "class")
        self.class_entry.grid(row=2, column=1, pady=5)

        self.runs_label = tk.Label(self, text="Number of Runs:")
        self.runs_label.grid(row=3, column=0, pady=5)
        self.runs_spinbox = tk.Spinbox(self, from_=1, to=999, increment=1, width=10)
        self.runs_spinbox.delete(0, "end")
        self.runs_spinbox.insert(0, 10)
        self.runs_spinbox.grid(row=3, column=1, pady=5)

        self.folds_label = tk.Label(self, text="Number of Folds:")
        self.folds_label.grid(row=4, column=0, pady=5)
        self.folds_spinbox = tk.Spinbox(self, from_=2, to=999, increment=1, width=10)
        self.folds_spinbox.delete(0, "end")
        self.folds_spinbox.insert(0, 10)
        self.folds_spinbox.grid(row=4, column=1, pady=5)

        self.transformed_label = tk.Label(self, text="Transformed Dataset:")
        self.transformed_label.grid(row=5, column=0, pady=5)
        self.transformed_name = tk.Label(self, text="")
        self.transformed_name.grid(row=5, column=1, pady=5)

        self.original_label = tk.Label(self, text="Original Dataset:")
        self.original_label.grid(row=6, column=0, pady=5)
        self.original_name = tk.Label(self, text="")
        self.original_name.grid(row=6, column=1, pady=5)

        self.run_button = tk.Button(self, text="Run", command=self.run_model)
        self.run_button.grid(row=7, column=0, columnspan=2, pady=10)  # Spanning two columns

    def select_transformed_dataset(self):
        self.transformed_dataset = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        self.transformed_name.config(text=self.transformed_dataset)

    def select_original_dataset(self):
        self.original_dataset = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        self.original_name.config(text=self.original_dataset)

    def run_model(self):
        try:
            self.class_column_name = self.class_entry.get()  # Retrieve the class label entered by the user
            self.n_runs = int(self.runs_spinbox.get())  # Corrected to use runs_spinbox
            self.n_folds = int(self.folds_spinbox.get())  # Corrected to use folds_spinbox

            if not self.transformed_dataset or not self.original_dataset or not self.class_column_name or not self.n_runs or not self.n_folds:
                messagebox.showerror("Error", "Please fill in all fields.")
                return

            # Now you can call your model runner with the provided inputs
            model_runner = TrainValidateModels(self.transformed_dataset, self.original_dataset, self.class_column_name, self.n_runs, self.n_folds)
            X_train, y_train, X_val, y_val = model_runner.prepare_data()
            results = model_runner.run_models(X_train, y_train, X_val, y_val)

            # Convert results to DataFrame and save
            results_df = pd.DataFrame(results).T
            # Extracting the filenames without paths and extensions to use in the output file name
            transformed_dataset_base = self.transformed_dataset.split('/')[-1].split('.')[0]
            original_dataset_base = self.original_dataset.split('/')[-1].split('.')[0]

            # Directory where the results will be saved
            results_dir = f'train_datasets/{transformed_dataset_base}_validate_datasets/{original_dataset_base}'
            # Check if the directory exists, if not, create it
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)

            # Define the full path for the results csv
            results_file_path = os.path.join(results_dir, f'{self.n_runs}_{self.n_folds}_results.csv')
            results_df.to_csv(results_file_path)

            messagebox.showinfo("Success", f"Results saved to {results_file_path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

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
                    if n_classes == 2 and y_proba_run.ndim == 2 and y_proba_run.shape[1] == 2:
                        # For binary classification, use the probabilities for the positive class (second column)
                        roc_auc = roc_auc_score(y_val_run, y_proba_run[:, 1])
                    elif n_classes > 2:
                        # For multiclass classification, use One-vs-Rest (OvR) strategy if applicable
                        roc_auc = roc_auc_score(y_val_run, y_proba_run, multi_class="ovr")
                    else:
                        # For other unexpected cases
                        roc_auc = roc_auc_score(y_val_run, y_proba_run)
                    auc_scores.append(roc_auc)
                else:
                    auc_scores.append(float('-inf'))  # Ignore runs without ROC capability

            if auc_scores:
                best_index = np.argmax(auc_scores)
                worst_index = np.argmin(auc_scores)
                best_worst_indices[name] = (best_index, worst_index, max(auc_scores), min(auc_scores))
                auc_values[name] = (max(auc_scores), min(auc_scores))

        auc_df = pd.DataFrame.from_dict(auc_values, orient='index', columns=['Best AUC', 'Worst AUC'])
        auc_df.to_csv(f'./roc_auc_values_{datetime.datetime.now().strftime("%Y%m%d_%H%M")}.csv')
        return auc_df

    def save_roc_plot(self, y_test, y_proba, n_classes, target_names, model_name, label):
        try:
            # Ensure y_proba is at least 2D
            if y_proba.ndim == 1:
                y_proba = y_proba.reshape(-1, 1)

            output_dir = f"./roc_plots/{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Plotting setup
            fig, ax = plt.subplots(figsize=(10, 8))
            colors = cycle(["aqua", "darkorange", "cornflowerblue"])

            if n_classes == 2 and y_proba.shape[1] == 1:
                # Binary classification with single probability array
                fpr, tpr, _ = roc_curve(y_test, y_proba[:, 0])
                roc_auc = auc(fpr, tpr)
                plt.plot(fpr, tpr, color=next(colors), lw=2,
                        label=f'{target_names[1]} (AUC = {roc_auc:.2f})')  # Class 1 is typically the positive class
            else:
                # Multiclass or binary with separate probabilities
                for i in range(n_classes):
                    fpr, tpr, _ = roc_curve(y_test[:, i], y_proba[:, i])
                    roc_auc = auc(fpr, tpr)
                    plt.plot(fpr, tpr, color=next(colors), lw=2,
                            label=f'{target_names[i]} (AUC = {roc_auc:.2f})')

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
            # Convert decision function scores to probabilities
            if name in ['Ridge', 'SGD']:  # These classifiers need calibration
                # Use CalibratedClassifierCV if not calibrated
                model = CalibratedClassifierCV(model, method='sigmoid', cv=5)
                model.fit(X_train, y_train)
                y_proba = model.predict_proba(X_val)
            else:
                y_proba = sigmoid(y_scores)  # Sigmoid for binary classification
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
        print(f"Training Dataset: {self.transformed_dataset}")
        print(f"Exploration Dataset: {self.original_dataset}")
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

if __name__ == "__main__":
    app = GUI()
    app.mainloop()
