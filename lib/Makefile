CC = gcc

default: libfastwordle.a

libfastwordle.a: fastwordle.o
	ar rcs $@ $^

fastwordle.o: fastwordle.c fastwordle.h
	$(CC) -c $<

clean:
	rm *.o *.a
