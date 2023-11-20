import PC
import SPC
import DSC1
import DSC2
import SCC


class GCA:
    def __init__(self, dataset):
        print(dataset.plot_type)
        dataset.positions = []

        if dataset.plot_type == 'PC':  # Parallel Coordinates
            dataset.vertex_count = dataset.attribute_count
            PC.PC(dataset)

        elif dataset.plot_type == 'SPC':  # Shifted Paired Coordinates
            dataset.vertex_count = dataset.attribute_count // 2
            # make even attributes
            if (len(dataset.dataframe.columns) - 1) % 2 == 1:
                dataset.dataframe.insert(len(dataset.dataframe.columns) - 1, 'class', dataset.dataframe.pop('class'))
                dataset.dataframe['Dupe-x' + str(len(dataset.dataframe.columns) - 2)] = dataset.dataframe.iloc[:, len(dataset.dataframe.columns) - 2]
                dataset.vertex_count += 1
            SPC.SPC(dataset)

        elif dataset.plot_type == 'DSC1':  # Dynamic Scaffold Coordinates 1
            dataset.vertex_count = dataset.attribute_count
            DSC1.DSC1(dataset)

        elif dataset.plot_type == 'DSC2':  # Dynamic Scaffold Coordinates 2
            dataset.vertex_count = dataset.attribute_count // 2
            # make even attributes
            if (len(dataset.dataframe.columns) - 1) % 2 == 1:
                dataset.dataframe.insert(len(dataset.dataframe.columns) - 1, 'class', dataset.dataframe.pop('class'))
                dataset.dataframe['Dupe-x' + str(len(dataset.dataframe.columns) - 2)] = dataset.dataframe.iloc[:, len(dataset.dataframe.columns) - 2]
                dataset.vertex_count += 1
            DSC2.DSC2(dataset)

        elif dataset.plot_type == 'SCC':  # Static Circular Coordinates
            dataset.vertex_count = dataset.attribute_count
            SCC.SCC(dataset)

        else:
            print('No type selected')

