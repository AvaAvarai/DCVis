import numpy as np
from sklearn.preprocessing import MinMaxScaler

# this class is for finding DSC2 vertices
class DSC2Info:
    def __init__(self, dataset):
        working_df = dataset.dataframe.copy()

        # =============================================== scaling =============================================
        scaler = MinMaxScaler((0, 1))
        for i in range(dataset.attribute_count):
            working_df[working_df.columns[i]] = scaler.fit_transform(working_df[[working_df.columns[i]]])

        # space = 1.0 / dataset.vertex_count
        space_array = np.repeat(0.05, repeats=dataset.attribute_count)
        # for i in range(dataset.attribute_count):
        #     if i % 2 == 1:
        #         space_array[i] = 0.005
        space_array[0] = 1
        space_array[1] = 1

        for i in range(dataset.attribute_count):
            scaler = MinMaxScaler((0, space_array[i]))
            working_df[working_df.columns[i]] = scaler.fit_transform(working_df[[working_df.columns[i]]])
        # =====================================================================================================
        # =============================================== no scaling ==========================================
        # space = 1.0 / dataset.vertex_count
        # scaler = MinMaxScaler((0, space))
        # working_df[dataset.attribute_names] = scaler.fit_transform(working_df[dataset.attribute_names])
        # =====================================================================================================
        print(dataset.vertex_count)
        angle_array = np.repeat(0, dataset.vertex_count)
        t = 0
        # for i in range(dataset.vertex_count):
        #         angle_array[i] = 0 - t
        #         t -= 10
        angle_array[0] = 0
        angle_array[1] = 0

        for name in dataset.class_names:
            df_name = working_df[working_df['class'] == name]
            df_name = df_name.drop(columns='class', axis=1)

            # positions
            values = df_name.to_numpy()
            values = values.ravel()
            values = np.reshape(values, (-1, 2))
            scaffolds = np.asarray([[0, 0]])

            j = 0
            for i in range(len(df_name.index) * dataset.vertex_count):
                if i % dataset.vertex_count == 0:
                    j = 0
                    new_x = np.cos(np.deg2rad(angle_array[j])) * values[i][0] - np.sin(np.deg2rad(angle_array[j])) * \
                            values[i][1]
                    new_y = np.sin(np.deg2rad(angle_array[j])) * values[i][0] + np.cos(np.deg2rad(angle_array[j])) * \
                            values[i][1]
                    scaffolds = np.append(scaffolds, [[-1 + new_x, -1 + new_y]], 0)
                    j += 1
                else:
                    new_x = np.cos(np.deg2rad(angle_array[j])) * values[i][0] - np.sin(np.deg2rad(angle_array[j])) * \
                            values[i][1]
                    new_y = np.sin(np.deg2rad(angle_array[j])) * values[i][0] + np.cos(np.deg2rad(angle_array[j])) * \
                            values[i][1]
                    j += 1
                    scaffolds = np.append(scaffolds, [[scaffolds[i][0] + new_x, scaffolds[i][1] + new_y]],
                                          0)

            scaffolds = np.delete(scaffolds, 0, 0)
            dataset.positions.append(scaffolds)

        dataset.axis_positions = [[-1, -1], [-1, 1], [-1, -1], [1, -1]]
        dataset.axis_count = 2
