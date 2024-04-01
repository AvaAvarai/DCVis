"""
This script will make a print out of a full decision tree
Add column headers and fix missing values before running models
Make sure there is only one class column, and the remaining columns are attributes you'd like to run in the model
"""

import os

# imports
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

    # build the tree
    def build_tree(self, output_filename):
        # uses CART DT algorithm
        clf = tree.DecisionTreeClassifier()
        clf.fit(self.data, self.labels)

        dot_data = tree.export_graphviz(clf, out_file=None)
        graph = graphviz.Source(dot_data)
        graph.render(output_filename)


if __name__ == '__main__':
    os.environ["PATH"] += os.pathsep + 'C:\Program Files\Graphviz/bin'
    dataset_name = 'iris_dataset.csv'
    class_column_name = 'class'

    output_filename = 'dt_graph'

    a = PrintDT(dataset_name, class_column_name)
    a.get_data_and_labels()
    a.build_tree(output_filename)
