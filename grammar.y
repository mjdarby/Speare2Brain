/***********************************************************************

Speare2Brain, the Shakespeare -> Brainfuck transpiler

Copyright (C) 2014 Matthew Darby

Changes from the original work present in this file:
* C code is no longer output, the new target language is NSPL,
  also known as Not-Shakespeare Programming Language.
* Constant expressions are evaluated as often as possible
  rather than being left in the form 2*2*2*2*1 etc.

Based off the work and released under the same license as the below:

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

%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "strutils.h"
#include "telma.h"

#define COMMENT_COLUMN   40  //
#define INDENTATION_SIZE 2   // number of spaces to indent output C code

/* macro to create indentation space */
#define INDENT (strpad(newstr(""), INDENTATION_SIZE, ' '))

/* Local function prototypes */
static void report_error(const char *expected_symbol);
static void report_warning(const char *expected_symbol);

/* Global variables local to this file */
static char *current_act = NULL;
static char *current_scene = NULL;
static int num_errors = 0;           // error counter
static int num_warnings = 0;         // warning counter
static int i;                        // all-purpose counter

%}

%union {
  char *str;
  struct {
    int num;
    char **list;
  } stringlist;
}

%token <str> ARTICLE
%token <str> BE
%token <str> CHARACTER
%token <str> FIRST_PERSON
%token <str> FIRST_PERSON_POSSESSIVE
%token <str> FIRST_PERSON_REFLEXIVE
%token <str> NEGATIVE_ADJECTIVE
%token <str> NEGATIVE_COMPARATIVE
%token <str> NEGATIVE_NOUN
%token <str> NEUTRAL_ADJECTIVE
%token <str> NEUTRAL_NOUN
%token <str> NOTHING
%token <str> POSITIVE_ADJECTIVE
%token <str> POSITIVE_COMPARATIVE
%token <str> POSITIVE_NOUN
%token <str> SECOND_PERSON
%token <str> SECOND_PERSON_POSSESSIVE
%token <str> SECOND_PERSON_REFLEXIVE
%token <str> THIRD_PERSON_POSSESSIVE

%token <str> COLON
%token <str> COMMA
%token <str> EXCLAMATION_MARK
%token <str> LEFT_BRACKET
%token <str> PERIOD
%token <str> QUESTION_MARK
%token <str> RIGHT_BRACKET

%token <str> AND
%token <str> AS
%token <str> ENTER
%token <str> EXEUNT
%token <str> EXIT
%token <str> HEART
%token <str> IF_NOT
%token <str> IF_SO
%token <str> LESS
%token <str> LET_US
%token <str> LISTEN_TO
%token <str> MIND
%token <str> MORE
%token <str> NOT
%token <str> OPEN
%token <str> PROCEED_TO
%token <str> RECALL
%token <str> REMEMBER
%token <str> RETURN_TO
%token <str> SPEAK
%token <str> THAN
%token <str> THE_CUBE_OF
%token <str> THE_DIFFERENCE_BETWEEN
%token <str> THE_FACTORIAL_OF
%token <str> THE_PRODUCT_OF
%token <str> THE_QUOTIENT_BETWEEN
%token <str> THE_REMAINDER_OF_THE_QUOTIENT_BETWEEN
%token <str> THE_SQUARE_OF
%token <str> THE_SQUARE_ROOT_OF
%token <str> THE_SUM_OF
%token <str> TWICE
%token <str> WE_MUST
%token <str> WE_SHALL

%token <str> ACT_ROMAN
%token <str> SCENE_ROMAN
%token <str> ROMAN_NUMBER

%token <str> NONMATCH


%type <str>        Act
%type <str>        ActHeader
%type <str>        Adjective
%type <stringlist> BinaryOperator
%type <stringlist> CharacterDeclaration
%type <stringlist> CharacterDeclarationList
%type <stringlist> CharacterList
%type <str>        Comment
%type <str>        Comparative
%type <str>        Comparison
%type <str>        Conditional
%type <str>        Constant
%type <str>        EndSymbol
%type <str>        EnterExit
%type <str>        Equality
%type <str>        Inequality
%type <str>        InOut
%type <str>        Jump
%type <str>        JumpPhrase
%type <str>        JumpPhraseBeginning
%type <str>        JumpPhraseEnd
%type <str>        Line
%type <str>        NegativeComparative
%type <str>        NegativeConstant
%type <str>        NegativeNoun
%type <str>        NonnegatedComparison
%type <str>        OpenYour
%type <str>        Play
%type <str>        PositiveComparative
%type <str>        PositiveConstant
%type <str>        PositiveNoun
%type <str>        Pronoun
%type <str>        Question
%type <str>        QuestionSymbol
%type <str>        Recall
%type <str>        Remember
%type <str>        Scene
%type <str>        SceneContents
%type <str>        SceneHeader
%type <str>        Sentence
%type <str>        SentenceList
%type <str>        StartSymbol
%type <str>        Statement
%type <str>        StatementSymbol
%type <str>        String
%type <str>        StringSymbol
%type <str>        Title
%type <str>        UnarticulatedConstant
%type <stringlist> UnaryOperator
%type <str>        UnconditionalSentence
%type <str>        Value


%start StartSymbol

%%

Act:
ActHeader Scene {
  $$ = cat2($1, $2);
}|
Act Scene {
  $$ = cat2($1, $2);
};

ActHeader:
ACT_ROMAN COLON Comment EndSymbol {
  free(current_act);
  current_act = newstr(strip_act(str2varname($1)));
  $$ = cat3(newstr("label,act,"), newstr(current_act), newstr(",\n"));
  free($2);
  free($4);
}|
ACT_ROMAN COLON Comment error {
  report_warning("period or exclamation mark");
  free(current_act);
  current_act = newstr(strip_act(str2varname($1)));
  $$ = cat3(newstr("label,act,"), newstr(current_act), newstr(",\n"));
  free($2);
}|
ACT_ROMAN error Comment EndSymbol {
  report_warning("colon");
  free(current_act);
  current_act = newstr(strip_act(str2varname($1)));
  $$ = cat3(newstr("label,act,"), newstr(current_act), newstr(",\n"));
  free($4);
};

Adjective:
POSITIVE_ADJECTIVE {
  $$ = $1;
}|
NEUTRAL_ADJECTIVE {
  $$ = $1;
}|
NEGATIVE_ADJECTIVE {
  $$ = $1;
};

BinaryOperator:
THE_DIFFERENCE_BETWEEN {
  $$.list = (char **) malloc(3*sizeof(char **));
  $$.list[0] = newstr("sub,");
  $$.list[1] = newstr(",");
  free($1);
}|
THE_PRODUCT_OF {
  $$.list = (char **) malloc(3*sizeof(char **));
  $$.list[0] = newstr("mul,");
  $$.list[1] = newstr(",");
  free($1);
}|
THE_QUOTIENT_BETWEEN {
  $$.list = (char **) malloc(3*sizeof(char **));
  $$.list[0] = newstr("div,");
  $$.list[1] = newstr(",");
  free($1);
}|
THE_REMAINDER_OF_THE_QUOTIENT_BETWEEN {
  $$.list = (char **) malloc(3*sizeof(char **));
  $$.list[0] = newstr("mod,");
  $$.list[1] = newstr(",");
  free($1);
}|
THE_SUM_OF {
  $$.list = (char **) malloc(3*sizeof(char **));
  $$.list[0] = newstr("add,");
  $$.list[1] = newstr(",");
  free($1);
};

CharacterDeclaration:
CHARACTER COMMA Comment EndSymbol {
  $$.list = (char **) malloc(sizeof(char **));
  $$.list[0] = cat2((str2varname(newstr($1))), newstr(",\n"));
  free($2);
  free($4);
}|
error COMMA Comment EndSymbol {
  report_error("character name");
  $$.list = (char **) malloc(sizeof(char **));
  $$.list[0] = newstr("");
}|
CHARACTER error Comment EndSymbol {
  report_error("comma");
  $$.list = (char **) malloc(sizeof(char **));
  $$.list[0] = newstr("");
};

CharacterDeclarationList:
CharacterDeclaration {
  $$.list = (char **) malloc(sizeof(char **));
  $$.list[0] = $1.list[0];
  free($1.list);
}|
CharacterDeclarationList CharacterDeclaration {
  $$.list = $1.list;
  $$.list[0] = cat2($1.list[0], $2.list[0]);
  free($2.list);
};

CharacterList:
CHARACTER AND CHARACTER {
  $$.list = (char **) malloc(2*sizeof(char **));
  $$.list[0] = $1;
  $$.list[1] = $3;
  $$.num = 2;
  free($2);
}|
CHARACTER COMMA CharacterList {
  $$.num = $3.num + 1;
  $$.list = realloc($3.list, $$.num*sizeof(char **));
  $$.list[$$.num - 1] = $1;
  free($2);
};

Comment:
String {
  $$ = cat3(newstr("/* "), $1, newstr(" */"));
}|
error {
  report_warning("comment");
  $$ = newstr("/* NO COMMENT FOUND */");
};

Comparative:
NegativeComparative {
  $$ = newstr("less_than,");
  free($1);
}|
PositiveComparative {
  $$ = newstr("greater_than,");
  free($1);
};

Comparison:
NOT NonnegatedComparison {
  $$ = cat2(newstr("not,"), $2);
  free($1);
}|
NonnegatedComparison {
  $$ = $1;
};

Conditional:
IF_SO {
  $$ = newstr("true");
  free($1);
}|
IF_NOT {
  $$ = newstr("false");
  free($1);
};

Constant:
ARTICLE UnarticulatedConstant {
  $$ = $2;
  free($1);
}|
FIRST_PERSON_POSSESSIVE UnarticulatedConstant {
  $$ = $2;
  free($1);
}|
SECOND_PERSON_POSSESSIVE UnarticulatedConstant {
  $$ = $2;
  free($1);
}|
THIRD_PERSON_POSSESSIVE UnarticulatedConstant {
  $$ = $2;
  free($1);
}|
NOTHING {
  $$ = newstr("0");
  free($1);
};

EndSymbol:
QuestionSymbol {
  $$ = $1;
}|
StatementSymbol {
  $$ = $1;
};

EnterExit:
LEFT_BRACKET ENTER CHARACTER RIGHT_BRACKET {
  $$ = cat3(newstr("enter_scene,"), str2varname($3), newstr(",\n"));
  free($1);
  free($2);
  free($4);
}|
LEFT_BRACKET ENTER CharacterList RIGHT_BRACKET {
  $$ = cat3(newstr("enter_scene_multiple,"), newstr(int2str($3.num)), newstr(",\n"));
  for (i = 0; i < $3.num; i++) {
    $$ = cat3($$, str2varname($3.list[i]), newstr(",\n"));
  }
  free($3.list);
  free($1);
  free($2);
  free($4);
}|
LEFT_BRACKET EXIT CHARACTER RIGHT_BRACKET {
  $$ = cat3(newstr("exit_scene,"), str2varname($3), newstr(",\n"));
  free($1);
  free($2);
  free($4);
}|
LEFT_BRACKET EXEUNT CharacterList RIGHT_BRACKET {
  $$ = cat3(newstr("exit_scene,"), int2str($3.num), newstr(",\n"));
  for (i = 0; i < $3.num; i++) {
    $$ = cat3($$, str2varname($3.list[i]), newstr(",\n"));
  }
  free($3.list);
  free($1);
  free($2);
  free($4);
}|
LEFT_BRACKET EXEUNT RIGHT_BRACKET {
  $$ = newstr("exit_scene_all,\n");
  free($1);
  free($2);
  free($3);
}|
LEFT_BRACKET ENTER error RIGHT_BRACKET {
  report_error("character or character list");
  $$ = newstr("");
  free($1);
  free($2);
  free($4);
}|
LEFT_BRACKET EXIT error RIGHT_BRACKET {
  report_error("character");
  $$ = newstr("");
  free($1);
  free($2);
  free($4);
}|
LEFT_BRACKET EXEUNT error RIGHT_BRACKET {
  report_error("character list or nothing");
  $$ = newstr("");
  free($1);
  free($2);
  free($4);
}|
LEFT_BRACKET error RIGHT_BRACKET {
  report_error("'enter', 'exit' or 'exeunt'");
  $$ = newstr("");
  free($1);
  free($3);
};

Equality:
AS Adjective AS {
  $$ = newstr("equal_to");
  free($1);
  free($2);
  free($3);
}|
AS error AS {
  report_error("adjective");
  $$ = newstr("");
  free($1);
  free($3);
}|
AS Adjective error {
  report_error("as");
  $$ = newstr("");
  free($1);
  free($2);
};

Inequality:
Comparative THAN {
  $$ = $1;
  free($2);
}|
Comparative error {
  report_warning("'than'");
  $$ = $1;
};

InOut:
OpenYour HEART StatementSymbol {
  $$ = newstr("int_output,\n");
  free($1);
  free($2);
  free($3);
}|
SPEAK SECOND_PERSON_POSSESSIVE MIND StatementSymbol {
  $$ = newstr("output,\n");
  free($1);
  free($2);
  free($3);
  free($4);
}|
LISTEN_TO SECOND_PERSON_POSSESSIVE HEART StatementSymbol {
  $$ = newstr("int_input,\n");
  free($1);
  free($2);
  free($3);
  free($4);
}|
OpenYour MIND StatementSymbol {
  $$ = newstr("char_input,\n");
  free($1);
  free($2);
  free($3);
}|
OpenYour error StatementSymbol {
  report_error("'mind' or 'heart'");
  $$ = newstr("");
  free($1);
  free($3);
}|
SPEAK error MIND StatementSymbol {
  report_warning("possessive pronoun, second person");
  $$ = newstr("output,\n");
  free($1);
  free($3);
  free($4);
}|
LISTEN_TO error HEART StatementSymbol {
  report_warning("possessive pronoun, second person");
  $$ = newstr("int_input,\n");
  free($1);
  free($3);
  free($4);
}|
SPEAK SECOND_PERSON_POSSESSIVE error StatementSymbol {
  report_warning("'mind'");
  $$ = newstr("output,\n");
  free($1);
  free($2);
  free($4);
}|
LISTEN_TO SECOND_PERSON_POSSESSIVE error StatementSymbol {
  report_warning("'heart'");
  $$ = newstr("int_input,\n");
  free($1);
  free($2);
  free($4);
}|
OpenYour HEART error {
  report_warning("period or exclamation mark");
  $$ = newstr("int_output,\n");
  free($1);
  free($2);
}|
SPEAK SECOND_PERSON_POSSESSIVE MIND error {
  report_warning("period or exclamation mark");
  $$ = newstr("output,\n");
  free($1);
  free($2);
  free($3);
}|
LISTEN_TO SECOND_PERSON_POSSESSIVE HEART error {
  report_warning("period or exclamation mark");
  $$ = newstr("int_input,\n");
  free($1);
  free($2);
  free($3);
}|
OpenYour MIND error {
  report_warning("period or exclamation mark");
  $$ = newstr("char_input,\n");
  free($1);
  free($2);
};

Jump:
JumpPhrase ACT_ROMAN StatementSymbol {
  $$ = cat3(newstr("goto,act,"), strip_act(str2varname($2)), newstr(",\n"));
  free($1);
  free($3);
}|
JumpPhrase SCENE_ROMAN StatementSymbol {
  $$ = cat5(newstr("goto,act,"), newstr(current_act), newstr("scene,"),
	    strip_scene(str2varname($2)), newstr(",\n"));
  free($1);
  free($3);
}|
JumpPhrase error StatementSymbol {
  report_error("'act [roman number]' or 'scene [roman number]'");
  $$ = newstr("");
  free($1);
  free($3);
};

JumpPhrase:
JumpPhraseBeginning JumpPhraseEnd {
  $$ = cat3($1, newstr(" "), $2);
}|
error JumpPhraseEnd {
  report_warning("'let us', 'we must' or 'we shall'");
  $$ = newstr("");
  free($2);
}|
JumpPhraseBeginning error {
  report_warning("'proceed to' or 'return to'");
  $$ = newstr("");
  free($1);
};

JumpPhraseBeginning:
LET_US {
  $$ = $1;
}|
WE_MUST {
  $$ = $1;
}|
WE_SHALL {
  $$ = $1;
};

JumpPhraseEnd:
PROCEED_TO {
  $$ = $1;
}|
RETURN_TO {
  $$ = $1;
};

Line:
CHARACTER COLON SentenceList {
  $$ = cat4(newstr("activate,"), str2varname($1), newstr(",\n"), $3);
  free($2);
}|
CHARACTER COLON error {
  report_error("sentence list");
  $$ = newstr("");
  free($1);
  free($2);
}|
CHARACTER error SentenceList {
  report_error("colon");
  $$ = newstr("");
  free($1);
  free($3);
};

NegativeComparative:
NEGATIVE_COMPARATIVE {
  $$ = $1;
}|
MORE NEGATIVE_ADJECTIVE {
  $$ = cat3($1, newstr(" "), $2);
}|
LESS POSITIVE_ADJECTIVE {
  $$ = cat3($1, newstr(" "), $2);
};

NegativeConstant:
NegativeNoun {
  $$ = newstr("(-1)");
  free($1);
}|
NEGATIVE_ADJECTIVE NegativeConstant {
  $$ = cat2(newstr("2*"), $2);
  free($1);
}|
NEUTRAL_ADJECTIVE NegativeConstant {
  $$ = cat2(newstr("2*"), $2);
  free($1);
};

NegativeNoun:
NEGATIVE_NOUN {
  $$ = $1;
};

NonnegatedComparison:
Equality {
  $$ = $1;
}|
Inequality {
  $$ = $1;
};

OpenYour:
OPEN SECOND_PERSON_POSSESSIVE {
  $$ = newstr("");
  free($1);
  free($2);
}|
OPEN error {
  report_warning("possessive pronoun, second person");
  $$ = newstr("");
  free($1);
};

Play:
Title CharacterDeclarationList Act {
  $$ = cat4(newstr("chars,\n"),
	    $2.list[0],
	    newstr("endchars,\n"),
	    $3);
  free($2.list);
}|
Play Act {
  $$ = cat2($1, $2);
}|
Title CharacterDeclarationList error {
  report_error("act");
  $$ = newstr("");
  free($2.list[0]);
  free($2.list);
}|
Title error Act {
  report_error("character declaration list");
  $$ = newstr("");
  free($1);
  free($3);
}|
error CharacterDeclarationList Act {
  report_warning("title");
  $$ = cat4(newstr("chars,\n"),
	    $2.list[0],
	    newstr("endchars,\n"),
	    $3);
  free($2.list);
};

PositiveComparative:
POSITIVE_COMPARATIVE {
  $$ = $1;
}|
MORE POSITIVE_ADJECTIVE {
  $$ = cat3($1, newstr(" "), $2);
}|
LESS NEGATIVE_ADJECTIVE {
  $$ = cat3($1, newstr(" "), $2);
};

PositiveConstant:
PositiveNoun {
  $$ = newstr("1");
  free($1);
}|
POSITIVE_ADJECTIVE PositiveConstant {
  $$ = cat2(newstr("2*"), $2);
  free($1);
}|
NEUTRAL_ADJECTIVE PositiveConstant {
  $$ = cat2(newstr("2*"), $2);
  free($1);
};

PositiveNoun:
NEUTRAL_NOUN {
  $$ = $1;
}|
POSITIVE_NOUN {
  $$ = $1;
};

Pronoun:
FIRST_PERSON {
  $$ = newstr("first_person");
}|
FIRST_PERSON_REFLEXIVE {
  $$ = newstr("first_person");
}|
SECOND_PERSON {
  $$ = newstr("second_person");
}|
SECOND_PERSON_REFLEXIVE {
  $$ = newstr("second_person");
};

Question:
BE Value Comparison Value QuestionSymbol {
  $$ = cat8(newstr("set_left_comp,"), $2, newstr(",\n"),
	    newstr("set_right_comp,"), $4, newstr(",\n"),
	    $3, newstr(",\n"));
  free($1);
  free($5);
}|
BE error Comparison Value QuestionSymbol {
  report_error("value");
  $$ = newstr("");
  free($1);
  free($3);
  free($4);
  free($5);
}|
BE Value error Value QuestionSymbol {
  report_error("comparison");
  $$ = newstr("");
  free($1);
  free($2);
  free($4);
  free($5);
}|
BE Value Comparison error QuestionSymbol {
  report_error("value");
  $$ = newstr("");
  free($1);
  free($2);
  free($3);
  free($5);
};

QuestionSymbol:
QUESTION_MARK {
  $$ = $1;
};

Recall:
RECALL String StatementSymbol {
  $$ = newstr("pop,\n");
  free($1);
  free($2);
  free($3);
}|
RECALL error StatementSymbol {
  report_warning("string");
  $$ = newstr("pop,\n");
  free($1);
  free($3);
}|
RECALL String error {
  report_warning("period or exclamation mark");
  $$ = newstr("pop,\n");
  free($1);
  free($2);
};

Remember:
REMEMBER Value StatementSymbol {
  $$ = cat3(newstr("push,"), $2, newstr(",\n"));
  free($1);
  free($3);
}|
REMEMBER error StatementSymbol {
  report_error("value");
  $$ = newstr("");
  free($1);
  free($3);
}|
REMEMBER Value error {
  report_warning("period or exclamation mark");
  $$ = cat3(newstr("push,"), $2, newstr(",\n"));
  free($1);
};

Scene:
SceneHeader SceneContents {
  $$ = cat2($1, $2);
};

SceneContents:
EnterExit {
  $$ = $1;
}|
Line {
  $$ = $1;
}|
SceneContents EnterExit {
  $$ = cat2($1, $2);
}|
SceneContents Line {
  $$ = cat2($1, $2);
};

SceneHeader:
SCENE_ROMAN COLON Comment EndSymbol {
  free(current_scene);
  current_scene = cat4(newstr("label,act,"),newstr(current_act), newstr(",scene,"), strip_scene(str2varname($1)));
  $$ = cat2(newstr(current_scene), newstr(",\n"));
  free($2);
  free($4);
}|
SCENE_ROMAN COLON Comment error {
  report_warning("period or exclamation mark");
  free(current_scene);
  current_scene = cat4(newstr("label,act,"),newstr(current_act), newstr(",scene,"), strip_scene(str2varname($1)));
  $$ = cat2(newstr(current_scene), newstr(",\n"));
  free($2);
}|
SCENE_ROMAN error Comment EndSymbol {
  report_warning("colon");
  free(current_scene);
  current_scene = cat4(newstr("label,act,"),newstr(current_act), newstr(",scene,"), strip_scene(str2varname($1)));
  $$ = cat2(newstr(current_scene), newstr(",\n"));
  free($4);
};

Sentence:
UnconditionalSentence {
  $$ = $1;
}|
Conditional COMMA UnconditionalSentence {
  $$ = cat5(newstr("if,"), $1, newstr(",\n"), $3, newstr("endif,\n"));
}|
Conditional error UnconditionalSentence {
  report_warning("comma");
  $$ = cat5(newstr("if,"), $1, newstr(",\n"), $3, newstr("endif,\n"));
};

SentenceList:
Sentence {
  $$ = $1;
}|
SentenceList Sentence {
  $$ = cat2($1, $2);
};

StartSymbol:
Play {
  char *program;
  program = newstr($1);
  printf(program);
  free(program);
};

Statement:
SECOND_PERSON BE Constant StatementSymbol {
  $$ = cat3(newstr("assign,"), $3, newstr(",\n"));
  free($1);
  free($2);
  free($4);
}|
SECOND_PERSON UnarticulatedConstant StatementSymbol {
  $$ = cat3(newstr("assign,"), $2, newstr(",\n"));
  free($1);
  free($3);
}|
SECOND_PERSON BE Equality Value StatementSymbol {
  $$ = cat3(newstr("assign,"), $4, newstr(",\n"));
  free($1);
  free($2);
  free($3);
  free($5);
}|
SECOND_PERSON BE Constant error {
  report_warning("period or exclamation mark");
  $$ = cat3(newstr("assign,"), $3, newstr(",\n"));
  free($1);
  free($2);
}|
SECOND_PERSON BE error StatementSymbol {
  report_error("constant");
  $$ = newstr("");
  free($1);
  free($2);
  free($4);
}|
SECOND_PERSON error Constant StatementSymbol {
  report_warning("be");
  $$ = cat3(newstr("assign,"), $3, newstr(",\n"));
  free($1);
  free($4);
}|
SECOND_PERSON UnarticulatedConstant error {
  report_warning("period or exclamation mark");
  $$ = cat3(newstr("assign,"), $2, newstr(",\n"));
  free($1);
}|
SECOND_PERSON error StatementSymbol {
  report_error("constant without article");
  $$ = newstr("");
  free($1);
  free($3);
}|
SECOND_PERSON BE Equality Value error {
  report_warning("period or exclamation mark");
  $$ = cat3(newstr("assign,"), $4, newstr(",\n"));
  free($1);
  free($2);
  free($3);
}|
SECOND_PERSON BE Equality error StatementSymbol {
  report_error("value");
  $$ = newstr("");
  free($1);
  free($2);
  free($3);
  free($5);
}|
SECOND_PERSON BE error Value StatementSymbol {
  report_warning("equality");
  $$ = cat3(newstr("assign,"), $4, newstr(",\n"));
  free($1);
  free($2);
  free($5);
}|
SECOND_PERSON error Equality Value StatementSymbol {
  report_warning("be");
  $$ = cat3(newstr("assign,"), $4, newstr(",\n"));
  free($1);
  free($3);
  free($5);
};

StatementSymbol:
EXCLAMATION_MARK {
  $$ = $1;
}|
PERIOD {
  $$ = $1;
};

String:
StringSymbol {
  $$ = $1;
}|
String StringSymbol {
  $$ = cat3($1, newstr(" "), $2);
};

StringSymbol: ARTICLE                                { $$ = $1; }
            | BE                                     { $$ = $1; }
            | CHARACTER                              { $$ = $1; }
            | FIRST_PERSON                           { $$ = $1; }
            | FIRST_PERSON_POSSESSIVE                { $$ = $1; }
            | FIRST_PERSON_REFLEXIVE                 { $$ = $1; }
            | NEGATIVE_ADJECTIVE                     { $$ = $1; }
            | NEGATIVE_COMPARATIVE                   { $$ = $1; }
            | NEGATIVE_NOUN                          { $$ = $1; }
            | NEUTRAL_ADJECTIVE                      { $$ = $1; }
            | NEUTRAL_NOUN                           { $$ = $1; }
            | NOTHING                                { $$ = $1; }
            | POSITIVE_ADJECTIVE                     { $$ = $1; }
            | POSITIVE_COMPARATIVE                   { $$ = $1; }
            | POSITIVE_NOUN                          { $$ = $1; }
            | SECOND_PERSON                          { $$ = $1; }
            | SECOND_PERSON_POSSESSIVE               { $$ = $1; }
            | SECOND_PERSON_REFLEXIVE                { $$ = $1; }
            | THIRD_PERSON_POSSESSIVE                { $$ = $1; }

            | COMMA                                  { $$ = $1; }

            | AND                                    { $$ = $1; }
            | AS                                     { $$ = $1; }
            | ENTER                                  { $$ = $1; }
            | EXEUNT                                 { $$ = $1; }
            | EXIT                                   { $$ = $1; }
            | HEART                                  { $$ = $1; }
            | IF_NOT                                 { $$ = $1; }
            | IF_SO                                  { $$ = $1; }
            | LESS                                   { $$ = $1; }
            | LET_US                                 { $$ = $1; }
            | LISTEN_TO                              { $$ = $1; }
            | MIND                                   { $$ = $1; }
            | MORE                                   { $$ = $1; }
            | NOT                                    { $$ = $1; }
            | OPEN                                   { $$ = $1; }
            | PROCEED_TO                             { $$ = $1; }
            | RECALL                                 { $$ = $1; }
            | REMEMBER                               { $$ = $1; }
            | RETURN_TO                              { $$ = $1; }
            | SPEAK                                  { $$ = $1; }
            | THAN                                   { $$ = $1; }
            | THE_CUBE_OF                            { $$ = $1; }
            | THE_DIFFERENCE_BETWEEN                 { $$ = $1; }
            | THE_FACTORIAL_OF                       { $$ = $1; }
            | THE_PRODUCT_OF                         { $$ = $1; }
            | THE_QUOTIENT_BETWEEN                   { $$ = $1; }
            | THE_REMAINDER_OF_THE_QUOTIENT_BETWEEN  { $$ = $1; }
            | THE_SQUARE_OF                          { $$ = $1; }
            | THE_SQUARE_ROOT_OF                     { $$ = $1; }
            | THE_SUM_OF                             { $$ = $1; }
            | TWICE                                  { $$ = $1; }
            | WE_MUST                                { $$ = $1; }
            | WE_SHALL                               { $$ = $1; }

            | ACT_ROMAN                              { $$ = $1; }
            | SCENE_ROMAN                            { $$ = $1; }
            | ROMAN_NUMBER                           { $$ = $1; }

            | NONMATCH                               { $$ = $1; }
            ;

Title:
String EndSymbol {
  $$ = newstr("");
  free($2);
};

UnarticulatedConstant:
PositiveConstant {
  char buffer[128];
  if (strlen($1) == 1) {
    sprintf(buffer, "%d", 1);
  } else if (strlen($1) % 2 == 0) {
    int power = (strlen($1) - 2) / 2;
    sprintf(buffer, "%d", (int)-(pow(2,power)));
  } else {
    int power = (strlen($1) - 1) / 2;
    sprintf(buffer, "%d", (int)(pow(2,power)));
  }
  $$ = newstr(buffer);
}|
NegativeConstant {
  char buffer[128];
  if (strlen($1) == 4) {
    sprintf(buffer, "%d", -1);
  } else if (strlen($1) % 2 == 0) {
    int power = (strlen($1) - 4) / 2;
    sprintf(buffer, "%d", (int)-(pow(2,power)));
  } else {
    int power = (strlen($1) - 3) / 2;
    sprintf(buffer, "%d", (int)(pow(2,power)));
  }
  $$ = newstr(buffer);
};

UnaryOperator:
THE_CUBE_OF {
  $$.list = (char **) malloc(2*sizeof(char **));
  $$.list[0] = newstr("cube,");
  free($1);
}|
THE_FACTORIAL_OF {
  $$.list = (char **) malloc(2*sizeof(char **));
  $$.list[0] = newstr("factorial,");
  free($1);
}|
THE_SQUARE_OF {
  $$.list = (char **) malloc(2*sizeof(char **));
  $$.list[0] = newstr("square,");
  free($1);
}|
THE_SQUARE_ROOT_OF {
  $$.list = (char **) malloc(2*sizeof(char **));
  $$.list[0] = newstr("sqrt,");
  free($1);
}|
TWICE {
  $$.list = (char **) malloc(2*sizeof(char **));
  $$.list[0] = newstr("twice,");
  free($1);
};

UnconditionalSentence:
InOut {
  $$ = $1;
}|
Jump {
  $$ = $1;
}|
Question {
  $$ = $1;
}|
Recall {
  $$ = $1;
}|
Remember {
  $$ = $1;
}|
Statement {
  $$ = $1;
};

Value:
CHARACTER {
  $$ = cat2(newstr("value_of,"), str2varname($1));
}|
Constant {
  $$ = $1;
}|
Pronoun {
  $$ = cat2(newstr("value_of,"), $1);
}|
BinaryOperator Value AND Value {
  $$ = cat4($1.list[0], $2, $1.list[1], $4);
  free($1.list);
  free($3);
}|
UnaryOperator Value {
  $$ = cat2($1.list[0], $2);
}|
BinaryOperator Value AND error {
  report_error("value");
  $$ = newstr("");
  free($1.list[0]);
  free($1.list[1]);
  free($1.list);
  free($2);
  free($3);
}|
BinaryOperator Value error Value {
  report_warning("'and'");
  $$ = cat4($1.list[0], $2, $1.list[1], $4);
  free($1.list);
}|
BinaryOperator error AND Value {
  report_error("value");
  $$ = newstr("");
  free($1.list[0]);
  free($1.list[1]);
  free($1.list);
  free($3);
  free($4);
}|
UnaryOperator error {
  report_error("value");
  $$ = newstr("");
  free($1.list[0]);
  free($1.list);
};

%%

int yyerror(char *s)
{
  /* Don't do anything special here. */
  return 0;
}

void report_error(const char *expected_symbol)
{
  fprintf(stderr, "Error at line %d: %s expected\n", yylineno, expected_symbol);
  num_errors++;
}

void report_warning(const char *expected_symbol)
{
  fprintf(stderr, "Warning at line %d: %s expected\n", yylineno, expected_symbol);
  num_warnings++;
}

int main(void)
{
#if(YYDEBUG == 1)
  yydebug = 1;
#endif
  if (yyparse() == 0) {
    if (num_errors > 0) {
      fprintf(stderr, "%d errors and %d warnings found. No code output.\n", num_errors, num_warnings);
      exit(1);
    } else if (num_warnings > 0) {
      fprintf(stderr, "%d warnings found. Code may be defective.\n", num_warnings);
    }
  } else {
      fprintf(stderr, "Unrecognized error encountered. No code output.\n");
      exit(1);
  }
  return 0;
}
