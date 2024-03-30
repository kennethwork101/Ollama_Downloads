# Pre-requsite is python, ollama, git, poetry

# ollama-downloads
Download models from  https://ollama.com/library'

https://ollama.com/download

1. Install Dependencies

ollama:
curl -fsSL https://ollama.com/install.sh | sh

poetry:
curl -sSL https://install.python-poetry.org | python3 -

2. Clone the repo
https://github.com/kennethwork101/ollama-downloads.git

3. Install kwwutils
cd ollama-downloads
poetry install

4. Run test script to download models from ollama
poetry shell
cd src/ollama_downloads
python ollama_downloads_process.py
python ollama_downloads_process.py --models  openhermes:latest
python ollama_downloads_process.py --models  "openhermes:latest,mistral:latest,llama2:latest,openchat:latest"
