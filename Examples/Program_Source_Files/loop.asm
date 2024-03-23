$i = 0
$step = 5
$range = 100

@loop:
    show $i

    noop
    noop
    noop

    ina $i
    add $step
    outa $i

    cmp $range
    jmpl @loop
