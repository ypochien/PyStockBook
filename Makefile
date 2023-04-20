
test:
	pytest tests -vv

test-cov:
	pytest --cov=PyStockBook --cov-report=html
