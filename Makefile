install:
	pip3 install . --user
	rm -r lambda_calc.egg-info
	cp lambdapy /usr/local/bin/lambdapy

check:
	cd test && ./test && ./test --file test.l && ./test --file test-let.l

clean:
	rm -rf *pyc __pycache__/ build/
