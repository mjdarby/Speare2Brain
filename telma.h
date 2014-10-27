/***********************************************************************

Speare2Brain, the Shakespeare -> Brainfuck transpiler

Copyright (C) 2014 Matthew Darby

No changes from the original work are present in this file.

Based off the below work and released under the same license as the below:

SPL, the Shakespeare Programming Language

Copyright (C) 2001 Karl Hasselstr�m and Jon �slund

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
USA.

***********************************************************************/

/* These are things that are defined in scanner.c and needed in
   grammar.y.

   (telma.h? Read it backwards!)
*/

int yyerror(char *s);
int yylex(void);

extern int yylineno;
extern char *yytext;
