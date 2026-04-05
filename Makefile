.PHONY: build publish clean

# Build distribution packages
build: clean
	python -m build

# Upload to PyPI (run `make build` first or use `make publish`)
upload:
	twine upload dist/*

# Clean, build, and upload in one step
publish: build upload

# Remove build artifacts
clean:
	rm -rf dist/ build/ *.egg-info
