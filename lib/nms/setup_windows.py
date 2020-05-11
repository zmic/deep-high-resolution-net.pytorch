# --------------------------------------------------------
# Pose.gluon
# Copyright (c) 2018-present Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Modified from py-faster-rcnn (https://github.com/rbgirshick/py-faster-rcnn)
# --------------------------------------------------------
#
# Adapted for building the extensions on Windows. 
#
# All this file needs to do is to build two .pyd files from 3 source files,
# so rather than shoe-horning nvcc into distutils.extension, just build the 
# two extensions "ad hoc" 
# 

import os
from os.path import join as pjoin
from setuptools import setup
#from distutils.extension import Extension
#from Cython.Distutils import build_ext
import numpy as np
import shutil
import sysconfig

# --------------------------------------------------------

if shutil.which('cython.exe') is None:
    raise RuntimeError('cython.exe must be in your path.')

if shutil.which('cl.exe') is None:
    raise RuntimeError('Can\'t find "cl.exe". This script must be run inside a Visual Studio environment.')
    
    
def locate_cuda():
    """Locate the CUDA environment on the system
    Returns a dict with keys 'home', 'nvcc', 'include', and 'lib64'
    and values giving the absolute path to each directory.
    Starts by looking for the CUDA_PATH env variable. If not found, everything
    is based on finding 'nvcc.exe' in the PATH.    
    """

    # CUDA_PATH  C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.2
    if 'CUDA_PATH1' in os.environ:
        home = os.environ['CUDA_PATH']
        nvcc = pjoin(home, 'bin', 'nvcc.exe')
    else:
        nvcc = shutil.which('nvcc.exe')
        if nvcc is None:
            raise EnvironmentError('The nvcc binary could not be '
                'located in your $PATH. Either add it to your path, or set $CUDA_PATH')
        home = os.path.dirname(os.path.dirname(nvcc))
    
    cudaconfig = {'home':home, 'nvcc':nvcc,
                  'include': pjoin(home, 'include'),
                  'lib64': pjoin(home, 'lib', 'x64')}
    for k, v in cudaconfig.items():
        if not os.path.exists(v):
            raise EnvironmentError('The CUDA %s path could not be located in %s' % (k, v))

    return cudaconfig
    
    
CUDA = locate_cuda()


# Obtain the numpy include directory.  This logic works across numpy versions.
try:
    numpy_include = np.get_include()
except AttributeError:
    numpy_include = np.get_numpy_include()

syspaths = sysconfig.get_paths()
python_include = syspaths['include']
python_lib = syspaths['stdlib']

# --------------------------------------------------------
#
# build cpu_nms.pyd
#

command = "cython cpu_nms.pyx"
os.system(command)

command = "cl /D_USRDLL /D_WINDLL /I{} /I{} cpu_nms.c /link /DLL /LIBPATH:{}s /OUT:cpu_nms.pyd".format(python_include,numpy_include, python_lib)
os.system(command)

# --------------------------------------------------------
#
# build gpu_nms.pyd
#
command = "cython gpu_nms.pyx"
os.system(command)

command = '"{}" -c -arch=sm_35 --ptxas-options=-v -I{} -I{} nms_kernel_externc.cu'.format(CUDA['nvcc'], python_include, numpy_include)
os.system(command)

command = 'cl /D_USRDLL /D_WINDLL /I{} /I{} gpu_nms.c nms_kernel_externc.obj "{}\cudart.lib" /link /DLL /LIBPATH:{}s /OUT:gpu_nms.pyd'.format(python_include, numpy_include, CUDA['lib64'], python_lib)
os.system(command)

