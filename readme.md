# RobotRasa
Интерфейс для распознавания команд робота основанный на фреймворке для создания чат-ботов Rasa.
Перенаправляет распознанные команды на парсер команд.
# Установка Rasa и зависимостей
Установка Rasa:
```
pip install rasa
```
Если хотите использовать конфигурацию spacy:
```
pip install "rasa[spacy]"
```
Также придется установить модель:
```
python -m spacy download ru_core_news_md
```
Чтобы использовать трансформеры, нужен python 3.7 или 3.8, также нужно их поставить:
```
pip install "rasa[transformers]"
```
# Запуск и использование
Создать проект Rasa с примером moodbot: 
```
rasa init
```
Можно использовать для создания структуры проекта и дальнейшего редактирования файлов.

Обучение:
```
rasa train -c [путь до yml файла конфига]
```
Для обучения только на правилах, нужно пропустить файл с историями:
```
rasa train -c configs/rule_based_conf.yml --data data/nlu.yml data/rules.yml data_rule_based/rules.yml
```
Запуск сервера для кастомных actions:
```
rasa run actions
```
Запуск консольного интерфейса:
```
rasa shell
```
Запуск http сервера Rasa:
```
rasa run
```
Формат POST запросов json:
```json
{"sender": "user", "message": "команда"}
```
отправлять на http://[ip_addr]:[port]/webhooks/rest/webhook/
# Структура проекта
- [data](src/data) и [data_rule_based](src/data_rule_based) - данные для обучения
- [configs](src/configs) - конфигурации обучения
- [tests](src/tests) - тестовые историями
- [actions](src/actions) - кастомные actions
- [credentials.yml](src/credentials.yml) - конфигурация серверов для обмена сообщениями (rasa run запускает rest api сервер)
- [endpoints.yml](src/endpoints.yml) - конфигурация эндпоинтов (сюда пишется сервер кастомных actions)

Подробнее в каждой директории

# Окружение
Если не работает с GPU:
- поставить cudatoolkit, cdnn
- установить переменную окружения:
    ```
  export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/
    ```