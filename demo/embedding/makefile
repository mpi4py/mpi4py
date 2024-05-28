include ../config.mk
.PHONY: default build test clean
default: build test clean

PROGRAM = helloworld
SOURCE = $(PROGRAM).c
TARGET = $(PROGRAM).exe

CFLAGS  = $(shell $(PYTHON_CONFIG) --cflags)
LDFLAGS = $(shell $(PYTHON_CONFIG) --ldflags --embed)
$(TARGET): $(SOURCE)
	$(MPICC) $(CFLAGS) $(LDFLAGS) -o $@ $<

build: $(TARGET)

test: build
	$(MPIEXEC_RUNCMD) ./$(TARGET)

clean:
	$(RM) -r $(TARGET) $(TARGET).dSYM
