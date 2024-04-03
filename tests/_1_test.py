import pytest
import sys

from kwwutils import clock, get_llm, printit
from ollama_downloads.ollama_downloads_process import OllamaModels


@clock
def test_ollama_one(options, model):

    package_root = sys.path[0]
    printit("1 package_root", package_root)
    printit("1 options", options)
    options["default_concur_req"] = 10
    options["max_concur_req"] = 10
    options["url"] = "https://ollama.com/library"
    options["models_dir"] = f"{package_root}/models"
    options["models"] = "openhermes:latest"
    printit("2 options", options)
    ollama_models = OllamaModels(options)
    ollama_models.download_models()


@clock
def test_ollama_all(options, model):
    package_root = sys.path[0]
    printit("1 package_root", package_root)
    printit("1 options", options)
    options["default_concur_req"] = 10
    options["max_concur_req"] = 10
    options["url"] = "https://ollama.com/library"
    options["models_dir"] = f"{package_root}/models"
    options["models"] = None
    printit("2 options", options)
    ollama_models = OllamaModels(options)
    ollama_models.download_models()
