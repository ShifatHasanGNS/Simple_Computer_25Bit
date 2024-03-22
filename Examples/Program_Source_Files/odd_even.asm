! Author: Md. Shifat Hasan (2107067)

! This program takes an integer as input and checks if it is even or odd.

$num = #d7

$one = #d1
$two = #d2

$temp  ! temp var

show $num  ! show 'num'
ina $num   ! load 'num'
div $two   ! divide by 2, remainder is stored in RX

! move the value of RX to RA via 'temp'
outx $temp
show $temp
ina $temp

cmp $one   ! compare(RA, 1) = RA - 1 --> set necessary flags
jmpz @is_odd   ! jump to 'is_even' label, if zero-flag is set

@back_from_is_odd:

jmpl @is_even   ! jump to 'is_even' label, if zero-flag is set

@back_from_is_even:

showf

hlt

@is_odd:
  set #d0
  jmp @back_from_is_odd

@is_even:
  clr #d0
  jmp @back_from_is_even
