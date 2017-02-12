from distutils.core import setup
from Cython.Build import cythonize
from setuptools.extension import Extension

rfctrl_ext = Extension(
    'pi433.rfctrl',
    language='c++',
    libraries=['wiringPi'],
    sources=['pi433/rfctrl.pyx', 'pi433/src/RCSwitch.cpp']
)

setup(ext_modules = cythonize(rfctrl_ext))