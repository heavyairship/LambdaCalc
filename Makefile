clean:
	rm -rf *pyc __pycache__/ lambdacalc/__pycache__ lambdacalc/*pyc build/ dist/ lambdacalc.egg-info/

install:
	pip3 install . --user
	cp lambdacalc/lambdapy /usr/local/bin/lambdapy

check: clean install
	cd test && ./test && ./test --file test.l && ./test --file test-let.l && ./test --file test-while.l

quick-check: clean install
	cd test && ./test

update:
	git add . && git commit -m "update" && git push
