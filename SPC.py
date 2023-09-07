import numpy as np
from sklearn.preprocessing import MinMaxScaler


class SPCInfo:
    def __init__(self, dataset):
        working_df = dataset.dataframe.copy()

        section_array = np.linspace(start=-1, stop=1, num=dataset.vertex_count + 1)
        j = 0
        for i in range(dataset.attribute_count):
            if i % 2 != 0:
                scaler = MinMaxScaler((-1, 1))
                working_df[working_df.columns[i]] = scaler.fit_transform(working_df[[working_df.columns[i]]])
            else:
                scaler = MinMaxScaler((section_array[j], section_array[j + 1]))
                working_df[working_df.columns[i]] = scaler.fit_transform(working_df[[working_df.columns[i]]])
                j += 1

        for name in dataset.class_names:
            df_name = working_df[working_df['class'] == name]
            df_name = df_name.drop(columns='class', axis=1)

            # positions
            values = df_name.to_numpy()
            values = values.ravel()
            values = np.reshape(values, (-1, 2))

            dataset.positions.append(values)

        axis_vertex_array = [[-1, -1], [1, -1]]
        for i in range(dataset.vertex_count):
            axis_vertex_array.append([section_array[i], -1])
            axis_vertex_array.append([section_array[i], 1])

        dataset.axis_positions = axis_vertex_array
        dataset.axis_count = dataset.vertex_count + 1

        print('SPC BASED GCA COMPLETE')
