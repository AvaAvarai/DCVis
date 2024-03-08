class DisplayData:
    def __init__(self, dataset, textbox):
        data_info_string = ('Dataset Name: ' + dataset.name +
                            '\n\n' + 'Number of Classes: ' + str(dataset.class_count) +
                            '\n\n' + 'Number of Attributes: ' + str(dataset.attribute_count) +
                            '\n\n' + 'Number of Samples: ' + str(dataset.sample_count))

        counter = 1
        for ele in dataset.class_names:
            data_info_string += ('\n\n' + 'Class ' + str(counter) + ': ' + str(ele) +
                                 '\n' + '--Sample Count: ' + str(dataset.count_per_class[counter - 1]))
            counter += 1

        textbox.setText(data_info_string)

