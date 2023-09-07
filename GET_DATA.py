import pandas as pd
import numpy as np
import os

import COLORS


class GetData:
    def __init__(self, dataset, filename):
        # store dataset into dataframe
        df = pd.read_csv(filename)

        # get dataset name
        dataset.name = os.path.basename(filename)

        # make even attributes
        if (len(df.columns) - 1) % 2 == 1:
            df['Dupe-x' + str(len(df.columns) - 1)] = df.iloc[:, len(df.columns) - 1]

        # put class column to end of dataframe
        df.insert(len(df.columns) - 1, 'class', df.pop('class'))

        # get class information
        dataset.class_count = len(df['class'].unique())
        dataset.class_names = df['class'].value_counts().index.tolist()
        dataset.count_per_class = df['class'].value_counts().tolist()
        dataset.class_order = np.arange(0, dataset.class_count)

        # initial colors (10 options)
        colors = COLORS.getColors()
        class_color_array = colors.colors_array

        cnt = 0  # counter for color array
        dataset.class_colors = []
        for i in range(dataset.class_count):
            # repeat colors for more than 9 classes, class colors can be changed interactively later
            if i % 9 == 0:
                cnt = 0
            # make all classes and markers initially active
            # add colors and update counter
            dataset.class_colors.append(class_color_array[cnt])
            cnt += 1
        dataset.active_markers = np.repeat(True, dataset.class_count)
        dataset.active_classes = np.repeat(True, dataset.class_count)

        # get attribute information
        dataset.attribute_names = df.columns.tolist()[:-1]
        dataset.attribute_count = len(df.columns) - 1
        dataset.attribute_order = np.arange(0, dataset.attribute_count)

        dataset.active_attributes = np.repeat(True, dataset.attribute_count)

        # get sample information
        dataset.sample_count = len(df.index)
        # initialize arrays for clipping options
        dataset.clipped_samples = np.repeat(False, dataset.sample_count)
        dataset.vertex_in = np.repeat(False, dataset.sample_count)
        dataset.last_vertex_in = np.repeat(False, dataset.sample_count)

        # general dataframe
        dataset.dataframe = df