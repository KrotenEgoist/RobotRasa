# RobotRasa
Интерфейс для распознавания команд робота основанный на фреймворке для создания чат-ботов Rasa.
Перенаправляет распознанные команды на парсер команд.
# Установка
Окружение Anaconda:
```shell
conda env create -f conda_env/rasa_dev.yml
```
# Обучение и тестирование моделей
Подробнее в Makefile \
Обучение и оценка моделей
```shell
make -f Makefile
```
Очистка проекта
```shell
make -f Makefile clean
```
# Структура проекта
### conda_env
YAML файлы для окружений Anaconda
### models
Rasa модели в формате *.tar.gz
### results
Результаты тестирования обученных rasa моделей. Возможно 3 варианта тестов:
1. core - тестирование stories
2. nlu - стандартное разбиение обучающих данных на train/test
3. nlu_cross - кросс валидация с указанием количества фолдов
### src
YAML и python файлы необходимые для обучения и инференса моделей rasa, содержит:
- actions - описание действий на intent пользователя
- configs - конфигурации моделей rasa
- data - обучающие данные rasa
- tests - тестовые истории для оценки core
- train_test_split - тестовые данные для оценки nlu

# Оформление проекта на примере base
```text
RobotRasa
├── conda_env
├── models
│   └── model_base.tar.gz
├── results
│   ├── model_base_core
│   ├── model_base_nlu
│   └── model_base_nlu_cross
└── src
    ├── actions
    │   └── base
    │       └── actions.py
    ├── configs
    │   └── config_base.yml
    ├── data
    │   └── base
    │       ├── credentials.yml
    │       ├── domain.yml
    │       ├── endpoints.yml
    │       ├── nlu.yml
    │       ├── rules.yml
    │       └── stories.yml
    ├── tests
    │   └── base
    │       └── test_stories.yml
    └── train_test_split
        └── base
├── Makefile
├── README.md
└── requirements.txt
```
