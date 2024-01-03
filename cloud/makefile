BOLD := \033[1m
NORMAL := \033[0m
GREEN := \033[1;32m

.DEFAULT_GOAL := help
HELP_TARGET_DEPTH ?= \#
.PHONY: help
help: # Show how to get started & what targets are available
    @printf "This is a list of all the make targets that you can run, e.g. $(BOLD)make dagger$(NORMAL) - or $(BOLD)m dagger$(NORMAL)\n\n"
    @awk -F':+ |$(HELP_TARGET_DEPTH)' '/^[0-9a-zA-Z._%-]+:+.+$(HELP_TARGET_DEPTH).+$$/ { printf "$(GREEN)%-20s\033[0m %s\n", $$1, $$3 }' $(MAKEFILE_LIST) | sort
    @echo


install: clean # Format all files (terraform fmt --recursive .)
    python3.9 -m pip install -t python/lib/python3.9/site-packages selenium==4.5.0 --upgrade
    python3.9 -m pip install -t python/lib/python3.9/site-packages wget --upgrade
    curl -SL https://chromedriver.storage.googleapis.com/106.0.5249.61/chromedriver_linux64.zip > chromedriver.zip
    curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-57/stable-headless-chromium-amazonlinux-2.zip > headless-chromium.zip
    mkdir -p lambda
    zip -9 -r lambda/python.zip python
    unzip chromedriver.zip
    unzip headless-chromium.zip
    zip -9 -r lambda/chromedriver.zip chromedriver headless-chromium
    rm -f chromedriver.zip headless-chromium.zip chromedriver headless-chromium

build: # Create all layers to upload to the Lambda Function
    zip -9 -r lambda/app.zip app.py

clean:
    rm -rf lambda python