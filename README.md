# Prabodha

Run Ollama locally on macOS:

```bash
ollama serve
```

If the backend runs on your Mac, use `AI_ENGINE_URL=http://localhost:11434`.
If the backend runs inside Docker and Ollama runs on your Mac, use `AI_ENGINE_URL=http://host.docker.internal:11434`.

The Docker stack now only brings up Postgres and the media volume helper. Ollama is expected to run on the host.
