import glob
import os

import numpy as np
import torch
from numpy.random import poisson
from PIL import Image
from torch.utils import data
from torchvision import datasets, transforms


def pil_loader(path):
    # open path as file to avoid ResourceWarning (https://github.com/python-pillow/Pillow/issues/835)
    with open(path, 'rb') as f:
        with Image.open(f) as image:
            return image.convert('RGB')


def poisson_noise(image, peak=30):
    image = np.array(image)
    ratio = peak / 255.0
    output = poisson(image * ratio) / ratio

    # convex combination
    t = np.random.rand()
    output = t * image + (1 - t) * output

    output = np.clip(output, 0, 255).astype(np.uint8)
    output = Image.fromarray(output)
    return output


class NoisyCoco(data.Dataset):
    def __init__(self, root, folder='train2017', transform=None, crop_size=128):
        super(NoisyCoco, self).__init__()
        self.root = root
        self.crop_size = crop_size
        self.random_crop = transforms.RandomCrop(crop_size)
        self.paths = glob.glob(os.path.join(root, folder, '*.jpg'))
        self.transform = transform

    def __getitem__(self, index):
        path = self.paths[index]
        image = pil_loader(path)

        # crop
        try:
            image = self.random_crop(image)
        except:
            # need to do something else
            z = np.zeros(shape=[self.crop_size,self.crop_size,3],dtype=np.uint8)
            image = Image.fromarray(z)

        # add poisson noise
        noisy = poisson_noise(image)

        if self.transform:
            image = self.transform(image)
            noisy = self.transform(noisy)

        return noisy, image

    def __len__(self):
        return len(self.paths)


def main():

    transform = transforms.Compose([
        transforms.ToTensor()
    ])

    dataloader = data.DataLoader(NoisyCoco('data',
                                           folder='test2017',
                                           transform=transform,
                                           crop_size=320),
                                 32,
                                 shuffle=True)
    from torchvision.utils import save_image
    from torch.autograd import Variable

    for i, (x, y) in enumerate(dataloader):
        continue


if __name__ == '__main__':
    main()
