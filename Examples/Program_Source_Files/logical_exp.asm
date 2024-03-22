! Author: Md. Shifat Hasan (2107067)

! Evaluate the following logical expression:
! #b1010 and #b1100 xor #b1010 or #b1100 = ?  (all the operators have equal precedence)
! Result is #b1110 = #hE

$a = #b1010
$b = #b1100
$c = #b1010
$d = #b1100

$result

ina $a
and $b
xor $c
or $d

outa $result      ! Expected output: #hE
show $result

hlt
