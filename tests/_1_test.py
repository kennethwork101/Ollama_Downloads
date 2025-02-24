import pytest

from kwwutils import clock, get_llm, printit
from uvprog2025.Ollama_Downloads.src.ollama_downloads.ollama_downloads_process import OllamaModels

@pytest.mark.testme
@clock
def test_ollama_one(options, model):
    printit("1 options", options)
    options["default_concur_req"] = 10
    options["max_concur_req"] = 10
    options["url"] = "https://ollama.com/library"
    options["models_dir"] = f".ollama_downloads/models"
    options["models"] = "openhermes:latest"
    printit("2 options", options)
    ollama_models = OllamaModels(options)
    ollama_models.download_models()


@clock
def test_ollama_all(options, model):
    printit("1 options", options)
    options["default_concur_req"] = 10
    options["max_concur_req"] = 10
    options["url"] = "https://ollama.com/library"
    options["models_dir"] = f".ollama_downloads/models"
    options["models"] = None
    printit("2 options", options)
    ollama_models = OllamaModels(options)
    ollama_models.download_models()
