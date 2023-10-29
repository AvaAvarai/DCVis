import PC
import SPC
import DSC1
import DSC2
import SCC


class GCA_Option:
    def __init__(self, dataset):
        print(dataset.plot_type)
        dataset.positions = []

        if dataset.plot_type == 'PC':
            dataset.vertex_count = dataset.attribute_count
            PC.PCInfo(dataset)

        elif dataset.plot_type == 'DSC1':
            dataset.vertex_count = dataset.attribute_count
            DSC1.DSC1Info(dataset)

        elif dataset.plot_type == 'DSC2':
            dataset.vertex_count = int(dataset.attribute_count / 2)
            DSC2.DSC2Info(dataset)

        elif dataset.plot_type == 'SPC':
            dataset.vertex_count = int(dataset.attribute_count / 2)
            SPC.SPCInfo(dataset)

        elif dataset.plot_type == 'SCC':
            dataset.vertex_count = dataset.attribute_count
            SCC.SCCInfo(dataset)

        else:
            print('No type selected')

