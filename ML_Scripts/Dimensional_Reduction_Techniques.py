"""
This script will run dimensional reduction techniques on a dataset
Add column headers, fix missing values, and make sure class labels are in numeric form, before running models
Make sure there is only one class column, and the remaining columns are attributes you'd like to run in the model
"""

# import dimensional reduction techniques
from sklearn.manifold import TSNE
from sklearn.decomposition import TruncatedSVD, PCA
from sklearn.manifold import MDS

# import utilities
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# clear warnings
import warnings


def warn(*args, **kwargs):
    pass


warnings.warn = warn


# =====================================================
class DimensionalReduction:
    def __init__(self, dataset_name, class_column_name):
        self.dataset_name = dataset_name
        self.class_column_name = class_column_name

        self.labels = None
        self.data = None

    # csv to data and labels
    def get_data_and_labels(self):
        # read the dataset file
        data = pd.read_csv(self.dataset_name)

        # labels
        self.labels = data[self.class_column_name]

        data.drop([self.class_column_name], axis=1, inplace=True)
        self.data = data

    # =====================================================

    # run dimensional reduction
    def run_dim_reduction(self, model, num_of_comp):

        # run models
        if model == 'TSNE':  # t-distributed stochastic neighbor embedding
            # TSNE warning
            if num_of_comp >= 4:
                print('TSNE requires 1 to 3 components')
                return
            transformed_data = TSNE(n_components=num_of_comp).fit_transform(self.data)

        elif model == 'TSVD':  # truncated singular value decomposition
            transformed_data = TruncatedSVD(n_components=num_of_comp).fit_transform(self.data)

        elif model == 'PCA':  # principal component analysis
            transformed_data = PCA(n_components=num_of_comp).fit_transform(self.data)

        elif model == 'MDS':  # multidimensional scaling
            transformed_data = MDS(n_components=num_of_comp).fit_transform(self.data)

        else:
            transformed_data = None

        # create column names for components
        column_names = ['component_' + str(i+1) for i in range(num_of_comp)]

        # return components as dataframe
        output = pd.DataFrame(transformed_data[:], columns=column_names)
        output[self.class_column_name] = self.labels

        return output
    
    # =====================================================

    # add components to dataset passed to class
    def add_components_to_dataset(self, component_df):
        component_df.drop([self.class_column_name], axis=1, inplace=True)
        comp_names = component_df.columns.values.tolist()

        # add components
        self.data[comp_names] = component_df[:]

        # add class
        self.data['class'] = self.labels

        return self.data
    
    # =====================================================
    
    # make scatterplot
    def scatterplot_of_components(self, component_df, x, y):
        """
        custom palette for a lot of classes
        access the custom palette by changing my_palette variable to my_palette=colors
        add or remove colors from colors array if you have more classes
        """
        # colors = ['#0000FF', '#FF0000']
        my_palette = 'hls'

        # number of classes
        targets = len(component_df[self.class_column_name].unique())  # of classes

        # general plot info
        plt.figure(figsize=(10, 10))
        ax = sns.scatterplot(x, y, palette=sns.color_palette(palette=my_palette, n_colors=targets),
                             data=component_df, hue=self.labels, legend='full')
        ax.set_xlabel('Component 1', fontsize=16)
        ax.set_ylabel('Component 2', fontsize=16)
        plt.show()


# =====================================================


if __name__ == '__main__':
    dataset_name = 'LUPI_VEHICLE_ALL.csv'
    class_column_name = 'class'

    output_csv_name = 'CWU_TEST2.csv'

    # initiate class
    m = DimensionalReduction(dataset_name, class_column_name)

    # get data and labels
    m.get_data_and_labels()
    # technique and number of reduction components -> manually enter here
    dim_components = m.run_dim_reduction('TSNE', 2)

    # optional if you want to see components on scatterplot
    m.scatterplot_of_components(dim_components, 'component_1', 'component_2')

    # optional combine components with original dataset
    new_data = m.add_components_to_dataset(dim_components)

    print(new_data)
    new_data.to_csv(output_csv_name, index=False)

    """
    If you want to combine dimensional reduction techniques just initiate another class
    Example: MNIST 784 real attributes -> 50 PCA -> 2 TSNE
    
    a = DimensionalReduction('mnist.csv', 'class')
    a.get_data_and_labels()
    pca_comps = a.run_dim_reduction('PCA', 50)
    pca_comps.to_csv('PCA_comps.csv', index=False)
    
    b = DimensionalReduction('PCA_comps.csv', 'class')
    b.get_data_and_labels()
    tsne_comps = b.run_dim_reduction('TSNE',2)
    
    here you can call: 
    a.add_components_to_dataset(tsne_comps) --> tsne+original
    or b.add_components_to_dataset(tsne_comps) --> tsne+PCA
    """

