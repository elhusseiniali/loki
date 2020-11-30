import torch
from torchvision import transforms

import json


class ImageNetClassifier():
    """A class to provide common setup for all torchivision models that
    are pre-trained on the ImageNet[1] dataset.

    [1]: http://image-net.org
    """
    def __init__(self, model):
        """Basic setup tasks for the model.

        1.  device: if CUDA drivers are available, attach classifier to
        GPU. Otherwise, use CPU.
        2.  model.eval(): use model (check parameters below) in classifier
        mode.
        3.  transform: used to transform images to the form that the model
        needs.
        4.  normalize: normalize images as part of pre-processing expected by
        the model.
        5.  labels: human-readable labels (as opposed to class indices) for
        the classes (e.g. 'dog' instead of some integer).

        Parameters
        ----------
        model: [type]
            [description]
        """
        self.device = torch.device('cuda:0' if torch.cuda.is_available()
                                   else 'cpu')
        self.model = model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor()
        ])

        self.normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225])
        self.labels = self.generate_labels()

    def generate_labels(self):
        """Get labels from imagenet_class_index.json.

        Returns
        -------
        idx2label: [list of str]
            idx2label[class_id] gives the actual label as a string.
        """
        class_idx = json.load(open("./loki/static/models/imagenet/"
                                   "imagenet_class_index.json"))
        idx2label = [class_idx[str(k)][1] for k in range(len(class_idx))]

        return idx2label

    def prep_label(self, index):
        return torch.as_tensor(index).to(self.device).unsqueeze(0)

    def prep_tensor(self, img, normalize=True):
        """Prepare an image to be given to the model.

        Parameters
        ----------
        img: [PIL image or np.ndarray]
            Any image.
        normalize: bool, optional
            Choice to normalize an image or not, by default True.
            For prediction, images need to be normalized. When prepping
            for an attack, they shouldn't be (because Foolbox does it
            on its own).

        Returns
        -------
        [PyTorch.Tensor]
            PyTorch tensor representing the input image, attached to whatever
            device the model is attached to (i.e. GPU or CPU).
        """
        if normalize:
            img_t = self.normalize(self.transform(img))
        else:
            img_t = self.transform(img)
        batch_t = torch.unsqueeze(img_t, 0).to(self.device)

        return batch_t

    def predict(self, img, n=5):
        """Get classification from model.

        Parameters
        ----------
        img: [PIL Image or nd.array]
            Any image.
        n: int, optional
            number of classes, by default 5.

        Returns
        -------
        [list of tuple]
            A tuple in this list has the form:
                (tensor(class_id, device), label, percentage), where:
                - class_id is the id for the predicted ImageNet class,
                device is CPU or GPU;
                - label is the human-readable label of the
                class from class_id;
                - percentage is the model's confidence level that the image
                belongs to this class.
        """
        out = self.model(self.prep_tensor(img))

        _, index = torch.sort(out, descending=True)
        percentage = torch.nn.functional.softmax(out, dim=1)[0] * 100

        return [(i, self.labels[i],
                percentage[i].item()) for i in index[0][:n]]
