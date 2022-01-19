LIB_DIR = lib

default: fastwordle

fastwordle: setup.py fastwordle.pyx $(LIB_DIR)/libfastwordle.a
	python3 setup.py build_ext --inplace && rm -f fast_wordle.c && rm -Rf build

$(LIB_DIR)/libfastwordle.a:
	make -C $(LIB_DIR) libfastwordle.a

clean:
	rm -rf *.so *~ __pycache__
	rm -f $(LIB_DIR)/*.o $(LIB_DIR)/*.a $(LIB_DIR)/*~
