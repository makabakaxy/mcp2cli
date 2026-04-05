def safe_filename(name: str) -> str:
    """Replace characters unsafe for filenames (e.g. '/') with '--'."""
    return name.replace("/", "--")