---
title: "Compiling Cython code"
teaching: 5
exercises: 5
questions:
- "How do we compile Cython code in a typical project?"
objectives:
- "Use the `setup.py` file to compile Cython code"
- "Use the pyximport to compile on the fly"
- ""
keypoints:
- ""
- ""
---

### `pyx` is for Cython

Typical usage of Cython will include the writing of Python and Cython code side
by side in the same library. Consider our Fibonacci series code.

To mark it as a Cython (rather than Python) file, we place it in a `.pyx` file.

We create two files. The first is a Cython file that contains the code we've
already written for the Fibonacci series. We'll save it as `fib.pyx`:

~~~
def fib(int n):
    cdef int i, a, b
    a, b = 1, 1
    for i in range(n):
        a, b = a+b, a

    return a
~~~
{: .python}


In another file, we'll set up the compilation. The Python
[`distutils`](https://docs.python.org/3/library/distutils.html) library has
functionality to deal with extension code, and Cython knows how to take
advantage of that to orchestrate the compilation of `pyx` files:

~~~
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext = Extension("fib", sources=["fib.pyx"])

setup(ext_modules=[ext],
      cmdclass={'build_ext': build_ext})
~~~
{: .python}

To compile the fib.pyx file, we run the `setup` file:  

~~~
python setup_fib.py build_ext --inplace [--compiler=mingw32 #only for Windows!]
~~~
{: .python}

This creates a `fib.o` compiled object and a `fib.so` bundled Python extension,
such that in a Python/IPython session, you can now do:

~~~
import fib
a = fib.fib(10)
~~~
{: .python}


### C fails fast

The function that we created here is statically typed. That means that, in
contrast to a Python function it will only accept the types of objects for which
it has been compiled.

For example, if you run the function with an input `foo` for which `int(foo)`
would fail, it will not . For example, we can try running:

fib.fib("a string")

The dynamically typed Python could not identify that this is not the right type
for the operations in this function, but the C code, that is statically typed
recognizes this upfront, and fails immediately upon calling the function.

### Using `pyximport`

An even easier way to use cython is through the `pyximport` mechanism. For
example, we can create a Python file called `run_fib.py` that has the following
content:

~~~
import pyximport   # This is part of Cython
pyximport.install()
from fib import fib  # This finds the pyx file, compiles automatically!
print(fib(10))
~~~
{: .python}

Looking around in this folder, we see that this time, there is no `.c`, `.o` or
`.so` files around. This looks like magic, but we can resolve the mystery by
asking Python where it loaded this module from:

~~~
fib.__file__
~~~
{: .python}


## Optimizing further: using `cdef`

Typically, we will write an entire Cython module with functions, classes, and so
forth. Some of these objects need to have a public interface, so that they can
be used by our Python code, but some of these are local to the Cython module,
and don't need to be available to use in python code. We can gain additional
performance boosts by defining them in such a way that the compiler knows they
don't need to have a Python interface.  

We can use the `cdef` keyword to define local functions and even types. For
example, in a Cython file called `physics.pyx`, we define the following function
and class:

~~~
cdef float distance(float *x, float *y, int n):
  cdef:  # same as using two lines each starting with `cdef`
    int i
    float d = 0.0

  for i in range(n):
      d += (x[i]- y[i]) **2
  return d

cdef class Particle(object):
    cdef float psn[3], vel[3]
    cdef int id
~~~
{: .python}

These defined objects would be unavailable from the Python side, but will be
available to other functions within that `pyx` file/module. They have the
advantage that they have no Python overhead when called, so their performance is
very good.  

### Using `cpdef`

Alternatively, defining these objects with `cpdef` will create both the
Cython-available and the Python-available versions of a function or class. Not
as simple, because the inputs now need to be something that python knows how to
produce (array pointers are not one of those...). Instead, here we use [typed memory views](http://cython.readthedocs.io/en/latest/src/userguide/memoryviews.html).
This is a 'view' onto the memory occupied by a numpy array from within the C
side of things. This makes things go really fast, because instead of passing in
the array, you are passing in a view into the memory.

~~~
 cpdef float distance(double[:] x, double[:] y):  
     cdef int i
     cdef int n = x.shape[0]
     cdef float d = 0.0
     for i in range(n):
         d += (x[i] - y[i]) ** 2
     return d
~~~

Finally, make sure that you are not writing Cython code that you could easily
get from somewhere else. If it's a basic operation that many people might use,
it's probably already been implemented (and it's probably better implemented
than you would implement it, see
[`scipy.spatial.distances.cdist`](http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html)).
