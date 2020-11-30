import foolbox as fb


class PyTorchAttack():
    """Encapsulate Foolbox.PyTorchModel for classifiers
    pre-trained on ImageNet[1].

    [1]: http://image-net.org
    """
    def __init__(self, model, attack):
        """
        The only part that makes this ImageNet-specific is the
        pre-processing done. When we explore other models and datasets,
        I'll remove the hard-coded values and pass them differently, to
        make this mode accessible.

        Parameters
        ----------
        model: [PyTorch model]
            Any PyTorch model.
        attack: [foolbox.attacks]
            Any foolbox attack.
        """
        self.preprocessing = dict(mean=[0.485, 0.456, 0.406],
                                  std=[0.229, 0.224, 0.225], axis=-3)
        self.fmodel = fb.PyTorchModel(model, bounds=(0, 1),
                                      preprocessing=self.preprocessing)
        self.fmodel = self.fmodel.transform_bounds((0, 1))

        self.attack = attack

    def run(self, images, labels, epsilons=0.03):
        """Run the attack.

        Parameters
        ----------
        images : [torch.Tensor]
            A tensor representing an image or a set of images.
        labels : [torch.Tensor]
            A tensor with the integer for the image class_id for
            each image in images.
        epsilons : float, optional
            by default 0.03

        Note
        ----
        images and labels have to be 4D.

        This can usually be achieved via a simple torch.unsqueeze(0),
        but it is recommended to use ImageNetClassifier.prep_tensor,
        with normalize=False.

        Returns
        -------
        [torch.Tensor]
            Adversarial versions of all passed images.
        """
        advs, _, is_adv = self.attack(self.fmodel, images, labels,
                                      epsilons=epsilons)
        return advs
