all: build

build:
	go build -o use_by_c.o -buildmode=c-shared use_by_c.go 
	gcc -o use_go use_go.c ./use_by_c.o
	
.PHONY:build


clean: 
	rm -f use_go use_by_c.h use_by_c.o
