---
title: "Introduction"
teaching: 15
exercises: 5
questions:
- "Why use Cython?"
- "How do you install Cython?"
- "What are some ways you can use Cython?"
objectives:
- "Install Cython on your own laptop using conda"
- "Write functions that can be cythonized in the notebook"
- "Profile functions with ipython magic functions, and measure speedup due to cythonization"
keypoints:
- "Cython can speed up some computations dramatically"
- "Profiling code is a useful way to know whether Cython is helping"
---

### Introducing Cython

Writing code in python is easy: because it is dynamically typed, we don't have
to worry to much about declaring variable types (e.g. integers vs. floating
point numbers). Also, it is interpreted, rather than compiled. Taken together,
this means that we can avoid a lot of the boiler-plate that makes compiled,
statically typed languages hard to read. However, this incurs a major drawback:
performance for some operations can be quite slow.

Whenever possible, the numpy array representation is helpful in saving
time. But not all operations can be vectorized. Other times, your only choice
is to extension code in C, but this is very cumbersome, and requires writing
many lines of additional code above and beyond your core algorithms, just to
communicate between the Python and C computation layers.

[Cython](http://cython.org/) is a technology that allows us to easily bridge
between python, and the underlying C representations. The main purpose of the
library is to take code that is written in python, and, provided some additional
amount of (mostly type) information, compile it to C, compile the C code, and
bundle the C objects into python extensions that can then be imported directly
into python.

### Installing Cython

You can install Cython from the command line using `conda`:

~~~
conda install cython
~~~
{: .bash}

### A first example - why use Cython?

To demonstrate the usefulness of Cython, we'll start with an atypical usage
pattern: In the `Jupyter `notebook, we will use the `cython` extension, to
demonstrate why and how to use cython.

Later, we will also look at how to use cython in the context of modules and
libraries. But for now, let's load the cython extension. This allows us to
mark cells as Cython cells by starting them with `%%cython` magic.

~~~
%load_ext cython
~~~
{: .python}


Let's see what this is good for. Consider a very simple function in Python:

~~~
def my_poly(a,b):
    return 10.5 * a + 3 * (b**2)
~~~
{: .python}


The equivalent Cython function is defined in a `%%cython` cell.

~~~
%%cython
def my_polyx(double a, double b):
    return 10.5 * a + 3 * (b**2)
~~~
{: .python}


> ## What are the differences?  
>
> Note that the only difference is that we tell the function to treat these
> variables as double-precision numbers. Why is that important?
> **Cython is a dialect of Python**: If this code were written in a regular
> Python cell it would produce a syntax error. Cython is a 'dialect' of python,
> but it is not exactly like Python.
> In fact, Cython is a proper superset of python. That means that any python
> code is syntactical Cython code, but not the opposite.
>
{: .callout}

To time the performance of Python/Cython code, we can use the IPython
`%timeit` magic:

~~~
%timeit my_poly(10, 2)
%timeit my_polyx(10, 2)
~~~
{: .python}

For even a trivial piece of code, we can already gain an approximately 3-fold
speedup

Let's consider an (only slightly) more interesting example, the calculation of
the Fibonacci series.

> ## The Fibonacci series
>
> The [Fibonacci series](https://en.wikipedia.org/wiki/Fibonacci_number) are
> arranged according to the rule:
>     F[n] = F[n-1] + F[n-2]
>
> This series has many interesting properties, but for our purposes it has one
> particulary interesting property and that is the fact that the item in the
> `n`th location cannot be calculated in a vectorized fashion (without first
> calculating items in `n-1`, `n-2` and so on until `n-1 = 0`). This means that
> we expect a naive computation to be rather slow.

~~~
def fib(n):
    a, b = 1, 1
    for i in range(n):
        a, b = a+b, a

    return a
~~~
{: .python}


For the Cython version of the function, we will use the `cdef` keyword (a
Cython language constant) to define local variables (integers used only within the function):

~~~
%%cython
def fibx(int n):
    cdef int i, a, b
    a, b = 1, 1
    for i in range(n):
        a, b = a+b, a
    return a
~~~
{: .python}

Compare the two using `%timeit`:

~~~
%timeit fib(10)
%timeit fibx(10)
~~~
{: .python}

In this case, we are already in the realm of a 10X speedup!

Let's pause to consider the implications of this. The C code required to
perform the same calculation as fibx might look something like this:

~~~
int fib(int n){
    int tmp, i, a, b;
    a = b = 1;
    for(i=0; i<n; i++){
         tmp = a;
         a += b;
         b = tmp;}         
    return a;}
~~~
{: .code}


In and of itself, that's not too terrible, but can get unpleasant if you write
more than this trivial function. The main issue is that integrating this code
into a python program is not trivial and requires writing extension code (think
mex, if you've used these in Matlab). This also has overhead that is hard to
optimize. Cython writes highly optimized python extension code, making it easy
to separate out performance bottle-necks and compile them, but keep using the
functions in your Python code.

> ## Speeding up recursion
>
> Recursive functions are functions that call themselves during their
> execution. Another interesting property of the Fibonacci series is that it
> can be written as a recursive function.
>
> Rewrite the fib function to use recursion. Is it faster than the
> non-recursive version? Does Cythonizing it give even more of an advantage?
>
{: .challenge}


> ## Speeding up recursion
> Here is a version of the Fibonacci series written using recursion:
>
>    def fib_r(n):
>         if n <= 1:
>              return n
>         else:
>              return fib_r(n-1) + fib_r(n-2)
>
> Is it better
> Well, it turns out that recursion looks clever, but works much worse.
> Even worse for this case, Cythonizing the recursed version of Fibonacci

{: .solution}


### Writing Cython that also works as Python

One of the major challenges in using Cython is that it requires compiling the
code for all the platforms (and architectures) on which you want to run the
code. This often means that you will distribute the Cython source code and ask
users to compile it themselves. If this fails, however, you might still want the
code to do what it's supposed to do, albeit slower.

The following is a perfectly syntactical Python example, that can also be
compiled using Cython. The declarations are now done as calls to functions in
the Cython library, instead of. If all else fails, this could would still work.

~~~
%%cython
import cython
@cython.locals(n=cython.int)
def fib_pure_python(n):
    cython.declare(a=cython.int,
                   b=cython.int,
                   i=cython.int)
    a, b = 1, 1
    for i in range(n):
        a, b = a+b, a
    return a
~~~
{: .python}

Try running this code with the `%%cython` magic removed, and witness the slow
down back to Python speed.
