---
title: "Wrap-Up"
teaching: 2
exercises: 0
questions:
- "What have we learned?"
objectives:
- "Recognize situations where using Cython/Numba is a good idea"
- "Recognize the pros and cons of using each of these"

keypoints:
- "Python can be slow in some conditions"
- "Cython an Numba can give substantial performance boosts in some of these"
- "There are use-cases in which one of these is better than the other"
- "Use them judiciously, to make your code faster"
---

## Why *not* to use Cython/Numba

One big disadvantage of using Cython/Numba is that it makes handling and
debugging errors harder. That is because the tracebacks that you get when
things go wrong will be much harder to decipher.

This means that code has to be thoroughly tested before it is converted to a
compiled version.
