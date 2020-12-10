import foolbox as fb

from typing import Tuple, Any, Optional
import numpy as np
import eagerpy as ep

import matplotlib.pyplot as plt

from PIL import Image
import io


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

    @staticmethod
    def get_image(
        images: Any,
        *,
        n: Optional[int] = None,
        data_format: Optional[str] = None,
        bounds: Tuple[float, float] = (0, 1),
        ncols: Optional[int] = None,
        nrows: Optional[int] = None,
        figsize: Optional[Tuple[float, float]] = None,
        scale: float = 1,
        **kwargs: Any,
    ) -> None:
        """This function returns a PIL image of the passed Tensor.
        Adapted from Foolbox.plot.images[1].

        [1]: https://github.com/bethgelab/foolbox/
        """
        x: ep.Tensor = ep.astensor(images)
        if x.ndim != 4:
            raise ValueError(
                "expected images to have four dimensions: "
                "(N, C, H, W) or (N, H, W, C)"
            )
        if n is not None:
            x = x[:n]
        if data_format is None:
            channels_first = x.shape[1] == 1 or x.shape[1] == 3
            channels_last = x.shape[-1] == 1 or x.shape[-1] == 3
            if channels_first == channels_last:
                raise ValueError("data_format ambigous, "
                                 "please specify it explicitly")
        else:
            channels_first = data_format == "channels_first"
            channels_last = data_format == "channels_last"
            if not channels_first and not channels_last:
                raise ValueError(
                    "expected data_format to be 'channels_first' or"
                    " 'channels_last'"
                )
        assert channels_first != channels_last
        x = x.numpy()
        if channels_first:
            x = np.transpose(x, axes=(0, 2, 3, 1))
        min_, max_ = bounds
        x = (x - min_) / (max_ - min_)

        if nrows is None and ncols is None:
            nrows = 1
        if ncols is None:
            assert nrows is not None
            ncols = (len(x) + nrows - 1) // nrows
        elif nrows is None:
            nrows = (len(x) + ncols - 1) // ncols
        if figsize is None:
            figsize = (ncols * scale, nrows * scale)
        fig, axes = plt.subplots(
            ncols=ncols,
            nrows=nrows,
            figsize=figsize,
            squeeze=False,
            constrained_layout=True,
            **kwargs,
        )

        for row in range(nrows):
            for col in range(ncols):
                ax = axes[row][col]
                ax.set_xticks([])
                ax.set_yticks([])
                ax.axis("off")
                i = row * ncols + col
                if i < len(x):
                    ax.imshow(x[i])

        buf = io.BytesIO()
        plt.savefig(buf, format='jpg')
        buf.seek(0)

        img = Image.open(buf)
        return img
