import numpy as np
from sklearn.preprocessing import MinMaxScaler


class DCC:
    def __init__(self, dataset):
        circumference = dataset.attribute_count
        diameter = circumference / np.pi
        radius = diameter / 2

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

        # Changed start from -1 to 0 cause normalization is [0,1]
        section_array = np.linspace(start=0, stop=1, num=dataset.vertex_count)

        for class_index, class_name in enumerate(dataset.class_names):
            #start = time.time()
            df_name = working_df[working_df['class'] == class_name]
            df_name = df_name.drop(columns='class', axis=1)

            # Create the x_coord[]
            x_coord = np.tile(section_array, reps=len(df_name.index))

            # Y coord is the normalization and also the arc length
            y_coord = df_name.to_numpy().ravel()

            # overlapping end
            MinE = dataset.attribute_count
            MaxE = 0

            # Keep Track of Arc Length
            arc_length = 0
            arc_rule = 0

            # Get length 
            attribute_length = dataset.attribute_count * dataset.count_per_class[class_index]
            # For Loop to change x values
            for i in range(attribute_length):
                if arc_rule >= dataset.attribute_count:
                    # reset arc_length based on amount of attributes
                    arc_length = 0
                    arc_rule = 0

                arc_length += y_coord[i]

                # add attributes to compare overlapping arc length
                if arc_length > dataset.attribute_count - 1:
                    dataset.all_arc_lengths.append(arc_length)
                    # Get min Max arc length of each class
                    if arc_length > MaxE:
                        MaxE = arc_length
                    if arc_length < MinE:
                        MinE = arc_length

                # Calculate the center angle in degrees
                center_angle = arc_length * 360 / (2 * np.pi * radius)
                # Convert the center angle to radians
                center_angle = np.pi * center_angle / 180

                x_coord[i] = radius * np.sin(center_angle)
                y_coord[i] = radius * np.cos(center_angle)

                arc_rule += 1
                #arc_length = arc_rule

            dataset.minmax_arc_lengths.append(MinE)
            dataset.minmax_arc_lengths.append(MaxE)

            pos_array = np.column_stack((x_coord, y_coord))
            dataset.positions.append(pos_array)

            # end = time.time()
            # print(end-start)

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
