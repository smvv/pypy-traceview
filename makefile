PYTEST_FLAGS := -q --maxfail 1

test:
	pipenv run pytest $(PYTEST_FLAGS)

watch:
	pipenv run ptw -q --clear -- $(PYTEST_FLAGS)
