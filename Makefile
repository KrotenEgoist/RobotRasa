all: train test

# Обучение моделей rasa
train: models/model_base.tar.gz

# Базовая модель для проверки работоспособности
models/model_base.tar.gz: src/data/base/nlu.yml src/data/base/rules.yml src/data/base/stories.yml src/configs/config_base.yml src/data/base/domain.yml
	rasa train \
		--data src/data/base \
		--config src/configs/config_base.yml \
		--domain src/data/base/domain.yml \
		--endpoints src/data/base/endpoints.yml \
		--out models \
		--fixed-model-name model_base

# Тест моделей rasa
test:  results/model_base_core results/model_base_nlu_cross results/model_base_nlu

# Тест историй base
results/model_base_core: src/tests/base/test_stories.yml src/data/base/endpoints.yml models/model_base.tar.gz
	rasa test core \
		--stories src/tests/base/test_stories.yml \
		--endpoints src/data/base/endpoints.yml \
		--model models/model_base.tar.gz \
		--out results/model_base_core

# Кросс валидация base
results/model_base_nlu_cross: src/data/base/nlu.yml src/data/base/domain.yml src/configs/config_base.yml
	rasa test nlu \
		--nlu src/data/base/nlu.yml \
		--domain src/data/base/domain.yml \
		--config src/configs/config_base.yml \
		--cross-validation \
		--folds 2 \
		--out results/model_base_nlu_cross

# Стандартный тест с разделением выборки на train/test base
src/train_test_split/base/test_data.yml: src/data/base/nlu.yml
	rasa data split nlu \
		--nlu src/data/base/nlu.yml \
		--random-seed 42 \
		--out src/train_test_split/base

results/model_base_nlu: src/train_test_split/base/test_data.yml src/data/base/domain.yml src/configs/config_base.yml models/model_base.tar.gz
	rasa test nlu \
		--nlu src/train_test_split/base/test_data.yml \
		--domain src/data/base/domain.yml \
		--config src/configs/config_base.yml \
		--model models/model_base.tar.gz \
		--out results/model_base_nlu

# Очистка проекта
clean:
	rm -rf .rasa
	rm -rf models
	rm -rf results
	rm -rf src/train_test_split
