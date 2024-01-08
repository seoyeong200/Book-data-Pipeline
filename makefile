.PHONY: install

install:  # Format all files (terraform fmt --recursive .)
	python3 -m pip install -t python/lib/python3.6/site-packages selenium==3.8.0
	python3 -m pip install -t python/lib/python3.6/site-packages wget --upgrade
	curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > chromedriver.zip
	curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-41/stable-headless-chromium-amazonlinux-2017-03.zip > headless-chromium.zip
	mkdir -p lambda
	zip -9 -r lambda/python.zip python
	unzip chromedriver.zip
	unzip headless-chromium.zip
	zip -9 -r lambda/chromedriver.zip chromedriver headless-chromium
	rm -f chromedriver.zip headless-chromium.zip chromedriver headless-chromium


build: # Create all layers to upload to the Lambda Function
	zip -9 -r lambda/app.zip app.py

# clean:
# 	rm -rf lambda python
