install:
	pip3 install . --user
	rm -r lambda_calc.egg-info
	cp lambdapy /usr/local/bin/lambdapy

check:
	./test --file test.l

clean:
	rm -rf *pyc __pycache__/
