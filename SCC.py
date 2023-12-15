import numpy as np
import DATASET

def compute_coordinates(data, df):
    radius = data.attribute_count / (2 * np.pi)
    section_array = np.linspace(0, 1, data.attribute_count)
    x_coord = np.tile(section_array, reps=len(df.index))
    y_coord = df.to_numpy().ravel()

    attribute_length = data.attribute_count * len(df.index)
    arc_length = 0
    arc_rule = 0

    for i in range(attribute_length):
        if arc_rule >= data.attribute_count:
            arc_length = 0
            arc_rule = 0

        if data.attribute_inversions[arc_rule]:
            arc_length += (1 - y_coord[i])  # Invert the range
        else:
            arc_length += y_coord[i]
            
        center_angle = arc_length * 360 / (2 * np.pi * radius)
        center_angle = np.pi * center_angle / 180

        x_coord[i] = radius * np.sin(center_angle)
        y_coord[i] = radius * np.cos(center_angle)

        arc_rule += 1
        arc_length = arc_rule

    return np.column_stack((x_coord, y_coord))


class SCC:
    def __init__(self, data: DATASET.Dataset):
        data.vertex_count = data.attribute_count
        data.dataframe = data.normalize_data(range=(0, 1))

        # Compute coordinates for each class and store in data.positions
        data.positions = [compute_coordinates(data, data.dataframe[data.dataframe['class'] == class_name].drop('class', axis=1))
                          for class_name in data.class_names]

        data.axis_count = 0
