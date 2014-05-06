# Makefile for the update-dotdee program.
#
# Author: Peter Odding <peter@peterodding.com>
# Last Change: July 6, 2013
# URL: https://github.com/xolox/python-update-dotdee

default:
	@echo 'Makefile for the update-dotdee program'
	@echo
	@echo 'Usage:'
	@echo
	@echo '    make publish    publish changes to GitHub/PyPI'
	@echo '    make clean      cleanup all temporary files'
	@echo

clean:
	rm -Rf build dist update_dotdee.egg-info

publish:
	git push origin && git push --tags origin
	make clean && python setup.py sdist upload
