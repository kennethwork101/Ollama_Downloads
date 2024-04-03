#!/usr/bin/env python

import argparse
import inspect
import json
import os
import re
import subprocess
from collections import Counter, namedtuple
from concurrent.futures import ProcessPoolExecutor, as_completed
from enum import Enum
from pprint import pformat

import tqdm
from kwwutils import clock, printit
from selenium import webdriver
from selenium.webdriver.common.by import By

DownloadStatus = Enum('DownloadStatus', 'OK NOT_FOUND ERROR')


def _download_one(model, verbose):
    name_ = f"{inspect.currentframe().f_code.co_name}"
    cmd = "ollama pull"
    command = f"{cmd} {model}"
    print(command)
    result = subprocess.check_output([command], shell=True)
    print(f"{name_} result: {result}")


@clock
class OllamaModels:
    @clock
    def __init__(self, options):
        self.name_ = self.__class__.__name__
        name_ = f"{self.name_}: {inspect.currentframe().f_code.co_name}"
        self.options = options
        self.url = options["url"]
        self.driver = webdriver.Chrome()
        self.driver.get(self.url)
        print(f"{name_} url {self.driver.current_url}")
        print(f"{name_} title {self.driver.title}")
        assert self.driver.title == "library", f"-error: {name_} bad title {self.driver.title}"
        home_dir = os.path.expanduser("~")
        self.models_dir = os.path.join(home_dir, options["models_dir"])
        if not os.path.exists(self.models_dir):
            os.makedirs(folder_path)

    @clock
    def __del__(self):
        name_ = f"{self.name_}: {inspect.currentframe().f_code.co_name}"
        print(f"{name_} exiting")
        self.close_browser()

    @clock
    def close_browser(self):
        name_ = f"{self.name_}: {inspect.currentframe().f_code.co_name}"
        print(f"{name_} exiting")
        self.driver.quit()

    @clock
    def download_models(self):
        name_ = f"{self.name_}: {inspect.currentframe().f_code.co_name}"
        repo = self.driver.find_element(By.ID, "repo")
        printit(f"{name_} repo", repo)
        links = repo.find_elements(By.XPATH, "//li/a[@href]")
        PAT_RE = re.compile(rf"^{self.url}/(\S+)$")
        models = sorted([re.findall(PAT_RE, link.get_attribute("href"))[0] for link in links])
#       printit(f"{name_} models", models)
        self.concur_req = min(self.options['default_concur_req'], self.options['max_concur_req'], len(models))
        printit("{name_} concur_req", self.concur_req)
        models = [m for m in models if m not in ["wizardlm"]]
        self._get_models_info(models)
        if self.options["models"] is not None:
            models = self.options["models"].split(",")
            print(f"{name_} models {models}")
            self._download_many(models)
            if len(models) == 1:
                fname = "models_one.txt"
                fdata = [data for data in self.models_data if data['model'] == models[0]]
                self._save_file(fname, fdata)
            else:
                fname = "models_few.txt"
                fdata = [data for data in self.models_data for model in models if data['model'] == model]
                self._save_file(fname, fdata)

        else:
            self._download_all_models(models)

    @clock
    def _download_all_models(self, models):
        # Download all models files from Ollama
        self._download_many(models)
        # Save models file info to disk
        self._save_all_models_file(models)

    @clock
    def _download_many(self, models):
        name_ = f"{self.name_}: {inspect.currentframe().f_code.co_name}"
        verbose = True
        counter: Counter[DownloadStatus] = Counter()
        with ProcessPoolExecutor(max_workers=self.concur_req) as executor:
            to_do_map = {}
            for model in sorted(models):
                future = executor.submit(_download_one, model, verbose)
                to_do_map[future] = model
            done_iter = as_completed(to_do_map)
            if verbose is True:
                done_iter = tqdm.tqdm(done_iter, total=len(models))
            for future in done_iter:
                try:
                    status = future.result()
                except KeyboardInterrupt:
                    break
                else:
                    error_msg = ''
                if error_msg:
                    status = DownloadStatus.ERROR
                counter[status] += 1
                if verbose and error_msg:
                    cc = to_do_map[future]  # <14>
                    print(f'{name_} {cc} error: {error_msg}')
        return counter

    @clock
    def _get_models_info(self, models):
        name_ = f"{self.name_}: {inspect.currentframe().f_code.co_name}"
        MODEL_DATA_NAMEDTUPLE = namedtuple("Model_Data_Namedtuple", "model size size_type")
        models_all_downloaded = set(models)
        models_codes = set([m for m in models if "code" in m])
        models_sql = set([m for m in models if "sql" in m])
        models_math = set([m for m in models if "math" in m])
        models_all = models_all_downloaded - models_codes - models_sql - models_math
        printit("{name_} models_codes", models_codes)
        # Use ollama to retrieve models information
        command = "ollama list"
        result = subprocess.check_output([command], shell=True)
#       printit(f"{name_} {command}: ", result)
        models = result.strip().decode("utf-8")
        models = models.split("\n")
        pat = re.compile(f"^(\S+)\s+\S+\s+(\S+)\s(GB|MP).*$")
        models_data = []
        for line in models:
            matched = pat.match(line)
            if matched is not None:
                mdata = MODEL_DATA_NAMEDTUPLE(*matched.groups())
                mdata = mdata._asdict()
                models_data.append(mdata)
#       print("{name_} models_data", pformat(models_data))
        models_all_downloaded_info = models_data
        print(f"models_data {models_data}")
        models_codes_info = [m for m in models_data if m["model"].split(":")[0] in models_codes]
        models_sql_info = [m for m in models_data if m["model"].split(":")[0] in models_sql]
        models_math_info = [m for m in models_data if m["model"].split(":")[0] in models_math]
        models_big_info = [m for m in models_data if m["size_type"] == "GB" and float(m["size"]) > 10]
        models_big = set([m["model"].split(":")[0] for m in models_big_info])
        print("{name_}  models_big", pformat(models_big))
        models_all_info = [m for m in models_data if m["model"].split(":")[0] not in (
            models_codes | models_sql | models_big | models_math)]
        print("{name_} models_all_downloaded_info", pformat(models_all_downloaded_info))
        print("{name_} models_big_info", pformat(models_big_info))
        print("{name_} models_all_info", pformat(models_all_info))
        print("{name_} models_codes_info", pformat(models_codes_info))
        print("{name_} models_sql_info", pformat(models_sql_info))
        print("{name_} models_math_info", pformat(models_math_info))
        self.models_data = models_data
        self.models_all_downloaded_info = models_data
        self.models_codes_info = models_codes_info
        self.models_sql_info = models_sql_info
        self.models_math_info = models_math_info
        self.models_big_info = models_big_info
        self.models_all_info = models_all_info

    @clock
    def _save_all_models_file(self, models):
        name_ = f"{self.name_}: {inspect.currentframe().f_code.co_name}"
        for fname, data in zip(
            ["models_all_downloaded.txt", "models_big.txt", "models_all.txt", "models_codes.txt", "models_sql.txt", "models_math.txt",],
            [self.models_all_downloaded_info, self.models_big_info, self.models_all_info, self.models_codes_info, self.models_sql_info, self.models_math_info,]):
            self._save_file(fname, data)
        for fname in ["models_all_downloaded.txt", "models_big.txt", "models_all.txt", "models_codes.txt", "models_sql.txt", "models_math.txt",]:
            self._load_file(fname)

    @clock
    def _save_file(self, fname, fdata):
        name_ = f"{self.name_}: {inspect.currentframe().f_code.co_name}"
        print(f"{name_} fname {fname}")
        print(f"{name_} self.models_dir {self.models_dir}")
        fname = os.path.join(self.models_dir, fname)
        print(f"{name_} fname {fname}")
        with open(fname, "w") as fp:
            json.dump(fdata, fp, indent=4)

    @clock
    def _load_file(self, fname):
        name_ = f"{self.name_}: {inspect.currentframe().f_code.co_name}"
        print(f"{name_} fname {fname}")
        print(f"{name_} self.models_dir {self.models_dir}")
        fname = os.path.join(self.models_dir, fname)
        print(f"{name_} fname {fname}")
        with open(fname, "r") as fp:
            data = json.load(fp)
            printit(f"{fname} data", data)
            printit(f"{fname} data type", type(data))


def Options():
    parser = argparse.ArgumentParser()
    parser.add_argument('--default_concur_req', type=int, help='default_concur_req', default=10)
    parser.add_argument('--max_concur_req', type=int, help='max_concur_req', default=10)
    parser.add_argument('--url', type=str, help='url', default='https://ollama.com/library')
    parser.add_argument('--models_dir', type=str, help='models_dir', default='.ollama_downloads/models')
    parser.add_argument('--models', type=str, help='models: A comma seperated list of models to download')
    args = vars(parser.parse_args())
    return args


if __name__ == "__main__":
    options = Options()
    printit("options", options)
    ollama_models = OllamaModels(options)
    ollama_models.download_models()
