
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
cd ..
```

```
unzip pytorch-armv7l.zip
rm pytorch-armv7l.zip
```

```
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
Выполнение этих программ не должно вызывать ошибку.
```
cd //home/pi/yolov5-main
```
```python
python3 inference.py
python3 yolov5_client.py
```
В настройках роутера устанавливаем статический IP-адрес камеры

Выставляем  inference-параметры в файле конфигурации `config.json`

<img width="460" alt="Screenshot 2022-09-12 at 13 47 09" src="https://user-images.githubusercontent.com/43553016/189635352-997966d9-2fe4-4a8a-b3e2-35e3c8c7799c.png">

`modelPath` - название модели, если модель в другом расположении, то можно указать путь
`rstpAddress` -  адрес rtsp сервера. rtsp://login:password:IP:port
`threshold` - порог предикта
`iouThreshold` - порог iou метрики
`latteMenuItemId` - параметр, необходимый для предобработки латте и применения CLAHE 
`natsUrl` -  дефолтный адрес 
`sendResultsTopic` - топик для отправления результатов детекции
`dbname, usr, pwd, host` - опционально (PostgreSQL). Нужно раскоментить строки (28-38) & (59-60) в yolov5_client.py для записи в БД.


Выставляем crop-параметры в файле конфигурации `config.json`

<img width="445" alt="Screenshot 2022-09-12 at 13 46 33" src="https://user-images.githubusercontent.com/43553016/189635340-e81c22be-7ec4-4672-94f5-0f1b616d2f16.png">


`pixelCoeff` -  параметр, отображаюший количетсво мм в одном пикселе. Для разных комплексов и групп он разный, вычисляется однократно эмпирически при отладке.


`clipLimit` - параметр, необходимый для предобработки изображения, содержащего класс "Латте". Для разных комплексов и групп он разный, вычисляется эмпирически при отладке в зависимости от условий освещения.


Параметры `yCropMin, yCropMax, xCropMin, xCropMax` - параметры, определяющие границы изображения на входе в детектор.

Установим эти параметры. 
Выбираем изображение с камеры. При этом, разрешение загружаемого изображения должно равняться разрешению изображению, снятому с камеры посредством скрипта, поскольку Fluent & Clear изображения из клиента Reolink могут давать другие разрешения.  

Для этого смотрим разрешение в настройках камеры или произведем пинг камеры внутри комплекса с помощью скрипта `camera-ping.py`

```
cd //home/pi/yolov5-main
python3 camera-ping.py
```

<img width="462" alt="Screenshot 2022-09-12 at 14 21 19" src="https://user-images.githubusercontent.com/43553016/189641354-132dcde5-5990-4ee0-986a-361faf307b78.png">

Сохраняем изображение в клиенте Reolink -> Resize https://www.iloveimg.com/resize-image

<img width="1280" alt="Screenshot 2022-09-12 at 14 53 28" src="https://user-images.githubusercontent.com/43553016/189648110-b4e7a0d5-4025-4ae6-9318-daef11846f64.png">

Resize -> Crop https://www.iloveimg.com/crop-image

Пример для nozzleId0:

Устанавливаем коэффициенты
<img width="1280" alt="Screenshot 2022-09-12 at 15 03 20" src="https://user-images.githubusercontent.com/43553016/189649106-c214e07b-32f3-4a75-970a-33c5d4a1926e.png">

`yCropMin` = 653

`yCropMax` = 653 + 643 = 1296 

`xCropMin` = 320

`xCropMax` = 320 + 493 = 813

Коэффициенты зависят от положения камеры -> меняем положение камеры = меняем коэффициенты
 
 Пути сохранения сырых изображений, предиктов, результатов соответственно:

`rawImagesSavePath` 
`predictionImagesSavePath`
`saveJsonResultsPath`


Для правильной работы сервиса необходимо проверить путь, указанный для выполнения программ.

```bash
nano yolov5.service
```
<img width="335" alt="Screenshot 2022-09-12 at 13 31 12" src="https://user-images.githubusercontent.com/43553016/189632662-2bf4dac2-7a43-4869-b2bb-5b5ef46c34ad.png">

Обращаем внимание на WorkingDerictory - путь, в котором лежат файлы inference.py & yolov5_client.py

## 5) Установка и запуск сервиса 
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

