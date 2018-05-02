# MindSet

MindSet is a language based on set theory. It has only one data type, the set, one atomic datum, the empty set `{}`, and one persistent variable, `U`, which at the start of the program is equal to the input.

## Overview

- Sets are defined via curly braces and commas, as in Python. Extraneous commas are ignored.
- Most lines are simply evaluated, and `U` is set to the result. A line is considered not to end until all `{}` and `()` have been closed.
- Operators are all either binary infix, or unary postfix.
- For convenience, the (nonnegative) integers can be written in their ordinary base 10 form instead of their set theoretic form; they will be translated for program execution.\*
- Labels are used in flow control and as temporary variables in certain operators. They can be any nonempty alphabetic string (no numbers or underscores) except for `U`, and are case sensitive.
- If a line is preceded by `@` and a label, the result is not assigned to `U`. Instead, if the result is *not* `{}`, execution moves to the line after the *first* occurrence of the same `@` label. If it *is* `{}`, then execution moves to the line after the the *last* occurence of the same `@` label.
- If an `@` label occurs exactly once (such that execution will simply continue on regardless of the result), then implementations are encouraged to print the result of the accompanying evaluation when it is encountered, as a debug functionality.

\* For those not familiar, `0` is defined as `{}`, and the positive integers are represented by the set containing all previous integers. So, `1`=`{0}`, `2`=`{0,1}`, `3`=`{0,1,2}`.

## Operators

Arbitrary sets are represented by `A` and `B`. Labels are represented by `a`.

Precedence is parentheses, then unary operators, then binary operators from left to right.

### Standard Binary Operators

| Syntax      |     Name            | Meaning |
| ----------: | ------------------- | ------- |
| `A+B`       | Union               | The set of everything that's an element of `A` or `B`. |
| `A*B`       | Intersection        | The set of everything that's an element of both `A` and `B`. |
| `A-B`       | Difference          | The set of everything that's an element of `A`, but not `B`. |
| `A<B`       | Subset              | `U` if every element of `A` is an element of `B`, `{}` otherwise. |
| `A[B`       | Membership          | `U` if `A` is an element of `B`, `{}` otherwise. |
| `A=B`       | Equality            | `U` if `A` and `B` are the same, `{}` otherwise. |

### Standard Unary Operators

Using any Reduce operator on the empty set returns the empty set.

| Syntax      |     Name            | Meaning |
| ----------: | ------------------- | ------- |
| `A+`        | Union Reduce        | The union of all elements in `A`. |
| `A*`        | Intersection Reduce | The intersection of all elements in `A`. |
| `A-`        | Difference Reduce   | The set of all elements of elements of `A` which are elements of exactly one element of A. |
| `A$`        | Ordinal             | The whole number set representing the number of elements in `A`. |
| `A^`        | Power Set           | The set of all possible subsets of `A`. |

### Complex Unary Operators

| Syntax      |     Name            | Meaning |
| ----------: | ------------------- | ------- |
| `A#a:(...)` | Map                 | The set of all elements `a` of `A`, transformed by the expression in the parentheses. For example, `{0,1,2}#a:(a-{0})` returns `{0,{1}}`, since `0-0`=`1-0`=`0` and `2-0`=`{1}`. |
| `A?a:(...)` | Filter              | The set of all elements `a` of `A` which don't return `{}` for the expression in the parentheses. For example, `{0,1,2}?a:(a-{0})` returns `{2}`. |

## Useful Concepts

- An ordered pair [`A`, `B`] can be defined with the form the Kuratowski formulation `{{A}, {A,B}}`. Then, `A` can be retrieved via unary `*`, and `B` can be retrieved via unary `-`. This works even if `A`=`B`.
- Ordered lists of larger size can be constructed in the form `{{0,{0,A}}, {1,{1,B}}, {2,{2,C}}...}`.
- To retrieve element `n` of list `A`, you can use `A?a:({n}[a)+-`


## Example programs

### Adding two numbers

The program assumes that the input is a set of 2 integral elements.

```
@Add {0}-U
  {U+ + {U+}, U*+ }
@Add {0}-U
(U-{0})+
```

- `@Add {0}-U` is simply a loop which ends when `U` contains `0`
- Since `U` is a set of numbers, `U+` is the maximum and `U*` is the minimum
- `A + {A}` is simply the successor function -- AKA, increment.
- Because of how numbers work, `A+` functions as a decrement.
- `(U-{0})+` gets rid of the `0`, and then "unpacks" the remaining member of `U` (`{A}+` always equals `A`)