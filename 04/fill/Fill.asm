// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
//create screen ptr: addr = SCREEN
@SCREEN
D=A
@addr
M=D  //addr = SCREEN

//SCREEN size: 256 x 512 (32x16)
//therefore, there are 256 x 32 memory adresses = 8192
@8192
D=A
@n
M=D  // n=512

// screen iterator
@i
M=0 // i=0

// whether screen will be black or white
@bw
M=-1  // bw=-1  -> 1111 1111 1111 1111

@screenWHITE
M=1

@KBD
M=0


(LISTEN)
  // read keyboard memory address -> Keyboard = RAM[24576]
  @KBD
  D=M
  //if KBD !=0 (char pressed) jump to KEYPRESSED
  @KEYPRESSED
  D; JNE

  //else
    //set bw bit to -bw
    @bw
    M=0

    // check whether screen was most recently turned white 
    @screenWHITE
    D=M

    //if screen is NOT white (==0), then jump to fillscreen to make white
    @FILLSCREEN
    D;JEQ

  @LISTEN
  0;JMP

(KEYPRESSED)
  //set bw bit to -bw
  @bw
  M=-1

  // check whether screen was most recently turned white 
  @screenWHITE
  D=M

  //if screenWHITE==TRUE (!=0)-> fill w/ black
  @FILLSCREEN
  D; JNE

  //else jump back
  @LISTEN
  0;JMP

(FILLSCREEN)
      //loop over screen addr
      (SCREENLOOP)
          @i
          D=M
          @n
          D=D-M  // i -= n
          @ENDFILL
          D;JGT // if i > n goto ENDFILL

          @addr
          D=M
          @R0
          M=D
          @i
          D=M
          @R0
          M=M+D  //R0 = addr + i

          //get content of bw bit
          @bw
          D=M  // D=bw

          @R0
          A=M  // A = RAM[0] (address stored in R0)
          M=D  // addr + i = bw

          @i
          M=M+1 // i+=1

      @SCREENLOOP
      0;JMP


  (ENDFILL)
  @bw
  D=M  //0 or -1
  @screenWHITE
  M=D+1

  //reset i
  @i
  M=0 // i = 0

  // when done, jump to LISTEN
  @LISTEN
  0;JMP
