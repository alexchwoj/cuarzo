.data
label_0: .asciz "Enter a number: "
label_1: .asciz "%d"
label_4: .asciz "The number %d is higher than 10.\n"
label_5: .asciz "The number %d is lower than 10.\n"
.bss
.lcomm bss_tmp, 4
.lcomm number, 4
.text
.globl main
main:
finit
pushl $label_0
call printf
add $4, %esp
pushl $number
pushl $label_1
call scanf
add $8, %esp
pushl number
pushl $label_4
call printf
add $8, %esp
jmp label_3
label_2:
pushl number
pushl $label_5
call printf
add $8, %esp
label_3:
pushl $0
call exit
