from typing import List, Optional, Tuple
import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler

import COLORS

class Dataset:
    def __init__(self):
        # dataset info
        self.name: str = ''
        self.dataframe: Optional[pd.DataFrame] = None

        # class information
        self.class_count: int = 0
        self.count_per_class: List[int] = []
        self.class_names: List[str] = []
        self.class_colors: List[Tuple[int, int, int]] = []  # RGB colors

        # attribute information
        self.attribute_count: int = 0
        self.attribute_names: List[str] = []
        self.attribute_alpha: int = 255  # for attribute slider
        
        self.attribute_inversions: List[bool] = []  # for attribute inversion option

        # sample information
        self.sample_count: int = 0
        self.clipped_samples: np.ndarray = np.array([], dtype=float)  # for line clip option
        self.vertex_in: np.ndarray = np.array([], dtype=float)  # for vertex clip option
        self.last_vertex_in: np.ndarray = np.array([], dtype=float)  # for last vertex clip option
        
        # plot information
        self.plot_type: str = ''
        self.positions: List[float] = []
        self.axis_positions: List[float] = []
        self.axis_on: bool = True
        self.axis_count: int = 0
        self.vertex_count: int = 0  # number of vertices depends on plot type

        self.active_attributes: np.ndarray = np.array([], dtype=bool)  # show/hide markers by attribute
        self.active_classes: List[bool] = []  # show/hide classes
        self.active_markers: List[bool] = []  # show/hide markers by class

        self.class_order: List[int] = []  # choose which class is on top
        self.attribute_order: List[int] = []  # choose attribute order (requires running graph construction algorithm again)

    def load_from_csv(self, filename: str):
        try:
            df = pd.read_csv(filename)

            # get dataset name
            self.name = os.path.basename(filename)

            # make even attributes
            if (len(df.columns) - 1) % 2 == 1:
                df['Dupe-x' + str(len(df.columns) - 1)] = df.iloc[:, len(df.columns) - 1]

            # put class column to end of dataframe
            df.insert(len(df.columns) - 1, 'class', df.pop('class'))

            # get class information
            self.class_count = len(df['class'].unique())
            self.class_names = df['class'].value_counts().index.tolist()
            self.count_per_class = df['class'].value_counts().tolist()
            self.class_order = np.arange(0, self.class_count)

            # get class colors
            self.class_colors = COLORS.getColors(self.class_count, [0, 0, 0, 1], [1, 1, 1, 1]).colors_array
            
            # initialize arrays for class options
            self.active_markers = np.repeat(True, self.class_count)
            self.active_classes = np.repeat(True, self.class_count)

            # get attribute information
            self.attribute_names = df.columns.tolist()[:-1]
            self.attribute_count = len(df.columns) - 1
            self.attribute_order = np.arange(0, self.attribute_count)

            self.active_attributes = np.repeat(True, self.attribute_count)
            self.attribute_inversions = np.repeat(False, self.attribute_count)

            # get sample information
            self.sample_count = len(df.index)
            # initialize arrays for clipping options
            self.clipped_samples = np.repeat(False, self.sample_count)
            self.vertex_in = np.repeat(False, self.sample_count)
            self.last_vertex_in = np.repeat(False, self.sample_count)

            # general dataframe
            self.dataframe = df
        except FileNotFoundError:
            print(f"File {filename} not found.")
            # Notify the controller to show a warning message
        except pd.errors.EmptyDataError:
            print("The file is empty.")
            # Notify the controller to show a warning message
        except Exception as e:
            print(f"An error occurred: {e}")
            # Notify the controller to show a warning message
    
    def normalize_data(self, range: Tuple[float, float]):
        scaler = MinMaxScaler(range)
        self.dataframe[self.attribute_names] = scaler.fit_transform(self.dataframe[self.attribute_names])
        return self.dataframe
    
    def normalize_col(self, col: int, range: Tuple[float, float]):
        scaler = MinMaxScaler(range)
        self.dataframe[self.attribute_names[col]] = scaler.fit_transform(self.dataframe[[self.attribute_names[col]]])
        return self.dataframe
