Speare2Brain
============

Speare2Brain is an ongoing project to develop a Shakespeare to Brainfuck transpiler. Based off the efforts of Jon Åslund and Karl Hasselström and their original SPL -> C transpiler, this project will first transpile Shakespeare to an intermediate format before transpiling to Brainfuck.

We'll be ripping out the internals of the original grammar generator to do this, making a mockery of the original project and sacrificing our souls in order to appease the demon lord Ba'al. The end result will be composed of:

* A heavily modified grammar.y, with some new helper functions in strutils.c. This will produce spl2nspl, an SPL-to-Not-Shakespeare-Programming-Language transpiler. Not-Shakespeare-Programming-Language is not Shakespeare Programming Language.
* A Python script called nspl2bf for transpiling the nspl to Brainfuck.
* A wrapper around these called speare2brain.