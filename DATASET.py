from typing import List, Optional, Tuple
import WARNINGS
import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler

import COLORS


class Dataset:
    def __init__(self):
        # dataset info
        self.name: str = ''
        self.filepath: str = ''
        
        self.dataframe: Optional[pd.DataFrame] = None

        self.not_normalized_frame: Optional[pd.DataFrame] = None

        # class information
        self.class_count: int = 0
        self.count_per_class: List[int] = []
        self.class_names: List[str] = []
        self.class_colors: List[Tuple[int, int, int, int]] = []  # RGB colors TODO: change to using RGBA for individualized attribute alpha slider control

        self.rule_regions = {}

        # attribute information
        self.attribute_count: int = 0
        self.attribute_names: List[str] = []
        self.attribute_alpha: int = 255  # for attribute slider

        self.attribute_inversions: List[bool] = []  # for attribute inversion option
        self.overlap_points = {}

        # sample information
        self.sample_count: int = 0
        self.clipped_samples: np.ndarray = np.array([], dtype=float)  # for line clip option
        self.clear_samples: np.ndarray = np.array([], dtype=float)
        self.vertex_in: np.ndarray = np.array([], dtype=float)  # for vertex clip option
        self.last_vertex_in: np.ndarray = np.array([], dtype=float)  # for last vertex clip option

        # plot information
        self.plot_type: str = ''
        self.positions: List[float] = []
        
        self.overlap_indices = []
        self.radial_bounds = {}
        
        self.axis_positions: List[float] = []
        self.axis_on: bool = True
        self.axis_count: int = 0
        self.vertex_count: int = 0

        self.trace_mode: bool = False

        self.coefs = []

        self.active_attributes: np.ndarray = np.array([], dtype=bool)
        self.active_classes: List[bool] = []
        self.active_markers: List[bool] = []
        self.active_sectors: List[bool] = []
        
        self.class_order: List[int] = []
        self.attribute_order: List[int] = []
        self.all_arc_lengths: List[int] = []

    def duplicate_last_attribute(self):
        if self.dataframe is None or self.dataframe.empty:
            print("DataFrame is not loaded or is empty.")
            return

        last_attribute = self.dataframe.columns[-2]
        new_attribute = f'{last_attribute}_copy'
        self.dataframe[new_attribute] = self.dataframe[last_attribute]
        self.attribute_names.append(new_attribute)
        self.attribute_count += 1
        self.vertex_count += 1
        self.active_attributes = np.append(self.active_attributes, True)
        self.attribute_inversions = np.append(self.attribute_inversions, False)
        
        # reorder DataFrame columns to ensure 'class' is the last column
        cols = self.dataframe.columns.tolist()
        cols.append(cols.pop(cols.index('class')))  # Move 'class' to the end
        self.dataframe = self.dataframe[cols]

    def reload(self):
        if self.filepath:
            try:
                # store inversions
                inversions = self.attribute_inversions
                df = pd.read_csv(self.filepath)
                self.load_frame(df)
                # restore inversions
                self.attribute_inversions = inversions
            except Exception as e:
                print(f"Error reloading data: {e}")
        else:
            print("No filepath set for reloading.")

    def update_coef(self, attribute_index, new_coef_value):
        if 0 <= attribute_index < len(self.coefs):
            self.coefs[attribute_index] = new_coef_value

    def load_frame(self, df: pd.DataFrame, not_normal = None):
        # put class column to end of dataframe
        df.insert(len(df.columns) - 1, 'class', df.pop('class'))

        # get class information
        self.class_count = len(df['class'].unique())
        self.class_names = df['class'].value_counts().index.tolist()
        self.count_per_class = df['class'].value_counts().tolist()
        self.class_order = np.arange(0, self.class_count)

        # get class colors
        self.class_colors = COLORS.getColors(self.class_count, [0, 0, 0], [1, 1, 1]).colors_array

        # initialize arrays for class options
        self.active_markers = np.repeat(True, self.class_count)
        self.active_classes = np.repeat(True, self.class_count)
        self.active_sectors = np.repeat(True, self.class_count)

        # get attribute information
        self.attribute_names = df.columns.tolist()[:-1]
        self.attribute_count = len(df.columns) - 1
        self.attribute_order = np.arange(0, self.attribute_count)
        self.max_radial_distances = [0] * self.attribute_count
        self.coefs = np.ones(self.attribute_count) * 100

        self.active_attributes = np.repeat(True, self.attribute_count)
        self.attribute_inversions = np.repeat(False, self.attribute_count)

        # get sample information
        self.sample_count = len(df.index)
        # initialize arrays for clipping options
        self.clipped_samples = np.repeat(False, self.sample_count)
        self.clear_samples = np.repeat(False, self.sample_count)
        self.vertex_in = np.repeat(False, self.sample_count)
        self.last_vertex_in = np.repeat(False, self.sample_count)

        # general dataframe
        self.dataframe = df
        
        if not_normal is not None:
            self.not_normalized_frame = not_normal
        else:
            self.not_normalized_frame = df.copy()

    def delete_clip(self):
        """Delete the selected samples from the dataframe."""
        clipped_mask = np.array(self.clipped_samples, dtype=bool)
        self.dataframe = self.dataframe[~clipped_mask].reset_index(drop=True)
        self.not_normalized_frame = self.not_normalized_frame[~clipped_mask].reset_index(drop=True).copy()
        self.clipped_samples = np.zeros(len(self.dataframe), dtype=bool)
        # get sample information
        self.sample_count = len(self.dataframe.index)
        self.count_per_class = self.dataframe['class'].value_counts().tolist()
        # initialize arrays for clipping options
        self.clipped_samples = np.repeat(False, self.sample_count)
        self.clear_samples = np.repeat(False, self.sample_count)
        self.vertex_in = np.repeat(False, self.sample_count)
        self.last_vertex_in = np.repeat(False, self.sample_count)

    def copy_clip(self):
        """Duplicate the selected samples in the dataframe."""
        bool_clipped = np.array(self.clipped_samples, dtype=bool)

        duplicated_data = self.dataframe[bool_clipped].copy()
        duplicated_non_normalized_data = self.not_normalized_frame[bool_clipped].copy()

        self.dataframe = pd.concat([self.dataframe, duplicated_data])
        self.not_normalized_frame = pd.concat([self.not_normalized_frame, duplicated_non_normalized_data])
        
        self.load_frame(self.dataframe, self.not_normalized_frame)
        
        # Reset clipped_samples to match the new dataframe size
        self.clipped_samples = np.zeros(len(self.dataframe), dtype=bool)
        # set the duplicated data indices to clipped_samples
        self.clipped_samples[-len(duplicated_data):] = True

    def move_samples(self, move_delta: int):
        """Move the selected samples up or down in the dataframe."""
        if self.dataframe is None or self.dataframe.empty:
            print("DataFrame is not loaded or is empty.")
            return

        if not any(self.clipped_samples):
            print("No samples selected.")
            return

        if move_delta == 0:
            return
        bool_clipped = np.array(self.clipped_samples, dtype=bool)
        for attribute in self.attribute_names:
            # validate attribute + move_delta [0, 1]
            if self.dataframe.loc[bool_clipped, attribute].min() + move_delta > 0 or self.dataframe.loc[bool_clipped, attribute].max() + move_delta < 1:
                if self.not_normalized_frame.loc[bool_clipped, attribute].min() + move_delta * 10 > 0 or self.not_normalized_frame.loc[bool_clipped, attribute].max() + move_delta * 10 < 1:
                    self.dataframe.loc[bool_clipped, attribute] += move_delta
                    # update not_normalized_frame without incompatible dtype by casting to int
                    self.not_normalized_frame.loc[bool_clipped, attribute] += int(move_delta * 10)

    def load_from_csv(self, filename: str):
        """Load the dataset from a CSV file."""
        try:
            df = pd.read_csv(filename)
            self.name = os.path.basename(filename)
            self.filepath = filename
            self.load_frame(df)

        except Exception as e:
            print(f"An error occurred: {e}")
            
    def normalize_data(self, our_range: Tuple[float, float]):
        """Normalize the data in the dataframe to the specified range."""
        if self.dataframe is None or self.dataframe.empty:
            print("DataFrame is not loaded or is empty.")
            return self.dataframe

        scaler = MinMaxScaler(our_range)
        # Only normalize self.dataframe
        self.dataframe[self.attribute_names] = scaler.fit_transform(self.dataframe[self.attribute_names])
        return self.dataframe

    def normalize_col(self, col: int, our_range: Tuple[float, float]):
        """Normalize a specific column in the dataframe to the specified range."""
        scaler = MinMaxScaler(our_range)
        self.dataframe[self.attribute_names[col]] = scaler.fit_transform(self.dataframe[[self.attribute_names[col]]])
        return self.dataframe

    def roll_clips(self, roll_dir: int):
        """Select the next sample(s) to clip"""
        self.clipped_samples = list(np.roll(self.clipped_samples, roll_dir))

    def roll_vertex_in(self, roll_dir: int):
        """Select the previous sample(s) to clip"""
        self.vertex_in = list(np.roll(self.vertex_in, roll_dir))
