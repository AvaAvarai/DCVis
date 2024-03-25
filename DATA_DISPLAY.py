class DisplayData:
    def __init__(self, dataset, textbox):
        data_info_string = f'Dataset Name: {dataset.name} \nNumber of classes: {dataset.class_count} attributes: {dataset.attribute_count} samples: {dataset.sample_count}'

        for index, ele in enumerate(dataset.class_names):
            data_info_string += f'\nClass {index + 1}: {ele} sample count: {dataset.count_per_class[index]}'

        textbox.setText(data_info_string)
