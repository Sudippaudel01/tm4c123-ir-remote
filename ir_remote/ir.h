// IR Remote Library
// For TM4C123GXL IR Remote Control Replacement Project

//-----------------------------------------------------------------------------
// Hardware Target
//-----------------------------------------------------------------------------

// Target Platform: EK-TM4C123GXL
// Target uC:       TM4C123GH6PM
// System Clock:    40 MHz

// Hardware configuration:
// IR Receiver:
//   TSOP13438 output connected to PB6 (T0CCP0)
// IR Transmitter:
//   IR333-A LED driven via 2N2222 transistor on PB7 (T0CCP1)

//-----------------------------------------------------------------------------
// Device includes, defines, and assembler directives
//-----------------------------------------------------------------------------

#ifndef IR_H_
#define IR_H_

#include <stdint.h>
#include <stdbool.h>

#define MAX_EDGES  200
#define NUM_KEYS   16

typedef struct
{
    uint16_t count;
    uint16_t times_us[MAX_EDGES];
    uint8_t  valid;
} IRSignal;

//-----------------------------------------------------------------------------
// Subroutines
//-----------------------------------------------------------------------------

void initIr(void);
void irRecv(uint8_t keyNum);
void irXmit(uint8_t keyNum);
bool isKeyValid(uint8_t keyNum);
void irTestLed(void);
void irInfo(uint8_t keyNum);

#endif
