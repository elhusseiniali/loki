import json


# Load ImageNet labels from JSON provided by
# the authors of the dataset.
imagenet_path = "./loki/static/datasets/imagenet/"\
                "imagenet_class_index.json"

imagenet_class_idx = json.load(open(imagenet_path))
imagenet_labels = [imagenet_class_idx[str(k)][1]
                   for k in range(len(imagenet_class_idx))]


class DatasetDAO():
    """Class to handle all operations
    involving file access for a dataset.
    """
    __instance__ = None

    def __init__(self, dataset):
        if DatasetDAO.__instance__ is None:
            DatasetDAO.__instance__ = self
        else:
            raise Exception("Only one instance of DatasetDAO is allowed.")

        self.dataset = dataset

    @staticmethod
    def get_instance():
        if not DatasetDAO.__instance__:
            DatasetDAO()
        return DatasetDAO.__instance__

    def get_all(self):
        return self.dataset.labels

    def get_by_id(self, class_id):
        return self.dataset.labels[int(class_id)]


class Dataset():
    def __init__(self, labels):
        self.labels = labels


ImageNetDAO = DatasetDAO(Dataset(labels=imagenet_labels))

datasets = [{
    "name": "ImageNet",
    "DAO": ImageNetDAO,
    "label_path": imagenet_path,
    "paper": "https://arxiv.org/abs/1409.0575"
}]
