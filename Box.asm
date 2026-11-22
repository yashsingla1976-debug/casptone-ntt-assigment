
// Box.asm - K = 81
// Box: starts at row 81, 20 rows tall,
// 32 pixels (2 words) wide, left edge.
// Row 81 starts at 16384 + 32*81 = 18976.
// Key pressed -> black box; key released -> box cleared.

(MAIN)
    @KBD
    D=M
    @PRESSED
    D;JNE
    @color
    M=0
    @DRAW
    0;JMP

(PRESSED)
    @color
    M=-1

(DRAW)
    @18976
    D=A
    @addr
    M=D

    @20
    D=A
    @rows
    M=D

(ROWLOOP)
    @addr
    D=M
    @ptr
    M=D

    @2
    D=A
    @cols
    M=D

(COLLOOP)
    @color
    D=M
    @ptr
    A=M
    M=D

    @ptr
    M=M+1

    @cols
    M=M-1
    D=M
    @COLLOOP
    D;JGT

    @32
    D=A
    @addr
    M=D+M

    @rows
    M=M-1
    D=M
    @ROWLOOP
    D;JGT

    @MAIN
    0;JMP
