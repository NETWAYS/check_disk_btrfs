.PHONY: lint test

lint:
	python -m pylint check_disk_btrfs
test:
	python -m unittest -v
