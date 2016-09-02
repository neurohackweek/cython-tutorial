---
title: "Using annotations to improve performance even more"
teaching: 15
exercises: 5
questions:
- "How do we diagnose performance bottlenecks?"
- "How can we improve these bottlenecks even more?"
objectives:
- "Use html annotations to diagnose performance bottlenecks"
- "Use additional compiler instructions to improve performance even more"
keypoints:
- "Cython provides an annotation system to diagnose the level of interaction with Python"
- "Improvements can often be made with this information"
- "Additional performance gains can be made with simple compiler instructions"
---

### How do we know this helps? using annotations

Recall that Cython compiles your code into C code for a python extension
module. Depending on the information you provided (type annotations,
`cdef`/`cpdef`) this will require more or less complicated C code. Cython
provides tools to explore and optimize this process. To create an annotation of
your file, on the command line run:

~~~
cython -a file_name.pyx
~~~

This generates your `.c` file, but also an `html` file with information about
the line-by-line cost of the `pyx` file. The shade of yellow corresponds the
number of lines of c that were generated, which highly correlates with the time
of execution.

Here's how this would be used in practice. Consider a simple case in which a
helper function is used to calculate an increment, and this function is used by
a more general function (`increment.pyx`):

~~~
def increment(int num, int offset):
    return num + offset

def increment_sequence(seq, offset):
    result = []
    for val in seq:
        res = increment(val, offset)
        result.append(res)
    return result
~~~
{: .python}

Cythonize this file, and open the `increment.html` file, which annotates the
cythonization process.

Now, let's consider how much better we would do using `cdef` (`increment.pyx`):

~~~
cdef int fast_increment(int num, int offset):
    return num + offset

def fast_increment_sequence(seq, offset):
    result = []
    for val in seq:
        res = fast_increment(val, offset)
        result.append(res)
    return result
~~~
{: .python}

Notice that in the second example, the lines corresponding to the first function
are now completely white. The second example will also be much faster, because
there is less Python-related overhead in that one. Cython can compile the
fast_increment function without needing to do things like Python type-checking,
etc.

In this case, we may as well use cpdef:

~~~
cpdef int increment_either(int num, int offset):
    return num + offset

def fast_increment_sequence(seq, offset):
    result = []
    for val in seq:
        res = increment_either(val, offset)
        result.append(res)
    return result
~~~
{: .python}


The function increment_either is only fast when called by
fast_increment_sequence. However, you can now independently call it from Python
(in which case, it will be slow).


> ## Compling c extensions from c code.
> This is useful if you want to use legacy C code. Consider the following toy
> example. Let's say you had the following C code (in fact.h):
>
>     int fact(int n)
>        {
>        if (n<=1)
>        return 1;
>        return n * fact(n-1);
>        }
>
> You could easily create a Python extension for this code by writing the Cython
> file that contains the following (fact.pyx):
>
>     cdef extern from "fact.h":
>         int _fact "fact"(int)
>
>     def fact(int n):
>         return _fact(n)
>     
>
> This is then compiled by typing:
>
>     cythonize fact.pyx  
>
> You can look at the fact.html file that gets generated with annotation to see
> all the code you now *didn't* have to write.
> Similar principles can be used with much more complex C code.
