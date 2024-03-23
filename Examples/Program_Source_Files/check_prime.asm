! Pseudocode to check if a number is prime:
!
! bool is_prime(int p):
!     if (p <= 1) return false
!     if (p == 2) return true
!     if (p == 3) return true
!     if (p % 2 == 0) return false
!     if ((p-1) % 6 == 0 || (p+1) % 6 == 0):
!         for (int i = 3; i*i <= p; i++):
!             if (p % i == 0) return false
!         return true
!     else return false
!

! Now let's implement this in assembly language

$p = 997   ! the number to check if it is prime
$x = 1     ! looping variable
show $x

! constants
$zero = 0
$one = 1
$six = 6

$temp      ! temporary variable

! --------------------

! if (p <= 1) return false
ina $p
cmp $x
jmpz @is_not_prime
jmpl @is_not_prime

! --------------------

! update: x = 1, x = x + 1 --> x = 2
ina $x
add $one
outa $x
show $x

! if (p == 2) return true
ina $p
cmp $x
jmpz @is_prime

! --------------------

! x = 2
! if (p % 2 == 0) return false
and $one
cmp $zero
jmpz @is_not_prime

! --------------------

! update: x = 2, x = x + 1 --> x = 3
ina $x
add $one
outa $x
show $x

! if (p == 3) return true
ina $p
cmp $x
jmpz @is_prime

! --------------------

! if (p-1) % 6 == 0 --> goto @loop
ina $p
sub $one
div $six
outx $temp
ina $temp
cmp $zero
jmp @loop

! or, if (p+1) % 6 == 0 --> goto @loop
ina $p
add $one
div $six
outx $temp
ina $temp
cmp $zero
jmp @loop

jmp @is_not_prime

! --------------------
! x = 3

@loop:
  ! for (int i = 3; i*i <= p; i++):
  !     if (p % i == 0) return false

  ! if (i*i <= p)
  ina $x
  mul $x
  cmp $p
  jmpg @is_prime

  ! if (p % i == 0)
  ina $p
  div $x
  outx $temp
  ina $temp
  cmp $zero
  jmpz @is_not_prime

  ! x = x + 1
  ina $x
  add $one
  outa $x
  show $x

  jmp @loop

jmp @is_prime

hlt

@is_prime:
  set 0
  clr 1
  clr 2
  clr 3
  show $p
  showf
  hlt

@is_not_prime:
  clr 0
  clr 1
  clr 2
  clr 3
  show $p
  showf
  hlt

! Done... :)
