install:
	pip3 install . --user
	cp lambdacalc/lambdapy /usr/local/bin/lambdapy

check:
	cd test && ./test && ./test --file test.l && ./test --file test-let.l && ./test --file ../lambdacalc/stdlib/arithmetic.l && ./test --file ../lambdacalc/stdlib/logic.l

clean:
	rm -rf *pyc __pycache__/ lambdacalc/__pycache__ lambdacalc/*pyc build/ dist/ lambdacalc.egg-info/

upload:
	python3 -m twine upload --repository testpypi dist/*

