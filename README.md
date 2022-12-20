
# Yolov5 Coffee Detector :robot:
 
 ## 1) Начало работы
 
 ```git
 git clone https://github.com/JutsFunFor/yolov5-main
 ```
 ```
 git clone https://github.com/Kashu7100/pytorch-armv7l
 ```
 ## 2) Установка зависимостей

Завариваем :coffee: и прописываем в консоль:


```
cd //home/pi/yolov5-main
chmod +x setup_libs.sh
chmod +x yolov5-reload.sh
sh setup_libs.sh
cd //home/pi
```

```
unzip pytorch-armv7l.zip
rm pytorch-armv7l.zip
```

```
export PATH="$HOME/.local/bin:$PATH"
cd //home/pi/pytorch-armv7l
pip3 install torch-1.7.0a0-cp37-cp37m-linux_armv7l.whl
pip3 install torchvision-0.8.0a0+45f960c-cp37-cp37m-linux_armv7l.whl
cd ..
```
## 3) Установка PostgreSQL (опционально)
```
sudo su postgres
createuser pi -P --interactive
```
Вводим пароль: ```3vn4ssps```
Shall the new role be a superuser? (y/n) y

## 4) Проверка работоспособности 
Выполнение этих программ не должно вызывать ошибку :pray:
```
cd //home/pi/yolov5-main
```
```python
python3 inference.py
python3 yolov5_client.py
```
:warning:В настройках роутера устанавливаем статический IP-адрес камеры. По умолчанию, адрес 192.168.1.22 закреплен за cm-камерой

Выставляем  inference-параметры в файле конфигурации `config.json`

<img width="460" alt="Screenshot 2022-09-12 at 13 47 09" src="https://user-images.githubusercontent.com/43553016/189635352-997966d9-2fe4-4a8a-b3e2-35e3c8c7799c.png">

:white_check_mark:`modelPath` - название модели, если модель в другом расположении, то можно указать путь

:white_check_mark:`rstpAddress` -  адрес rtsp сервера. rtsp://login:password:IP:port

:white_check_mark:`threshold` - порог предикта

:white_check_mark:`iouThreshold` - порог iou метрики

:white_check_mark:`latteMenuItemId` - параметр, необходимый для предобработки латте и применения CLAHE 

:white_check_mark:`natsUrl` -  дефолтный адрес 

:white_check_mark:`sendResultsTopic` - топик для отправления результатов детекции

:white_check_mark:`dbname, usr, pwd, host` - опционально (PostgreSQL). Нужно раскоментить строки (28-38) & (59-60) в yolov5_client.py для записи в БД.


Выставляем crop-параметры в файле конфигурации `config.json`

<img width="445" alt="Screenshot 2022-09-12 at 13 46 33" src="https://user-images.githubusercontent.com/43553016/189635340-e81c22be-7ec4-4672-94f5-0f1b616d2f16.png">


:white_check_mark:`pixelCoeff` -  параметр, отображаюший количетсво мм в одном пикселе. Для разных комплексов и групп он разный, вычисляется однократно эмпирически при отладке.


:white_check_mark:`clipLimit` - параметр, необходимый для предобработки изображения (CLAHE), содержащего класс "Латте". Для разных комплексов и групп он разный, вычисляется эмпирически при отладке в зависимости от условий освещения.


Параметры `yCropMin, yCropMax, xCropMin, xCropMax` - параметры, определяющие границы изображения на входе в детектор.

Установим эти параметры. 
Выбираем изображение с камеры. При этом, разрешение загружаемого изображения должно равняться разрешению изображению, снятому с камеры посредством скрипта, поскольку Fluent & Clear изображения из клиента Reolink могут давать другие разрешения.  

Для этого смотрим разрешение в настройках камеры или произведем пинг камеры внутри комплекса
с помощью скрипта `camera-ping.py`


```
cd //home/pi/yolov5-main
python3 camera-ping.py
```

<img width="462" alt="Screenshot 2022-09-12 at 14 21 19" src="https://user-images.githubusercontent.com/43553016/189641354-132dcde5-5990-4ee0-986a-361faf307b78.png">

Сохраняем изображение в клиенте Reolink :arrow_right: Resize :arrow_right: Crop

Resize - https://www.iloveimg.com/resize-image

Crop - https://www.iloveimg.com/crop-image

<img width="1280" alt="Screenshot 2022-09-12 at 14 53 28" src="https://user-images.githubusercontent.com/43553016/189648110-b4e7a0d5-4025-4ae6-9318-daef11846f64.png">

Пример для `nozzleId0`:
<img width="1280" alt="Screenshot 2022-09-12 at 15 03 20" src="https://user-images.githubusercontent.com/43553016/189649106-c214e07b-32f3-4a75-970a-33c5d4a1926e.png">

:white_check_mark:`yCropMin` = 653

:white_check_mark:`yCropMax` = 653 + 643 = 1296 

:white_check_mark:`xCropMin` = 320

:white_check_mark:`xCropMax` = 320 + 493 = 813

:underage:Коэффициенты зависят от положения камеры :arrow_right: меняем положение камеры = меняем коэффициенты
 
Пути сохранения сырых изображений, предиктов, результатов соответственно:

:white_check_mark:`rawImagesSavePath` 

:white_check_mark:`predictionImagesSavePath`

:white_check_mark:`saveJsonResultsPath`


Для правильной работы сервиса необходимо проверить путь, указанный для выполнения программ.

```bash
nano yolov5.service
```
<img width="335" alt="Screenshot 2022-09-12 at 13 31 12" src="https://user-images.githubusercontent.com/43553016/189632662-2bf4dac2-7a43-4869-b2bb-5b5ef46c34ad.png">

Обращаем внимание на WorkingDerictory - путь, в котором лежат файлы inference.py & yolov5_client.py

## 5) Установка и запуск сервиса :rocket:
```bash
sudo mv yolov5.service /etc/systemd/system
```
Можно запустить в командной строке 
```
cd //home/pi/yolov5-main
sh yolov5-reload.sh 
```
или выполнить следующие команды:
```
sudo systemctl daemon-reload
sudo systemctl stop yolov5.service
sudo systemctl start yolov5.service
sudo systemctl status yolov5.service
```
```
sudo journalctl -u yolov5.service -b -e
```
## 6) Common usage

При запуске сервиса из пункта 5 скрипт начинает слушать NATS topic, указанный в файле конфигурации. При поступлении сигнала о конце приготовления напитка и nozzleID - скрипт снимает изображение, обрезает согласно nozzleID и кормит его на вход нейросети. Формируется ответ, который сохраняется в файл `saveJsonResultsPath`, указанный в конфигурации. Помимо этого, сохраняются как сырые изображения, так и изображения с предиктом объектов - `rawImagesSavePath`, `predictionImagesSavePath`. 
Формат ответа выглядит следующим образом:
```
"{'Detection': {'Coffee': {'Xmax': '389.0', 'Ymax': '138.0', 'Ymin': '272.0', 'Score': '0.95'},
'CupTop': {'Xmax': '459.0', 'Ymax': '26.0', 'Ymin': '290.0', 'Score': '0.97'}},
'OrderId': '01G5757AKN9KVXABD1NX7AZSVG',
'OrderNumber': '463',
'NozzleId': '1',
'MenuItemId': '01G3GVZX2YW4WXEJNG2P1ZT3G1',
'DateTime': '2022-06-10 18:56:59',
'Capture_duration': '1.94',
'Inference_duration': '2.74',
'Save_img_duration': '0.08',
'Total_time': '4.76',
'RealDistance': '26.53'}"
```
