
# Yolov5 Coffee Detector
 
 ## 1) Начало работы.
 
 ```git
 git clone https://github.com/JutsFunFor/yolov5-main
 ```
 ```
 git clone https://github.com/Kashu7100/pytorch-armv7l
 ```
 ## 2) Установка зависимостей:
 

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

## 4) Проверка работоспособности. 
Выполнение этих программ не должно вызывать ошибку.
```
cd //home/pi/yolov5-main
```
```python
python3 inference.py
python3 yolov5_client.py
```

Для правильной работы сервиса необходимо проверить путь, указанный для выполнения программ.

```bash
nano yolov5.service
```

![image](https://user-images.githubusercontent.com/43553016/165237122-f159b376-d3bd-4bc2-8afa-ff032fdda742.png)


Обращаем внимание на WorkingDerictory - путь, в котором лежат файлы inference.py & yolov5_client.py

## 5) Установка и запуск сервиса.
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

После приготовления напитка появляется подобный вывод в статусе сервиса. Это говорит об успешном запуске программы.

![image](https://user-images.githubusercontent.com/43553016/163826169-26d7c0fb-0ea6-43f9-a59b-910adda0ad92.png)

## 6) Оценка результатов работы.

Результаты работы записываются в файл json_pred.json, в котором агрегирована информация о текущем заказе.
```bash
cat json_pred.json
```

![image](https://user-images.githubusercontent.com/43553016/163827088-b1f25468-8c9d-4a9f-944e-a25903a00423.png)

Также результаты работы передаются в топик "Coffee.core.detection" NATS-сервера.

