---
title: "Numba"
teaching: 10
exercises: 5
questions:
- "What other options do we have to speed up Python code?"
objectives:
- "Use Numba to just-in-time compile Python code"
keypoints:
- "Python can be slow in some conditions"
- "Cython an Numba can give substantial performance boosts in some of these"
- "Use them judiciously, to make your code faster"

---

### Numba does something quite different

[Numba](http://numba.pydata.org/) is a library that enables just-in-time (JIT)
compiling of Python code. It uses the [LLVM](http://llvm.org/) tool chain to do
this. Briefly, what LLVM does takes an intermediate representation of your code
and compile that down to highly optimized machine code, as the code is running.
That means that if you can get to this IR, you can get your code to run really
fast.

Numba is the bridge between the Python code and this intermediate
representation. Along the way, it does some clever type inference (for example,
if the code can take different types as input, integers vs. floats for example),
which allows it to be even faster. And there is a bunch of additional
cleverness. In particular, Numba is designed with scientific/numerical code in
mind, so it can sometimes leverage the fact that you are using Numpy. But we
won't get into that here.

### Installing

Numba can be installed using `conda`:

~~~
conda install numba
~~~
{: .python}


### Just-in-time compiling

Let's look again at the Fibonacci example we used before:

~~~
def fib(n):
    a, b = 1, 1
    for i in range(n):
        a, b = a+b, a

    return a
~~~
{: .python}


To get it to just-in-time compile on the first time it's run, we use Numba's
`jit` function:

~~~
from numba import jit
fibj = jit(fib)
~~~
{: .python}

Comparing timings we see a roughly ten-fold speedup!

Another way to use `jit` is as a decorator:

~~~
@jit
def fibj(n):
    a, b = 1, 1
    for i in range(n):
        a, b = a+b, a

    return a
~~~
{: .python}


> ## Python Decorators
>
> Decorators are a way to uniformly modify functions in a particular way. You
> can think of them as functions that take functions as input and produce a
> function as output (as explained on [this](http://matthew-brett.github.io/pydagogue/decorating_for_dummies.html) page by Matthew Brett).
>
> But the most concise explanation (as pointed out by MB) actually comes
> from the [Python reference documentation](https://docs.python.org/3/reference/compound_stmts.html#function-definitions):
>
> A function definition may be wrapped by one or more
> (*decorator*)[http://docs.python.org/glossary.html#term-decorator]
> expressions. Decorator expressions are evaluated when the function is
> defined, in the scope that contains the function definition. The result
> must be a callable, which is invoked with the function object as the
> only argument. The returned value is bound to the function name
> instead of the function object. Multiple decorators are applied in
> nested fashion. For example, the following code:
>
>    @f1(arg)
>    @f2
>    def func(): pass
>
> is equivalent to:
>
>    def func(): pass
>    func = f1(arg)(f2(func))
>
> As pointed out there, they are not limited neccesarily to function
> definitions, and [can also be used on class definitions](https://docs.python.org/3/reference/compound_stmts.html#class-definitions).
{: .callout}


## How does Numba work?

Do understand a little bit about how Numba works, let's see where it fails to
work. Let's rewrite the `fib` function using a custom Python object:

~~~
class MyInt(object):
  def __init__(self, n):
    self.int = n


def fib_obj(n):
    a, b = MyInt(1), MyInt(1)
    for i in range(n.int):
        a.int, b.int = a.int+b.int, a.int

    return a.int
~~~
{: .python}

This looks odd, but it works in the same way that the function above does
It's a bit slower, though (why do you think that is?).

Now, let's try to speed this up with Numba:

~~~

@jit
def fib_obj_j(n):
    a, b = MyInt(1), MyInt(1)
    for i in range(n.int):
        a.int, b.int = a.int+b.int, a.int

    return a.int
~~~
{: .python}

Timing this, we find it to be substantially *slower* than the non-jitted Python
version. The reason for this is that Numba is unable to do any type inference
here. Instead

### What is it really good for?

Let's look at an example where Numba really shines (h/t to [Jake Vanderplas](https://jakevdp.github.io/blog/2012/08/08/memoryview-benchmarks/)).
Consider a numpy function to calculate the parwise Euclidean distances between
two sets of coordinates:

~~~
def pdist_numpy(xs):
    return np.sqrt(((xs[:,None,:] - xs)**2).sum(-1))
~~~
{: .python}

We can use Numba to get this function to JIT (notice this is another way of `jit`-ing):

~~~
pdist_numba = jit(pdist_numpy)
~~~
{: .python}

Let's compare to Cython as well (this also demonstrates how to use numpy in
Cython code!):

~~~
%%cython
import numpy as cnp
def pdistx(xs):
    return cnp.sqrt(((xs[:,None,:] - xs)**2).sum(-1))
~~~
{: .python}

Timing all of these:

~~~
time_pdist_numpy = %timeit -o pdist_numpy(np.random.randn(5, 100))
time_pdist_numba = %timeit -o pdist_numba(np.random.randn(5, 100))
time_pdistx = %timeit -o pdistx(np.random.randn(5, 100))
print(time_pdist_numpy.best/time_pdist_numba.best)
print(time_pdist_numpy.best/time_pdistx.best)
~~~
{: .python}


We can see that we really can't beat numpy doing any of these.

But consider the following naive implementation of the same function in Python:

~~~
def pdist_python(xs):
    n, p = xs.shape
    D = np.empty((n, n), dtype=np.float)
    for i in range(n):
        for j in range(n):
            s = 0.0
            for k in range(p):
                tmp = xs[i,k] - xs[j,k]
                s += tmp * tmp
            D[i, j] = s**0.5
    return D
~~~
{: .python}

~~~
time_pdist_python = %timeit -o pdist_python(np.random.randn(5, 100))
print(time_pdist_python.best/time_pdist_numpy.best)
~~~
{: .python}

This is terrible! But this function can be substantially sped up with `jit`:

~~~
pdist_python_numba = jit(pdist_python)
~~~
{: .python}

~~~
time_pdist_python_numba = %timeit -o pdist_python_numba(np.random.randn(5, 100))
print(time_pdist_numpy.best/time_pdist_python_numba.best)
~~~
{: .python}

This is tremendously powerful, because there are many physical and statistical
functions that would be very hard to vectorize. Instead, in Numba, you are
*encouraged* to use nested loops, because Numba can leverage these, together
with type inference to do things blazingly fast.

### Using annotations

It is possible to use annotations in Numba as well.

To do that, we will need to create a Python module of our code (say `fib.py`)
and then add a `__main__` block, so that the code gets run (remember, it's
just-in-time compilation!) and can be annotated. For example:

~~~
from numba import jit


class MyInt(object):
    def __init__(self, n):
        self.int = n

@jit
def fib_obj(n):
    a, b = MyInt(1), MyInt(1)
    for i in range(n.int):
        a.int, b.int = a.int+b.int, a.int

    return a.int

@jit
def fib(n):
    a, b = 1, 1
    for i in range(n):
        a, b = a + b, a
    return a


if __name__ == "__main__":
    fib_obj(MyInt(10))
    fib(10)
~~~


> ### What does `if __name__ == "__main__":` do?
>
> This block can be added to a Python module to make it work both as a module
> and as a script. When a module is imported all of the function definitions
> in this module get executed, but the code in the functions does not get run.
> If, however, there is some code that is just sitting there .
>
> Defining a main block (fencing it inside an indented block under the
> `if __name__ == "__main__":` statement) allows us to define a specific part
> of the code that does not get run on importing, but does get run when the
> code is interpreted. For example, when `python fib.py` is called from the
> command line
>
{: .callout}

Annotations can then be done using:

~~~
numba --annotate-html fib.html fib.py
~~~
{: .python}


In this case, the code that interacts with Python objects that can't be
optimized is marked in red. If you click on the `show numba IR` text, you can
view the intermediate representation used by Numba to pass to LLVM. In general,
the more you see `pyobject` in there, the less Numba can do in terms of type
inferece to optimize your code. But whenever you see types inferred (e.g.
`int64`), the better Numba can do.


> # Numba Annotations
>
> Annotate the code we used for Euclidean distance calculations. Can you point
> out in the annotation why Numba-izing the naive implementation works better
> than operating on the Numpy-based implementation?
>
{: .challenge}
