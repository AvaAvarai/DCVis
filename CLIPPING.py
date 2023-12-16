import numpy as np
import pandas as pd
from csv import writer
import os

# exit codes for cohen-sutherland
INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8

def clip_display(textbox, total_sample):
    filenames = ['test_line.csv', 'test_vertex.csv', 'test_end.csv']
    clip_types = ['Line Clip', 'Vertex Clip', 'End Clip']
    info_string = ''

    cnt = 0
    for file in filenames:
        df = pd.read_csv(file)
        # get dataset name
        name = os.path.basename(file)

        # get class information
        class_names = df['class'].value_counts().index.tolist()
        count_per_class = df['class'].value_counts().tolist()
        sample_count = len(df.index)

        # display class data
        info_string += (
            'Clip Type: ' + clip_types[cnt] + '\n\n' + 'Number of Samples: ' + str(sample_count) + '\n' +
            'Amount of Dataset: ' + '{:.2f}'.format(sample_count / total_sample * 100)) + '%'

        # loop through class names
        counter = 1
        for ele in class_names:
            info_string += ('\n\n' + 'Class ' + str(counter) + ': ' + str(ele) +
                            '\n' + '--Count: ' + str(count_per_class[counter - 1]))
            counter += 1

        info_string += '\n\nDataset Name: ' + name + '\n===============\n\n'
        cnt += 1

    textbox.setText(info_string)

def clip_files(dataset, textbox):
    # for option 1 (lines clipped)
    output_train1 = open('train_line.csv', 'w', newline='')
    output_test1 = open('test_line.csv', 'w', newline='')
    csv_writer_train1 = writer(output_train1)
    csv_writer_test1 = writer(output_test1)

    # for option 2 (vertex bounded)
    output_train2 = open('train_vertex.csv', 'w', newline='')
    output_test2 = open('test_vertex.csv', 'w', newline='')
    csv_writer_train2 = writer(output_train2)
    csv_writer_test2 = writer(output_test2)

    # for option 3 (last vertex (line end) bounded)
    output_train3 = open('train_end.csv', 'w', newline='')
    output_test3 = open('test_end.csv', 'w', newline='')
    csv_writer_train3 = writer(output_train3)
    csv_writer_test3 = writer(output_test3)

    csv_writer_train1.writerow(np.append(np.array(dataset.attribute_names), 'class'))
    csv_writer_test1.writerow(np.append(np.array(dataset.attribute_names), 'class'))

    csv_writer_train2.writerow(np.append(np.array(dataset.attribute_names), 'class'))
    csv_writer_test2.writerow(np.append(np.array(dataset.attribute_names), 'class'))

    csv_writer_train3.writerow(np.append(np.array(dataset.attribute_names), 'class'))
    csv_writer_test3.writerow(np.append(np.array(dataset.attribute_names), 'class'))

    # build files
    for i in range(dataset.sample_count):
        if dataset.clipped_samples[i]:
            csv_writer_test1.writerow(np.array(dataset.dataframe.iloc[[i]].squeeze()))
        else:
            csv_writer_train1.writerow(np.array(dataset.dataframe.iloc[[i]].squeeze()))

        if dataset.vertex_in[i]:
            csv_writer_test2.writerow(np.array(dataset.dataframe.iloc[[i]].squeeze()))
        else:
            csv_writer_train2.writerow(np.array(dataset.dataframe.iloc[[i]].squeeze()))

        if dataset.last_vertex_in[i]:
            csv_writer_test3.writerow(np.array(dataset.dataframe.iloc[[i]].squeeze()))
        else:
            csv_writer_train3.writerow(np.array(dataset.dataframe.iloc[[i]].squeeze()))

    output_train1.close()
    output_test1.close()

    output_train2.close()
    output_test2.close()

    output_train3.close()
    output_test3.close()

    # build text box
    clip_display(textbox, dataset.sample_count)

class MinAndMax(object):
    x_min = None
    x_max = None
    y_min = None
    y_max = None

# Function to compute region code for a point(x, y)
def compute_code(x, y, min_max):
    code = INSIDE
    if x < min_max.x_min:  # to the left of rectangle
        code |= LEFT
    elif x > min_max.x_max:  # to the right of rectangle
        code |= RIGHT

    if y < min_max.y_min:  # below the rectangle
        code |= BOTTOM
    elif y > min_max.y_max:  # above the rectangle
        code |= TOP

    return code

def cohen_sutherland_clip(x1, y1, x2, y2, min_max, class_num, sample_num):
    # Compute region codes for P1, P2
    code1 = compute_code(x1, y1, min_max)
    code2 = compute_code(x2, y2, min_max)
    accept = False

    while True:
        # If both endpoints lie within rectangle
        if code1 == 0 and code2 == 0:
            accept = True
            break

        # If both endpoints are outside rectangle
        elif (code1 & code2) != 0:
            break

        # Some segment lies within the rectangle
        else:
            x = 1.0
            y = 1.0
            if code1 != 0:
                code_out = code1
            else:
                code_out = code2

            if code_out & TOP:
                x = x1 + (x2 - x1) * (min_max.y_max - y1) / (y2 - y1)
                y = min_max.y_max

            elif code_out & BOTTOM:
                x = x1 + (x2 - x1) * (min_max.y_min - y1) / (y2 - y1)
                y = min_max.y_min

            elif code_out & RIGHT:
                y = y1 + (y2 - y1) * (min_max.x_max - x1) / (x2 - x1)
                x = min_max.x_max

            elif code_out & LEFT:
                y = y1 + (y2 - y1) * (min_max.x_min - x1) / (x2 - x1)
                x = min_max.x_min

            if code_out == code1:
                x1 = x
                y1 = y
                code1 = compute_code(x1, y1, min_max)
            else:
                x2 = x
                y2 = y
                code2 = compute_code(x2, y2, min_max)

    if accept:
        # print('Sample: ' + str(sample_num) + ' in class: ' + str(class_num) + ' accepted from %.2f, %.2f to %.2f, %.2f' % (x1, y1, x2, y2))
        return True
    else:
        # print("Line rejected")
        return False


def vertex_check(vertex_x, vertex_y, min_max):
    if (min_max.x_min <= vertex_x <= min_max.x_max) and (min_max.y_min <= vertex_y <= min_max.y_max):
        return True
    else:
        return False


def clip_samples(positions, rect, dataset):
    min_max = MinAndMax()
    min_max.x_min = min(rect[0], rect[2])
    min_max.x_max = max(rect[0], rect[2])
    min_max.y_min = min(rect[1], rect[3])
    min_max.y_max = max(rect[1], rect[3])

    cnt = 0
    class_num = 1
    # check each class
    for data_class in positions:

        # check each sample in the class
        for sample in data_class:

            # check each polyline in the line
            for i in range(dataset.vertex_count):
                # line clip
                if i < dataset.vertex_count - 1:
                    is_clipped = cohen_sutherland_clip(sample[2 * i], sample[2 * i + 1], sample[2 * i + 2],
                                                       sample[2 * i + 3], min_max, class_num, cnt)
                    if is_clipped:
                        dataset.clipped_samples[cnt] = True

                    # vertex clip
                    is_inside = vertex_check(sample[2 * i], sample[2 * i + 1], min_max)
                    if is_inside:
                        dataset.vertex_in[cnt] = True
                else:
                    # last vertex clip (also checks generic vertex clip on last vertex)
                    is_inside = vertex_check(sample[2 * i], sample[2 * i + 1], min_max)
                    if is_inside:
                        dataset.vertex_in[cnt] = True
                        dataset.last_vertex_in[cnt] = True
            cnt += 1
        class_num += 1


class Clipping:
    def __init__(self, rect, dataset):
        positions = []
        for i in range(dataset.class_count):
            positions.append(np.array(dataset.positions[i]))
            positions[i] = np.reshape(positions[i], (dataset.count_per_class[i], dataset.vertex_count * 2))

        clip_samples(positions, rect, dataset)
