! Author: Md. Shifat Hasan (2107067)

! Evaluate the following arithmetic expression:
! 13 * 17 / 7
! 13 * 17 = 221, 221 / 7 = 31, remainder = 4
! Result is #d31 or #h1F, remainder is #d4 or #h4

$a = 13
$b = 17
$c = 7

$result
$remainder

ina $a
mul $b
div $c

outa $result      ! Expected output: #h1F
outx $remainder   ! Expected output: #h4

show $result

hlt
