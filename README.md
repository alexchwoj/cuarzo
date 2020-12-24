
<p align="center">
  <img src="https://i.imgur.com/4yP2jQN.png" width="500">
</p>
Cuarzo is a low-level programming language, aimed at creating x86 software for Linux

# About
Cuarzo originally emerged as a real-time scripting engine, it was slow and screwy. Over time it was molded into what it is today, a compiled language in all its aspects!

# Why use it?
- High level syntax, easy to understand for any beginner
- A highly manipulable pre-processor, create macros, environment variables and much more
- Fast as a rocket! The performance of Cuarzo is very high, thanks to the use of assembly
- Using low-level language features is now much easier!

# Example code
```c
# Comment (type 1)

/* Multiple
lines
comment (type 3) */

// Simple comment (type 2)

#define VALOR_ONE 1337
#define VALOR_TWO

main()
{
	#if defined VALOR_TWO
    	print("Valor one: VALOR_ONE")
	#endif

	#undef VALOR_ONE
	#define VALOR_ONE 20

	print("Valor one: VALOR_ONE")

	#if defined THIS_DEFINE_DOES_NOT_EXIST
    	print("Never!")
	#endif

	var distance
	var variable
	print("Hello world")
	print("System info: __CUARZO_SYSTEM_NAME__, __CUARZO_SYSTEM_RELEASE__, __CUARZO_SYSTEM_VERSION__")
	print("Build date: __CUARZO_BUILD_DATE__")
	return 0
}
```

# Alert
The project is still in an early phase, not yet ready for productive use