GRAMMAR = ./src/scenic/syntax/scenic.gram
PARSER = ./src/scenic/syntax/parser.py

.PHONY: all
all: $(PARSER)

$(PARSER): $(GRAMMAR)
	python -m pegen $(GRAMMAR) -o $(PARSER)

format:
	isort .
	black .

serve:
	python ./src/servers/nats_server.py

.PHONY: clean
clean:
	-rm $(PARSER)
