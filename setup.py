from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy

examples_extension = Extension(
    name="fastwordle",
    sources=["fastwordle.pyx"],
    libraries=["fastwordle"],
    library_dirs=["lib"],
    include_dirs=["lib", numpy.get_include()]
)


setup(
    name="fastwordle",
    ext_modules=cythonize([examples_extension],
                          compiler_directives={'language_level' : "3"}
                          )
)
