! Author: Md. Shifat Hasan (2107067)

! Evaluate the following arithmetic expression:
! 13 + 7 - 5 + 19
! Result is 34 (in decimal) or #h22 (in hexadecimal)

$a = 13
$b = 7
$c = 5
$d = 19

$result

ina $a
add $b
sub $c
add $d

outa $result      ! Expected output: #h22
show $result

hlt