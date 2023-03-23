# Тесты

## Тест историй
В test_stories.yml записываются тестовые истории, то что приходит и какой ожидаем ответ действие.

Тест историй
```
rasa test core --stories tests/test_stories.yml --out results
```

## Тест NLU
Есть две возможности
### Hold-out 
Перетасовать и разделить данные на обучающие и тренировочные:
```
rasa data split nlu
```
Далее запустить:
```
rasa test nlu --nlu train_test_split/test_data.yml
```
### Кросс-валидация
Для кросс-валидации запустить:
```
rasa test nlu \
    --nlu data/nlu \
    --cross-validation \
    --folds 4
```
Для теста определенного пайплайна, нужно указать ключ -c с параметром файла конфигурации, пример:
```
rasa test nlu -c configs/simple_conf.yml \
    --cross-validation \
    --folds 4 \
    --out results/simple-nlu 
```