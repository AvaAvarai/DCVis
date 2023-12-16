import numpy as np
from sklearn.preprocessing import MinMaxScaler

class DCC:
    def __init__(self, dataset):
        basic_radius = (dataset.attribute_count / np.pi) / 2

        dataset.minmax_arc_lengths = []

        working_df = dataset.dataframe.copy()
        scaler = MinMaxScaler((0, 1))
        working_df[dataset.attribute_names] = scaler.fit_transform(working_df[dataset.attribute_names])

        dataset.normalized_dataframe = working_df

        working_coef = working_df.copy()

        # strip last column
        working_coef = working_coef.iloc[:, 0:-1]

        coefArr = [100 / 100 for i in range(dataset.attribute_count)]

        for index, col in enumerate(working_coef.columns):
            columnCoef = coefArr[index]
            working_df[col] = columnCoef * working_df[col]

        section_array = np.linspace(start=0, stop=1, num=dataset.vertex_count)

        for class_index, class_name in enumerate(dataset.class_names):
            base_radius = (dataset.attribute_count / (2 * np.pi))

            # Adjust the radius based on class index
            if class_index < 2:
                # First two classes share the first axis
                radius_factor = 1
            else:
                # Subsequent classes each get their own axis, scaling geometrically
                scale_factor = 2.1  # Adjust this factor to control the rate of radius increase
                radius_factor = scale_factor * (class_index-1)

            radius = base_radius * radius_factor

            df_name = working_df[working_df['class'] == class_name]
            df_name = df_name.drop(columns='class', axis=1)

            x_coord = np.tile(section_array, reps=len(df_name.index))
            y_coord = df_name.to_numpy().ravel()

            MinE = dataset.attribute_count
            MaxE = 0

            arc_length = 0
            arc_rule = 0

            attribute_length = dataset.attribute_count * dataset.count_per_class[class_index]
            for i in range(attribute_length):
                if arc_rule >= dataset.attribute_count:
                    arc_length = 0
                    arc_rule = 0

                arc_length += y_coord[i]

                center_angle = arc_length * 360 / (2 * np.pi * radius) * radius_factor
                center_angle = np.pi * center_angle / 180

                x_coord[i] = radius * np.sin(center_angle)
                y_coord[i] = radius * np.cos(center_angle)

                arc_rule += 1

            dataset.minmax_arc_lengths.append(MinE)
            dataset.minmax_arc_lengths.append(MaxE)

            pos_array = np.column_stack((x_coord, y_coord))
            dataset.positions.append(pos_array)

        dataset.axis_count = 0

        overlaps = []
        distances = []

        for j in range(len(dataset.minmax_arc_lengths)):
            if j % 2 == 0 and j != 0:
                if dataset.minmax_arc_lengths[j] < dataset.minmax_arc_lengths[j - 1]:
                    distances.append(dataset.minmax_arc_lengths[j - 1] - dataset.minmax_arc_lengths[j])
                    minCA = dataset.minmax_arc_lengths[j] * 360 / (2 * np.pi * radius)
                    minCA = np.pi * minCA / 180
                    dataset.cr_start_x = radius * np.sin(minCA)
                    dataset.cr_start_y = radius * np.cos(minCA)
                    maxCA = dataset.minmax_arc_lengths[j - 1] * 360 / (2 * np.pi * radius)
                    maxCA = np.pi * maxCA / 180
                    dataset.cr_end_x = radius * np.sin(maxCA)
                    dataset.cr_end_y = radius * np.cos(maxCA)
                overlaps.append(dataset.minmax_arc_lengths[j])

        print(f"Overlapping Distances: {np.round(distances, decimals=2)}\nOverlapping Circumferences: {np.round(overlaps, decimals=2)}")
