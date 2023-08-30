clean:
	rm -rf ./cdk.out/

build:
	npm install -g aws-cdk && pip install -r requirements.txt