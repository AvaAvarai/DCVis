import numpy as np
from sklearn.preprocessing import MinMaxScaler
import time


class PCInfo:
    def __init__(self, dataset):
        working_df = dataset.dataframe.copy()
        scaler = MinMaxScaler((-1, 1))

        working_df[dataset.attribute_names] = scaler.fit_transform(working_df[dataset.attribute_names])

        section_array = np.linspace(start=-1, stop=1, num=dataset.vertex_count)

        for name in dataset.class_names:
            #start = time.time()
            df_name = working_df[working_df['class'] == name]
            df_name = df_name.drop(columns='class', axis=1)

            # positions
            x_coord = np.tile(section_array, reps=len(df_name.index))
            y_coord = df_name.to_numpy()
            y_coord = y_coord.ravel()
            # final form is [[x1, y1], [x2, y2], [x3, y3]]
            pos_array = np.column_stack((x_coord, y_coord))
            dataset.positions.append(pos_array)
            #end = time.time()
            #print(end-start)

        axis_vertex_array = [[-1, -1], [-1, 1]]
        for idx in range(1, dataset.vertex_count):
            axis_vertex_array.append([section_array[idx], -1])
            axis_vertex_array.append([section_array[idx], 1])

        dataset.axis_positions = axis_vertex_array
        dataset.axis_count = dataset.vertex_count

        print('PC BASED GCA COMPLETE')
