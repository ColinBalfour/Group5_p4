from torch import nn
import torch
import torchvision.transforms as transforms
import torchvision
import matplotlib.pyplot as plt
import numpy as np

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay


class Pipeline:
    def __init__(self, synthetic_dataset=None):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        transform = transforms.Compose(
            [
                transforms.Grayscale(
                    num_output_channels=1
                ),  # Convert image to grayscale
                transforms.ToTensor(),
                transforms.Normalize((0.5,), (0.5,)),
            ]
        )  # Normalize for grayscale images

        trainset = torchvision.datasets.CIFAR10(
            root="./data", train=True, download=True, transform=transform
        )

        if synthetic_dataset is not None:
            # Combine original CIFAR-10 data with synthetic data
            concat_dataset = torch.utils.data.ConcatDataset(
                [trainset, synthetic_dataset]
            )
            self.trainloader = torch.utils.data.DataLoader(
                concat_dataset, batch_size=32, shuffle=True, num_workers=4
            )
        else:
            # Only use original data if no synthetic data is provided
            self.trainloader = torch.utils.data.DataLoader(
                trainset, batch_size=32, shuffle=True, num_workers=4
            )

        testset = torchvision.datasets.CIFAR10(
            root="./data", train=False, download=True, transform=transform
        )
        self.testloader = torch.utils.data.DataLoader(
            testset, batch_size=32, shuffle=False, num_workers=4
        )

        self.classes = (
            "plane",
            "car",
            "bird",
            "cat",
            "deer",
            "dog",
            "frog",
            "horse",
            "ship",
            "truck",
        )

        self.lossFunc = nn.CrossEntropyLoss()

    def train_step(self, model, optimizer):
        model.train()

        epochloss = 0
        for batchcount, (images, labels) in enumerate(self.trainloader):
            images = images.to(self.device)
            labels = labels.to(self.device)

            # labels = torch.eye(len(classes))[labels].to(device)
            # pdb.set_trace()

            optimizer.zero_grad()

            y = model(images)

            # print('thing')
            # print(images.shape)
            # print(y.shape)
            # print(labels.shape)

            loss = self.lossFunc(y, labels)
            loss.backward()

            # print('gradients computed')

            optimizer.step()

            epochloss += loss.item()

        return epochloss

    def val_step(self, model):
        model.to(self.device)
        correct = 0
        total = 0

        total_labels = []
        total_predicted = []
        model.eval()
        with torch.no_grad():
            for batchcount, (images, labels) in enumerate(self.testloader):
                images = images.to(self.device)
                labels = labels.to(self.device)

                y = model(images)

                _, predicted = torch.max(y, 1)

                total += labels.size(0)
                correct += (predicted == labels).sum().item()

                total_labels.extend(labels.cpu().numpy())
                total_predicted.extend(predicted.cpu().numpy())

            cm = confusion_matrix(
                total_labels, total_predicted, labels=np.arange(len(self.classes))
            )
            ConfusionMatrixDisplay(cm, display_labels=self.classes).plot()

        return correct * 100 / total


def imshow(img):
    img = img / 2 + 0.5  # unnormalize
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()


LOSS_FN = nn.CrossEntropyLoss()
