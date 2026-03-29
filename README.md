### run api:-

```bash
cd api
uv venv
uv pip install -r pyproject.toml
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

