import pytest

from kwwutils import __version__
from kwwutils import clock, get_llm, printit
from ollama_downloads.ollama_downloads_process import OllamaModels



@clock
def test_version():
    llm_type = "llm"
    model = "openhermes"
    temperature = 0.1
    options = {}
    options["model"] = model
    options["temperature"] = temperature
    options["llm_type"] = llm_type
    printit("version", __version__)
    printit("options", options)
    assert __version__ == "0.1.1"
    llm = get_llm(options)
    printit("llm", llm)
    assert llm.temperature == temperature
    assert llm.model == model


@clock
def test_ollama():
    options = {}
    options["default_concur_req"] = 10
    options["max_concur_req"] = 10
    options["url"] = "https://ollama.com/library"
    options["models_dir"] = "models"
    ollama_models = OllamaModels(options)
    ollama_models.models(options["default_concur_req"], options["max_concur_req"])
    ollama_models.close_browser()
