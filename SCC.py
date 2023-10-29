import numpy
from sklearn.preprocessing import MinMaxScaler


class SCCInfo:
    def __init__(self, data):
        data.vertex_count = data.attribute_count
        radius = data.attribute_count / (2 * numpy.pi)
        
        scaler = MinMaxScaler((0, 1))
        data.dataframe[data.attribute_names] = scaler.fit_transform(data.dataframe[data.attribute_names])

        # Changed start from -1 to 0 cause normalization is [0,1]
        section_array = numpy.linspace(0, 1, data.attribute_count)

        for class_index, class_name in enumerate(data.class_names):
            #start = time.time()
            df_name = data.dataframe[data.dataframe['class'] == class_name]
            df_name = df_name.drop(columns='class', axis=1)

            # Create the x_coord[]
            x_coord = numpy.tile(section_array, reps=len(df_name.index))
            
            # Y coord is the normalization and also the arc length
            y_coord = df_name.to_numpy().ravel()
            
            # Get length
            attribute_length = data.attribute_count * data.count_per_class[class_index]

            # Keep Track of Arc Length
            arc_length = 0
            arc_rule = 0

            for i in range(attribute_length):
                if arc_rule >= data.attribute_count:
                    arc_length = 0
                    arc_rule = 0
                
                arc_length += y_coord[i]
                # Calculate the center angle in degrees
                center_angle = arc_length * 360 / (2 * numpy.pi * radius)
                # Convert the center angle to radians
                center_angle = numpy.pi * center_angle / 180

                x_coord[i] = radius * numpy.sin(center_angle)
                y_coord[i] = radius * numpy.cos(center_angle)
                
                arc_rule += 1
                arc_length = arc_rule

            pos_array = numpy.column_stack((x_coord, y_coord))
            data.positions.append(pos_array)
        
        data.axis_count = 0
        
        print('SCC BASED GCA COMPLETE')
