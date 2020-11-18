from facenet_pytorch import MTCNN, InceptionResnetV1
import torch

import pandas as pd

from PIL import Image


class InceptionResNet():
    """ A variant of FaceNet, a facial recognition system.
    https://deeplearning4j.org/api/latest/org/deeplearning4j/zoo/model/InceptionResNetV1.html
    """
    def __init__(self, pretrain='vggface2'):
        """Setup PyTorch to do all the work.

        - MTCNN: used to detect faces from input images, and to prepare the
        image for classification.
        https://arxiv.org/abs/1604.02878
        - device: if available, use an NVIDIA GPU (PyTorch has optimizations
        for CUDA).
        - resnet: the actual model doing the classification.
        - names: human names (instead of class indices) for VGGFace2.
        This implementation is temporary. A better implementation would have
        a Data class (with Data.data and Data.labels holding images and labels,
        respectively), and then this class would be used in our classifier.

        Parameters
        ----------
        pretrain : str, optional
            Dataset that the model was pre-trained on, by default 'vggface2'.
            https://www.robots.ox.ac.uk/~vgg/data/vgg_face2/

            For now, this is implemented with a default value because it's the
            only option we tried. We might have to revisit the design for other
            variants. Note that, in facenet_pytorch, there is another option
            (specifically, the casia-webface dataset).
        """
        self.device = torch.device('cuda:0' if torch.cuda.is_available()
                                   else 'cpu')

        self.mtcnn = MTCNN(
            image_size=160, margin=0, min_face_size=20,
            thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
            device=self.device
        )
        self.resnet = InceptionResnetV1(pretrained=pretrain).eval()\
                                                            .to(self.device)
        self.resnet.classify = True

        self.names = self.vggface2_labels()

    def vggface2_labels(self):
        """Extract all the names from identity_meta.csv, provided
        by the authors of VGGFace2.

        Returns
        -------
        [Pandas DataFrame], dict-like.
            A dict-like structure that has two columns/keys: Class_ID and Name.
        """
        id_meta = pd.read_csv("loki/static/models/vggface2/identity_meta.csv",
                              sep="\n")
        id_meta = id_meta[
            'Class_ID, Name, Sample_Num, Flag, Gender'].str\
                                                       .split(',', expand=True)

        id_meta.columns = [
            'Class_ID', 'Name', 'Sample_Num', 'Flag', 'Gender', 'None']
        id_meta.drop(columns=['None'], inplace=True)

        vgg_names = id_meta.drop(columns=[
            'Sample_Num', 'Flag', 'Gender']).set_index('Class_ID')

        return vgg_names

    def get_label(self, index, key="Name"):
        """Get the human name from class ID.

        Parameters
        ----------
        index : [int]
            Class ID (usually, training sets are oragnized as folders of
            different IDs, one folder per class, or human, in our case)
        key : str, optional
            Key inside the struct that holds the names, by default "Name".

        Returns
        -------
        [type]
            [description]
        """
        return eval(self.names[key][index])

    def predict(self, path):
        """Run the classifier.

        Parameters
        ----------
        path : [str]
            Input image path.

        Returns
        -------
        [str]
            Name of the person whose face the model thinks the
            image belongs to.
        """
        img = Image.open("loki/" + path)

        # crop and pre-whiten image tensor
        img_cropped = self.mtcnn(img).to(self.device)

        img_probs = self.resnet(img_cropped.unsqueeze(0))

        result = img_probs[0].argmax()
        index = result.item() + 1

        return self.get_label(index=index)
