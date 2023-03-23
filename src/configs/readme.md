# Конфиги для обучения
Во всех конфигах используется DIET классификации для intent'ов и классификатор entities по регулярным выражениям 
## simple_conf.yml
Конфиг без языковых моделей

## spacy_conf.yml
Конфиг использует модель spacy ru_core_news_md. Также увеличено количество эпох

## rule_basad_conf.yml
spacy конфиг, но без обучения историям, нужно дополнительно указать файл с дополнительными правилами [rules.yml](..%2Fdata_rule_based%2Frules.yml)

## bert_conf.yml
Конфиг для модели bert Geotrend/bert-base-en-ru-cased, rasa загружает веса только из моделей tensorflow. pytorch модели сначала надо переделать в tf.  
Увеличено количество слоев трансформера с 2 до 4, во всех нс отбрасываются меньше связей 50%, вместо 80%.