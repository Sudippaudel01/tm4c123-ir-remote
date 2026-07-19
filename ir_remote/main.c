// IR Remote Control Replacement
// Main application

//-----------------------------------------------------------------------------
// Hardware Target
//-----------------------------------------------------------------------------

// Target Platform: EK-TM4C123GXL
// Target uC:       TM4C123GH6PM
// System Clock:    40 MHz

// Hardware configuration:
//   UART0 on PA0/PA1 for serial terminal (115200 baud)
//   TSOP13438 IR receiver on PB6 (T0CCP0)
//   IR333-A LED via 2N3904 on PB7 (T0CCP1)

//-----------------------------------------------------------------------------
// Device includes, defines, and assembler directives
//-----------------------------------------------------------------------------

#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "clock.h"
#include "uart0.h"
#include "ir.h"
#include "tm4c123gh6pm.h"

#define MAX_CHARS 80

#define stringEquals(a, b) (strcmp(a, b) == 0)

//-----------------------------------------------------------------------------
// Subroutines
//-----------------------------------------------------------------------------

void getsUart0(char* data)
{
    int count = 0;
    while(true)
    {
        char c = getcUart0();

        // Handle Backspace
        if ((c == 8 || c == 127) && count > 0)
        {
            count--;
            putcUart0(8);    // move cursor back
            putcUart0(' ');  // overwrite character
            putcUart0(8);    // move cursor back again
        }
        // Handle Carriage Return (Enter)
        else if (c == 13)
        {
            data[count] = '\0';
            putsUart0("\r\n");
            return;
        }
        // Handle printable characters
        else if (c >= 32)
        {
            data[count] = c;
            putcUart0(c);    // echo character
            count++;
            if (count == MAX_CHARS)
            {
                data[count] = '\0';
                putsUart0("\r\n");
                return;
            }
        }
    }
}

// Simple atoi: parse decimal number from string, return 0 if invalid
uint8_t parseNumber(char* str)
{
    uint8_t result = 0;
    while(*str >= '0' && *str <= '9')
    {
        result = result * 10 + (*str - '0');
        str++;
    }
    return result;
}

//-----------------------------------------------------------------------------
// Main
//-----------------------------------------------------------------------------

int main(void)
{
    char buffer[MAX_CHARS + 1];

    initSystemClockTo40Mhz();
    initUart0();
    initIr();

    putsUart0("\r\n");
    putsUart0("IR Remote Control Replacement\r\n");
    putsUart0("Commands: xmit <1-16>, recv <1-16>, info <1-16>, test\r\n");
    putsUart0("         volup, voldown\r\n");
    putsUart0("Key 1 = ON/OFF  Key 2 = VOL+  Key 3 = VOL-\r\n");
    putsUart0("\r\n");

    if(!isKeyValid(1))
    {
        putsUart0("Key 1 (ON/OFF) is empty. Use 'recv 1' to record your TV power button.\r\n");
        putsUart0("\r\n");
    }
    putsUart0("Keys 2-16: Use 'recv <2-16>' to record any button from your remote.\r\n");
    putsUart0("\r\n");

    while(true)
    {
        putsUart0("> ");
        getsUart0(buffer);

        // Parse command: "xmit N" or "recv N"
        if(buffer[0] == 'x' && buffer[1] == 'm' && buffer[2] == 'i' && buffer[3] == 't' && buffer[4] == ' ')
        {
            uint8_t keyNum = parseNumber(buffer + 5);
            if(keyNum >= 1 && keyNum <= 16)
            {
                irXmit(keyNum);
            }
            else
            {
                putsUart0("Error: key number must be 1-16\r\n");
            }
        }
        else if(buffer[0] == 'r' && buffer[1] == 'e' && buffer[2] == 'c' && buffer[3] == 'v' && buffer[4] == ' ')
        {
            uint8_t keyNum = parseNumber(buffer + 5);
            if(keyNum >= 1 && keyNum <= 16)
            {
                irRecv(keyNum);
            }
            else
            {
                putsUart0("Error: key number must be 1-16\r\n");
            }
        }
        else if(buffer[0] == 'i' && buffer[1] == 'n' && buffer[2] == 'f' && buffer[3] == 'o' && buffer[4] == ' ')
        {
            uint8_t keyNum = parseNumber(buffer + 5);
            if(keyNum >= 1 && keyNum <= 16)
            {
                irInfo(keyNum);
            }
            else
            {
                putsUart0("Error: key number must be 1-16\r\n");
            }
        }
        else if(stringEquals(buffer, "volup"))
        {
            irXmit(2);
        }
        else if(stringEquals(buffer, "voldown"))
        {
            irXmit(3);
        }
        else if(buffer[0] == 't' && buffer[1] == 'e' && buffer[2] == 's' && buffer[3] == 't')
        {
            irTestLed();
        }
        else
        {
            putsUart0("Unknown command. Use: xmit <1-16>, recv <1-16>, info <1-16>, test\r\n");
            putsUart0("                     volup, voldown\r\n");
        }
    }
}
