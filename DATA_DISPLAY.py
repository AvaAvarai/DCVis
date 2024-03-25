class DisplayData:
    def __init__(self, dataset, textbox):
        data_info_string = ('Dataset Name: ' + dataset.name +
                            '\n' + 'Number of classes: ' + str(dataset.class_count) + ' attributes: ' + str(dataset.attribute_count) + ' samples: ' + str(dataset.sample_count))

        counter = 1
        for ele in dataset.class_names:
            data_info_string += ('\n' + 'Class ' + str(counter) + ': ' + str(ele) + ' sample Count: ' + str(dataset.count_per_class[counter - 1]))
            counter += 1

        textbox.setText(data_info_string)

