# %% [markdown]
# # Домашнее задание № 2
# Сегментация изображений с определением рода с помощью YOLOv7.

# %%
import os
import shutil
import torch
import yaml
from sklearn.model_selection import train_test_split

# %matplotlib inline

# %%
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# %% [markdown]
"""
### Загрузка набора данных
"""

# %%
import os  # noqa
from pathlib import Path  # noqa

dataset_path = Path("../../data/segmented")

# %% [markdown]
# Разобьём датасет на тестовую и обучающую выборки

# %%
test_size = 0.2  # размер тестовой выборки
valid_size = 0.1  # размер валидационной выборки

# %%
image_files = [f for f in os.listdir(dataset_path) if f.endswith(".jpg")]
annotation_files = [f for f in os.listdir(dataset_path) if f.endswith(".txt")]

image_files_with_annotations = [
    f for f in image_files if f.replace(".jpg", ".txt") in annotation_files
]

train_files, test_files = train_test_split(
    image_files_with_annotations, test_size=test_size, random_state=42
)
train_files, valid_files = train_test_split(
    train_files,
    test_size=len(image_files_with_annotations) * valid_size / len(train_files),
    random_state=42,
)


def copy_files(files, source_path, dest_path):
    for file in files:
        shutil.copy(os.path.join(source_path, file), os.path.join(dest_path, "images"))
        shutil.copy(
            os.path.join(source_path, file.replace(".jpg", ".txt")),
            os.path.join(dest_path, "labels"),
        )


for folder in ["train", "valid", "test"]:
    os.makedirs(os.path.join(dataset_path, folder, "images"), exist_ok=True)
    os.makedirs(os.path.join(dataset_path, folder, "labels"), exist_ok=True)

copy_files(train_files, dataset_path, os.path.join(dataset_path, "train"))
copy_files(valid_files, dataset_path, os.path.join(dataset_path, "valid"))
copy_files(test_files, dataset_path, os.path.join(dataset_path, "test"))

for file in os.listdir(dataset_path):
    if not file.endswith(".names") and os.path.isfile(os.path.join(dataset_path, file)):
        os.remove(os.path.join(dataset_path, file))

# %% [markdown]
# Добавим конфиг к YOLO

# %%
train_path = f'{dataset_path}/train/images'
val_path = f'{dataset_path}/valid/images'
test_path = f'{dataset_path}/test/images'

names_file = os.path.join(dataset_path, 'obj.names')
with open(names_file, 'r') as file:
    class_names = [line.strip() for line in file.readlines()]

num_classes = len(class_names)

data = {
    'train': train_path,
    'val': val_path,
    'test': test_path,
    'nc': num_classes,
    'names': class_names
}

output_file = os.path.join(dataset_path, 'data.yaml')
with open(output_file, 'w') as file:
    documents = yaml.dump(data, file)

os.remove(os.path.join(dataset_path, 'obj.names'))

# %% [markdown]
# ## Запуск обучения
# ### Архитектура сети

# %%
# %cd yolov7

# %%
weights = torch.load('yolov7.pt', map_location=torch.device('cpu'))

# %%
print(weights)

# %% [markdown]
"""
### Начало

Чтобы получить полный список аргументов обучения, перейдите по [ссылке](https://github.com/WongKinYiu/yolov7/blob/main/train.py)

Несколько важных аргументов, которые следует знать

configuration: в основной папке yolov7 перейдите в папку cfg/training и выберите путь к соответствующему файлу конфигурации. Укажите относительный путь к файлу в аргументе --cfg.
data путь к папке с данными, она будет обработана автоматически
weights путь к предварительно обученным весам, заданный аргументом --weights
"""

# %%
!python train.py --batch 16 --cfg cfg/training/yolov7.yaml --epochs 55 --data {dataset_path}/data.yaml --weights 'yolov7.pt'

# %% [markdown]
# ### Чтение тренировочной и тестовой выборки


# %%
def stem_extensions(filename: Path):
    extensions = "".join(filename.suffixes)

    return str(filename).removesuffix(extensions)


# %%
dataset_path = Path(stem_extensions(file_path))

with open(dataset_path / "train", "rb") as f:
    data_train = pickle.load(f, encoding="latin1")
with open(dataset_path / "test", "rb") as f:
    data_test = pickle.load(f, encoding="latin1")

# Классы по варианту.
CLASSES = [17, 70, 35]

train_X_raw = data_train["data"].reshape(-1, 3, 32, 32)
train_X_raw = np.transpose(train_X_raw, [0, 2, 3, 1])  # NCHW -> NHWC
train_y_raw = np.array(data_train["fine_labels"])
mask = np.isin(train_y_raw, CLASSES)
train_X = train_X_raw[mask].copy()
train_y = train_y_raw[mask].copy()
train_y = np.unique(train_y, return_inverse=1)[1]
del data_train

test_X = data_test["data"].reshape(-1, 3, 32, 32)
test_X = np.transpose(test_X, [0, 2, 3, 1])
test_y = np.array(data_test["fine_labels"])
mask = np.isin(test_y, CLASSES)
test_X = test_X[mask].copy()
test_y = test_y[mask].copy()
test_y = np.unique(test_y, return_inverse=1)[1]
del data_test

# print(train_y_raw.tolist())


# %%
def createImage(data: ArrayLike):
    return Image.fromarray(data).resize((256, 256))


# %%
# Source: https://stackoverflow.com/a/47334314
def grid_display(list_of_images, list_of_titles=[], no_of_columns=2, figsize=(10, 10)):
    fig = plt.figure(figsize=figsize)
    column = 0
    for i in range(len(list_of_images)):
        column += 1
        #  check for end of column and create a new figure
        if column == no_of_columns + 1:
            fig = plt.figure(figsize=figsize)
            column = 1
        fig.add_subplot(1, no_of_columns, column)
        plt.imshow(list_of_images[i])
        plt.axis("off")
        if len(list_of_titles) >= len(list_of_images):
            plt.title(list_of_titles[i])


# %%
# По 3 экземпляра класса из выборки.
number_of_images_per_class_to_show = 3

for class_id in CLASSES:
    print(f"{class_id = }:")
    i = number_of_images_per_class_to_show
    image_index_for_class = -1
    class_images = []
    image_indices = []

    while i > 0:
        image_index_for_class = train_y_raw.tolist().index(
            class_id, image_index_for_class + 1
        )
        image_indices.append(image_index_for_class)
        class_images.append(createImage(train_X_raw[image_index_for_class]))
        i -= 1
    grid_display(class_images, image_indices, number_of_images_per_class_to_show)
    plt.show()

# %% [markdown]
# ### Создание Cifar Dataset с аугментацией

# %%
from torch import Tensor  # noqa
from torch.utils.data import Dataset  # noqa


# New:
class CifarDataset(Dataset):
    def __init__(self, X: Tensor, y: Tensor, transform=None, p=0.0):
        assert X.size(0) == y.size(0)
        super(Dataset, self).__init__()
        self.X = X
        self.y = y
        self.transform = transform
        self.prob = p

    def __len__(self):
        return self.y.size(0)

    def __getitem__(self, index):
        X = self.X[index]
        if self.transform and np.random.random() < self.prob:
            X = self.transform(X.permute(2, 0, 1) / 255).permute(1, 2, 0) * 255

        y = self.y[index]

        return X, y


# %% [markdown]
"""
Попробуем применить аугментацию к одной из картинок.
"""

# %%
import torchvision.transforms as T  # noqa

transform = T.Compose(
    [
        T.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.2, hue=0.0),
        # shear - сдвиг.
        T.RandomAffine(degrees=15, translate=(0.1, 0.1), scale=(0.8, 1.2), shear=15),
    ]
)

Image.fromarray(
    (CifarDataset(Tensor(train_X), Tensor(train_y), transform=transform, p=1)[10])[0]
    .numpy()
    .astype(np.uint8)
).resize((256, 256))


# %% [markdown]
# ### Создание Pytorch DataLoader'a


# %%
def create_dataloader(batch_size=128):
    dataloader: dict[str, DataLoader] = {}
    for (X, y), part in zip([(train_X, train_y), (test_X, test_y)], ["train", "test"]):
        tensor_x = torch.Tensor(X)
        tensor_y = (
            F.one_hot(torch.Tensor(y).to(torch.int64), num_classes=len(CLASSES)) / 1.0
        )
        # New: Using CifarDataset.
        dataset = CifarDataset(
            tensor_x, tensor_y, transform=transform if part == "train" else None, p=0.5
        )  # создание объекта датасета
        dataloader[part] = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            # New: prefetch_factor, num_workers and persistent_workers params.
            # prefetch_factor=8 if part == "train" else 2,
            # num_workers=2,
            # persistent_workers=True,
        )  # создание экземпляра класса DataLoader

    return dataloader


# %% [markdown]
# ### Создание Pytorch модели свёрточной нейронной сети


# %%
HIDDEN_SIZE = 64


class Normalize(nn.Module):
    def __init__(self, mean, std):
        super(Normalize, self).__init__()
        self.mean = torch.tensor(mean).to(device)
        self.std = torch.tensor(std).to(device)

    def forward(self, input):
        x = input / 255.0
        x = x - self.mean
        x = x / self.std
        return x.permute(0, 3, 1, 2)  # nhwc -> nm


class GlobalMaxPool2d(nn.Module):
    def __init__(self):
        super(GlobalMaxPool2d, self).__init__()

    def forward(self, input):
        out = F.adaptive_max_pool2d(input, output_size=1)
        return out.flatten(start_dim=1)


class Cifar100_CNN(nn.Module):
    def __init__(self, hidden_size=HIDDEN_SIZE, classes=100):
        super(Cifar100_CNN, self).__init__()
        # https://blog.jovian.ai/image-classification-of-cifar100-dataset-using-pytorch-8b7145242df1
        self.seq = nn.Sequential(
            Normalize([0.5074, 0.4867, 0.4411], [0.2011, 0.1987, 0.2025]),
            nn.Conv2d(3, hidden_size, 5, stride=4, padding=2),
            nn.ReLU(),
            # New
            nn.Dropout2d(p=0.2),
            nn.Conv2d(hidden_size, hidden_size * 2, 3, stride=1, padding=1),
            nn.ReLU(),
            nn.AvgPool2d(4),  # nn.MaxPool2d(4),
            # New
            nn.Dropout2d(p=0.3),
            nn.Flatten(),
            nn.Linear(hidden_size * 8, classes),
        )

    def forward(self, input):
        return self.seq(input)


model = Cifar100_CNN(hidden_size=HIDDEN_SIZE, classes=len(CLASSES))
model.to(device)
print(model(torch.rand(1, 32, 32, 3).to(device)))
summary(model, input_size=(32, 32, 3))
weights = list(model.parameters())[0].detach().numpy()
weights.shape

# %% [markdown]
# ### Создание логов для Tensorboard

# %%
import time  # noqa

from torch.utils.tensorboard import SummaryWriter  # noqa

# %load_ext tensorboard

current_time = str(int(time.time()))

run_path = Path("runs/tensorboard")

train_run_path = run_path / "train" / current_time
test_run_path = run_path / "test" / current_time

train_summary_writer = SummaryWriter(log_dir=train_run_path)
test_summary_writer = SummaryWriter(log_dir=test_run_path)

# %% [markdown]
# ### Обучение модели по эпохам

# %%
REDRAW_EVERY = 20
EPOCHS = 250


def train(
    model: nn.Module,
    criterion: nn.CrossEntropyLoss,
    optimizer: optim.Optimizer,
    dataloader: dict[str, DataLoader],
    scheduler: optim.lr_scheduler.LRScheduler,
    epochs=EPOCHS,
):
    steps_per_epoch = len(dataloader["train"])
    steps_per_epoch_val = len(dataloader["test"])

    pbar = tqdm(total=epochs * steps_per_epoch)
    losses = []
    losses_val = []
    passed = 0
    # Для создания чекпоинта
    best_acc = 0
    checkpoint_path = Path("cifar_cnn_augmented.pth")

    for epoch in range(epochs):  # проход по набору данных несколько раз
        tmp = []
        model.train()
        for i, batch in enumerate(dataloader["train"], 0):
            # получение одного минибатча; batch это двуэлементный список из [inputs, labels]
            inputs, labels = batch

            # очищение прошлых градиентов с прошлой итерации
            optimizer.zero_grad()

            # прямой + обратный проходы + оптимизация
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            # loss = F.cross_entropy(outputs, labels)
            loss.backward()
            optimizer.step()

            # для подсчёта статистик
            accuracy = (
                labels.detach().argmax(dim=-1) == outputs.detach().argmax(dim=-1)
            ).to(torch.float32).mean().cpu() * 100
            tmp.append((loss.item(), accuracy.item()))
            pbar.update(1)

            # New: Запись в tensorboard.
            with train_summary_writer as writer:
                writer.add_scalar("loss", tmp[-1][0], global_step=pbar.n)
                writer.add_scalar("accuracy", tmp[-1][1], global_step=pbar.n)

        losses.append(
            (
                np.mean(tmp, axis=0),
                np.percentile(tmp, 25, axis=0),
                np.percentile(tmp, 75, axis=0),
            )
        )
        # New: Интеграция со scheduler.
        scheduler.step()  # Обновляем learning_rate каждую эпоху.

        tmp = []
        model.eval()
        with torch.no_grad():  # отключение автоматического дифференцирования
            for i, data in enumerate(dataloader["test"], 0):
                inputs, labels = data
                # на GPU
                # inputs, labels = inputs.to(device), labels.to(device)

                outputs = model(inputs)
                loss = criterion(outputs, labels)
                accuracy = (labels.argmax(dim=-1) == outputs.argmax(dim=-1)).to(
                    torch.float32
                ).mean().cpu() * 100
                tmp.append((loss.item(), accuracy.item()))
        losses_val.append(
            (
                np.mean(tmp, axis=0),
                np.percentile(tmp, 25, axis=0),
                np.percentile(tmp, 75, axis=0),
            )
        )
        # New: Запись в tensorboard.
        with test_summary_writer as writer:
            writer.add_scalar("loss", losses_val[-1][0][0], global_step=pbar.n)
            writer.add_scalar("accuracy", losses_val[-1][0][1], global_step=pbar.n)

        # New: Сохранение чекпоинта.
        acc = losses_val[-1][0][1]
        if acc > best_acc:
            best_acc = acc
            torch.save(model.state_dict(), checkpoint_path)

        # Обновление графиков.
        if (epoch + 1) % REDRAW_EVERY != 0:
            continue
        clear_output(wait=False)
        # New:
        print(
            "Эпоха: %s\n"
            "Лучшая доля правильных ответов: %s\n"
            "Текущая доля правильных ответов: %s" % (epoch + 1, best_acc, acc)
        )
        passed += pbar.format_dict["elapsed"]
        pbar = tqdm(total=EPOCHS * steps_per_epoch, miniters=5)
        pbar.update((epoch + 1) * steps_per_epoch)
        x_vals = np.arange(epoch + 1)
        _, ax = plt.subplots(1, 2, figsize=(15, 5))
        stats = np.array(losses)
        stats_val = np.array(losses_val)
        ax[1].set_ylim(stats_val[:, 0, 1].min() - 5, 100)
        ax[1].grid(axis="y")
        for i, title in enumerate(["CCE", "Accuracy"]):
            ax[i].plot(x_vals, stats[:, 0, i], label="train")
            ax[i].fill_between(x_vals, stats[:, 1, i], stats[:, 2, i], alpha=0.4)
            ax[i].plot(x_vals, stats_val[:, 0, i], label="val")
            ax[i].fill_between(
                x_vals, stats_val[:, 1, i], stats_val[:, 2, i], alpha=0.4
            )
            ax[i].legend()
            ax[i].set_title(title)
        plt.show()

    # New:
    model.load_state_dict(torch.load(checkpoint_path))
    print("Обучение закончено за %s секунд" % passed)

    return dataloader


# %%
# Запуск tensorboard в Jupyter Notebook.
# %tensorboard --logdir runs/tensorboard

# %% [markdown]
# ### Выбор функции потерь и оптимизатора градиентного спуска


# %%
# New: weight_decay, label_smoothing, scheduler_step_size.
def train_classifier(
    model: nn.Module,
    learning_rate=5e-3,
    batch_size=128,
    epochs=EPOCHS,
    momentum=0.9,
    # Регуляризация модели за счёт коэффициента, учитывающего сложность модели.
    # Норма параметров будет прибавлена к функции потерь. Чем больше
    # weight_decay, тем сильнее штраф за сложность.
    weight_decay=1e-5,
    # Добавляем сглаживание целевых меток, это увеличит значение функции потерь
    #   но полученная модель будет более устойчивой к выбросам в обучающей выборке.
    label_smoothing=0.1,
    # Постепенное уменьшение шага обучения каждые N эпох.
    scheduler_step_size=240,
):
    # New: label_smoothing
    criterion = nn.CrossEntropyLoss(label_smoothing=label_smoothing)
    # New: weight_decay
    optimizer = optim.SGD(
        model.parameters(),
        lr=learning_rate,
        momentum=momentum,
        weight_decay=weight_decay,
    )
    dataloader = create_dataloader(batch_size=batch_size)
    # New: scheduler.
    # Добавляем постепенное уменьшение шага обучения каждые step_size
    #   эпох.
    scheduler = optim.lr_scheduler.StepLR(
        optimizer=optimizer, step_size=scheduler_step_size, gamma=0.5
    )

    return train(
        model,
        criterion=criterion,
        optimizer=optimizer,
        dataloader=dataloader,
        epochs=epochs,
        scheduler=scheduler,
    )


dataloader = train_classifier(model)

# %% [markdown]
# ### Проверка качества модели по классам на обучающей и тестовой выборках


# %%
def report_classification_results(dataloader: DataLoader):
    y_pred = []
    y_true = []
    with torch.no_grad():  # отключение автоматического дифференцирования
        for _, data in enumerate(dataloader, 0):
            inputs, labels = data
            # на GPU
            # inputs, labels = inputs.to(device), labels.to(device)

            outputs = model(inputs).detach().cpu().numpy()
            y_pred.append(outputs)
            y_true.append(labels.numpy())
        y_true = np.concatenate(y_true)
        y_pred = np.concatenate(y_pred)
        print(
            classification_report(
                y_true.argmax(axis=-1),
                y_pred.argmax(axis=-1),
                digits=4,
                target_names=list(map(str, CLASSES)),
            )
        )


# %%
def compare_classification_reports(dataloader: dict[str, DataLoader]):
    for part in ["train", "test"]:
        print(part)
        report_classification_results(dataloader[part])
        part != "test" and print("-" * 53)


# %%
compare_classification_reports(dataloader)

# %% [markdown]
"""
### Анализ результатов обучения модели
В предыдущей модели (с MaxPulling) была довольно высокая точность и скорость обучения,
однако модель была склонна к переобучению.

Регуляризация с помощью аугментации изображений, dropout, label smoothing
и weight decay дали свои плоды: переобучение ушло, при этом точность модели
улучшилась на 2% по сравнению с лучшей версией модели
второй лабораторной работы.

К сожалению, взамен длительность обучения возросла в 5 раз.
"""

# %% [markdown]
"""
На лицо так же переобучение: в обучающей выборке характеристики были почти идеальными,
а в тестовых данных для некоторых классов средними. Скорректируем параметры для устранения
этого феномена в надежде улучшить качество модели.
"""

# %% [markdown]
# Подберём количество эпох.

# %%
model = Cifar100_CNN(hidden_size=HIDDEN_SIZE, classes=len(CLASSES))
dataloader = train_classifier(model, epochs=30)
compare_classification_reports(dataloader)

# %% [markdown]
# ## Экспорт модели

# %%
model_path = Path("models")
model_filename = "cifar100_cnn_augmented.pt"

model_path.mkdir(exist_ok=True)

model_file_path = model_path / model_filename

torch.save(model, model_file_path)
# загрузка
new_model_2 = torch.load(model_file_path)
new_model_2.eval()

# %%
# входной тензор для модели
onnx_model_filename = "cifar100_cnn_augmented.onnx"
x = torch.randn(1, 32, 32, 3, requires_grad=True).to(device)
torch_out = model(x)

# экспорт модели
torch.onnx.export(
    model,  # модель
    x,  # входной тензор (или кортеж нескольких тензоров)
    model_path
    / onnx_model_filename,  # куда сохранить (либо путь к файлу либо fileObject)
    export_params=True,  # сохраняет веса обученных параметров внутри файла модели
    opset_version=9,  # версия ONNX
    do_constant_folding=True,  # следует ли выполнять укорачивание констант для оптимизации
    input_names=["input"],  # имя входного слоя
    output_names=["output"],  # имя выходного слоя
    dynamic_axes={
        "input": {
            0: "batch_size"
        },  # динамичные оси, в данном случае только размер пакета
        "output": {0: "batch_size"},
    },
)
