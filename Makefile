all: train test

# Обучение моделей rasa
train: models/model_base.tar.gz

# Базовая модель для проверки работоспособности
models/model_base.tar.gz: src/data/rules.yml src/data/stories.yml src/configs/config_base.yml src/domain
	rasa train \
		--data src/data \
		--config src/configs/config_base.yml \
		--domain src/domain \
		--endpoints src/endpoints.yml \
		--out models \
		--fixed-model-name model_base

# Тест моделей rasa
test:  results/model_base_core results/model_base_nlu_cross results/model_base_nlu

# Тест историй base
results/model_base_core: src/tests/test_stories.yml src/endpoints.yml models/model_base.tar.gz
	rasa test core \
		--stories src/tests/test_stories.yml \
		--endpoints src/endpoints.yml \
		--model models/model_base.tar.gz \
		--out results/model_base_core

# Кросс валидация base
results/model_base_nlu_cross: src/domain src/configs/config_base.yml
	rasa test nlu \
		--nlu src/data \
		--domain src/domain \
		--config src/configs/config_base.yml \
		--cross-validation \
		--folds 4 \
		--out results/model_base_nlu_cross

# Стандартный тест с разделением выборки на train/test base
src/train_test_split/base/test_data.yml:
	rasa data split nlu \
		--nlu src/data \
		--random-seed 42 \
		--out src/train_test_split/base

results/model_base_nlu: src/train_test_split/base/test_data.yml src/domain src/configs/config_base.yml models/model_base.tar.gz
	rasa test nlu \
		--nlu src/train_test_split/base/test_data.yml \
		--domain src/domain \
		--config src/configs/config_base.yml \
		--model models/model_base.tar.gz \
		--out results/model_base_nlu

# Очистка проекта
clean:
	rm -rf .rasa
	rm -rf models
	rm -rf results
	rm -rf src/train_test_split
