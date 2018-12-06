TARGET = testMem
SOURCE = test.cpp mem.h
CFLAG  =  -L/usr/local/include/libmemcachde/ -lmemcached 
 
  
TARGET:
		g++ $(SOURCE) -o $(TARGET) $(CFLAG)
		 
.phony:clean
	 
clean:
		rm $(TARGET)
		 

