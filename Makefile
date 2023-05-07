.PHONY: lint test coverage

lint:
	python -m pylint check_disk_btrfs.py
test:
	python -m unittest -v -b test_check_disk_btrfs.py
coverage:
	python -m coverage run -m unittest test_check_disk_btrfs.py
	python -m coverage report -m --include check_disk_btrfs.py
