from typing import List, Optional, Tuple
import pandas as pd
import numpy as np

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
