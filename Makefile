.PHONY: build publish clean gen-index

# Regenerate presets/index.json from all preset manifests
gen-index:
	python -c "from mcp2cli.preset.exporter import rebuild_index; rebuild_index('presets')"

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
