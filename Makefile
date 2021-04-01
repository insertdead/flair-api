format:
	@printf 'formatting...\n'
	isort .
	black flair-client/ tests/
	@printf '\nDone!\n'

build:
	poetry build

publish: build
	poetry publish
