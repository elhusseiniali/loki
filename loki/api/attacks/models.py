import foolbox as fb


class PyTorchAttack():
    """Encapsulate Foolbox.PyTorchModel for classifiers
    pre-trained on ImageNet[1].

    [1]: http://image-net.org
    """
    def __init__(self, model, attack):
        """
        Set-up PyTorchModel to be able to run an attack.

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
        - advs
        [torch.Tensor]
            Adversarial versions of all passed images.
        - is_adv
        [torch.Tensor]
            Tensor with:
                for image in images:
                    . True if self.fmodel changes its
                    classification of the image
                    . False otherwise
            If multiple images are passed, then is_adv[i] would be
            the tensor described above, for image[i].
        """
        advs, _, is_adv = self.attack(self.fmodel, images, labels,
                                      epsilons=epsilons)
        return advs, is_adv


attacks = [
    {
        "name": "LinfDeepFool",
        "attack": fb.attacks.LinfDeepFoolAttack(),
        "paper": "https://arxiv.org/abs/1511.04599"
    },
    {
        "name": "FastGradientSignMethod",
        "attack": fb.attacks.FGSM(),
        "paper": "https://arxiv.org/abs/1412.6572"
    },
    {
        "name": "LinfBasicIterativeMethod",
        "attack": fb.attacks.LinfBasicIterativeAttack(),
        "paper": "https://arxiv.org/abs/1607.02533"
    },
    {
        "name": "AdditiveUniformNoise",
        "attack": fb.attacks.LinfAdditiveUniformNoiseAttack(),
        "paper": "https://dl.acm.org/citation.cfm?id=3134635"
    },
    {
        "name": "NewtonFool",
        "attack": fb.attacks.NewtonFoolAttack(),
        "paper": "https://arxiv.org/abs/1607.02533"
    },
    {
        "name": "Spatial Attack",
        "attack": fb.attacks.SpatialAttack(max_translation=6,
                                           num_translations=6,
                                           max_rotation=20,
                                           num_rotations=5
                                           ),
        "paper": "https://arxiv.org/abs/1801.02612"
    },
    {
        "name": "L2CarliniWagner",
        "attack": fb.attacks.L2CarliniWagnerAttack(steps=1000),
        "paper": "https://arxiv.org/abs/1608.04644"
    }
]
