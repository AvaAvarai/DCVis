# Print_DT.py is a script that builds and prints a decision tree from a dataset.

import os
import argparse
from pathlib import Path
from sklearn import tree
import pandas as pd
import graphviz


class PrintDT:
    def __init__(self, dataset_name, class_column_name):
        self.dataset_name = dataset_name
        self.class_column_name = class_column_name

        self.labels = None
        self.data = None

    # csv to data and labels
    def get_data_and_labels(self):
        data = pd.read_csv(self.dataset_name)

        # change class names to numerical and use as labels
        targets = data[self.class_column_name].unique()
        map_to_int = {name: n for n, name in enumerate(targets)}
        self.labels = data[self.class_column_name].replace(map_to_int)

        data.drop([self.class_column_name], axis=1, inplace=True)

        # optional scale the data
        # scaler = MinMaxScaler((0, 1))
        # data[:] = scaler.fit_transform(data[:])

        # get data
        self.data = data

    def build_tree(self, base_output_filename):
        clf = tree.DecisionTreeClassifier()
        clf.fit(self.data, self.labels)

        # Extract the base name of the dataset for inclusion in the output filename
        dataset_base_name = Path(self.dataset_name).stem

        # Create a unique output filename by appending the dataset name
        output_filename = f"{base_output_filename}_{dataset_base_name}"

        dot_data = tree.export_graphviz(clf, out_file=None)
        graph = graphviz.Source(dot_data)
        
        # Check if the output file already exists. If it does, append a numeric suffix.
        counter = 1
        final_output_filename = output_filename
        while os.path.exists(f"{final_output_filename}.pdf"):
            final_output_filename = f"{output_filename}_{counter}"
            counter += 1

        # Render the graph, saving the file with the final, unique filename
        graph.render(final_output_filename, cleanup=True)  # cleanup=True to remove intermediary files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Build and print a decision tree from a dataset.")
    parser.add_argument("dataset_name", help="Path to the dataset file (CSV format).")
    parser.add_argument("class_column_name", help="The name of the class column in the dataset.")
    args = parser.parse_args()

    os.environ["PATH"] += os.pathsep + 'C:\Program Files\Graphviz/bin'
    base_output_filename = 'dt_graph'

    a = PrintDT(args.dataset_name, args.class_column_name)
    a.get_data_and_labels()
    a.build_tree(base_output_filename)
