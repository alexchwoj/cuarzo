<p align="center">
  <img src="https://i.imgur.com/rdXQF8s.png" width="200">
</p>
Cuarzo is an instruction interpreter for python, which can be used for small remote applications.

# Features
- Print
- Get valors of variables (print)
- Variables (bool, float, int)
- Colors
- Sockets
- Modules

# Example code
### module_one.caz
```c
print "Module 1"
```
### module_two.caz
```c
print "Module 2"
```
### test.caz
```c
// Modules
#include <./module_one.caz>
#include <./module_two.caz>

// Example print and comment
print "Hello, this is Cuarzo~n~This is new line~n~Colors: ~r~RED ~g~GREEN ~y~YELLOW ~b~BLUE ~m~MAGENTA ~c~CYAN ~w~WHITE ~n~"

// Variables example
new float:flotante = 1.5
new bool:boolean = True
new int:entero = 5

// Print valors
print "El valor de flotante es: ~c~{flotante}~w~"
print "El valor de boolean es: ~c~{boolean}~w~"
print "El valor de entero es: ~c~{entero}~w~"
```


Donate (BTC)

`1CMEPuTPtEKRRbPokRp9vTqoJNVNmm1GXt`
