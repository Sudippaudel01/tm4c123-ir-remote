// IR Remote Control Library
// Target: EK-TM4C123GXL, 40 MHz
// IR Receiver: TSOP13438 on PB6 (T0CCP0)
// IR Transmitter: IR333-A via 2N3904 on PB7 (T0CCP1)

#include <stdint.h>
#include <stdbool.h>
#include "tm4c123gh6pm.h"
#include "ir.h"
#include "uart0.h"

#define IR_RX_MASK 64   // PB6
#define IR_TX_MASK 128  // PB7

IRSignal keys[NUM_KEYS];

volatile uint16_t captureBuffer[MAX_EDGES];
volatile uint16_t captureCount;
volatile uint8_t  captureDone;
volatile uint8_t  capturing;
volatile uint32_t lastEdgeTime;

volatile uint32_t gapTimerMs;
volatile uint32_t timeoutCounter;

// initialize timers and GPIO for IR receive and transmit
void initIr(void)
{
    // enable clocks for Timer0, Timer1, Timer2, Port B
    SYSCTL_RCGCTIMER_R |= SYSCTL_RCGCTIMER_R0 | SYSCTL_RCGCTIMER_R1
                        | SYSCTL_RCGCTIMER_R2;
    SYSCTL_RCGCGPIO_R |= SYSCTL_RCGCGPIO_R1;
    _delay_cycles(3);

    // PB6 = input capture (T0CCP0), PB7 = PWM output (T0CCP1)
    GPIO_PORTB_DIR_R &= ~IR_RX_MASK;
    GPIO_PORTB_DIR_R |= IR_TX_MASK;
    GPIO_PORTB_DEN_R |= IR_RX_MASK | IR_TX_MASK;
    GPIO_PORTB_AFSEL_R |= IR_RX_MASK | IR_TX_MASK;
    GPIO_PORTB_PCTL_R &= ~(GPIO_PCTL_PB6_M | GPIO_PCTL_PB7_M);
    GPIO_PORTB_PCTL_R |= GPIO_PCTL_PB6_T0CCP0 | GPIO_PCTL_PB7_T0CCP1;

    // Timer0A - edge capture on PB6, interrupt enabled during recv only
    TIMER0_CTL_R &= ~TIMER_CTL_TAEN;
    TIMER0_CFG_R = TIMER_CFG_16_BIT;
    TIMER0_TAMR_R = TIMER_TAMR_TAMR_CAP | TIMER_TAMR_TACMR;
    TIMER0_CTL_R |= TIMER_CTL_TAEVENT_BOTH;
    TIMER0_TAILR_R = 0xFFFF;
    TIMER0_TAPR_R = 0xFF;
    TIMER0_IMR_R &= ~TIMER_IMR_CAEIM;
    TIMER0_CTL_R |= TIMER_CTL_TAEN;

    // Timer0B - 38 kHz PWM carrier for IR LED
    TIMER0_CTL_R &= ~TIMER_CTL_TBEN;
    TIMER0_TBMR_R = TIMER_TBMR_TBMR_PERIOD | TIMER_TBMR_TBAMS;
    TIMER0_TBILR_R = 1052;       // 40MHz / 38kHz
    TIMER0_TBMATCHR_R = 350;     // ~1/3 duty cycle
    TIMER0_TBPR_R = 0;
    TIMER0_TBPMR_R = 0;
    TIMER0_CTL_R |= TIMER_CTL_TBPWML;
    GPIO_PORTB_AFSEL_R &= ~IR_TX_MASK;
    GPIO_PORTB_PCTL_R  &= ~GPIO_PCTL_PB7_M;
    GPIO_PORTB_DATA_R  &= ~IR_TX_MASK;

    // Timer1A - one-shot delay (polled)
    TIMER1_CTL_R &= ~TIMER_CTL_TAEN;
    TIMER1_CFG_R = TIMER_CFG_32_BIT_TIMER;
    TIMER1_TAMR_R = TIMER_TAMR_TAMR_1_SHOT;

    // Timer2 - free-running 32-bit timestamp at 40 MHz
    TIMER2_CTL_R &= ~TIMER_CTL_TAEN;
    TIMER2_CFG_R = TIMER_CFG_32_BIT_TIMER;
    TIMER2_TAMR_R = TIMER_TAMR_TAMR_PERIOD;
    TIMER2_TAILR_R = 0xFFFFFFFF;
    TIMER2_CTL_R |= TIMER_CTL_TAEN;

    // SysTick - 1 ms tick for gap detection
    NVIC_ST_CTRL_R = 0;
    NVIC_ST_RELOAD_R = 39999;    // 1 ms at 40 MHz
    NVIC_ST_CURRENT_R = 0;

    NVIC_PRI4_R = (NVIC_PRI4_R & 0x00FFFFFF) | (1 << 29); // Timer0A priority 1

    uint8_t i;
    for(i = 0; i < NUM_KEYS; i++)
    {
        keys[i].valid = 0;
        keys[i].count = 0;
    }
}

// Timer0A ISR - records edge timestamps from TSOP output on PB6
void timer0AIsr(void)
{
    uint32_t currentTime = TIMER2_TAV_R;
    TIMER0_ICR_R = TIMER_ICR_CAECINT;

    if(!capturing)
        return;

    gapTimerMs = 0;

    if(captureCount == 0)
    {
        if(GPIO_PORTB_DATA_R & IR_RX_MASK) // skip LOW->HIGH, wait for burst start
            return;
        lastEdgeTime = currentTime;
        captureCount = 1;
        return;
    }

    // Timer2 counts down so delta = older - newer
    uint32_t delta = lastEdgeTime - currentTime;
    uint32_t delta_us = delta / 40;

    if((captureCount - 1) < MAX_EDGES)
    {
        captureBuffer[captureCount - 1] = (delta_us > 65535) ? 65535 : (uint16_t)delta_us;
        captureCount++;
    }
    else
    {
        captureDone = 1;
        capturing = 0;
    }

    lastEdgeTime = currentTime;
}

// SysTick ISR - detects end of IR frame using gap timer
void systickIsr(void)
{
    timeoutCounter++;

    if(capturing && captureCount > 1)
    {
        gapTimerMs++;
        if(captureCount >= 10 && gapTimerMs >= 20)
        {
            captureDone = 1;
            capturing = 0;
        }
        else if(gapTimerMs >= 200)
        {
            captureDone = 1;
            capturing = 0;
        }
    }
}

// blocking delay in microseconds using Timer1A
static void delayUs(uint32_t us)
{
    if(us == 0) return;
    TIMER1_TAILR_R = (us * 40) - 1;
    TIMER1_ICR_R = TIMER_ICR_TATOCINT;
    TIMER1_CTL_R |= TIMER_CTL_TAEN;
    while(!(TIMER1_RIS_R & TIMER_RIS_TATORIS));
    TIMER1_CTL_R &= ~TIMER_CTL_TAEN;
    TIMER1_ICR_R = TIMER_ICR_TATOCINT;
}

// print a uint16 value over UART
static void printUint16(uint16_t n)
{
    char buf[6];
    char tmp[6];
    int8_t pos = 0;
    if(n == 0)
    {
        putcUart0('0');
        return;
    }
    while(n > 0)
    {
        tmp[pos++] = '0' + (n % 10);
        n /= 10;
    }
    int8_t j;
    for(j = 0; j < pos; j++)
        buf[j] = tmp[pos - 1 - j];
    buf[pos] = '\0';
    putsUart0(buf);
}

// record IR signal from remote into key slot N (1-16)
void irRecv(uint8_t keyNum)
{
    if(keyNum < 1 || keyNum > 16)
    {
        putsUart0("Error: recv valid for keys 1-16\r\n");
        return;
    }

    if(keyNum == 1)
        putsUart0("Recording ON/OFF power button for Key 1...\r\n");
    else if(keyNum == 2)
        putsUart0("Recording Volume Up for Key 2...\r\n");
    else if(keyNum == 3)
        putsUart0("Recording Volume Down for Key 3...\r\n");

    // let TSOP settle before capture
    putsUart0("Preparing receiver...\r\n");
    delayUs(500000);
    delayUs(500000);

    putsUart0("Ready - point remote at receiver and press a key...\r\n");

    captureCount = 0;
    captureDone = 0;
    gapTimerMs = 0;
    timeoutCounter = 0;
    capturing = 1;

    // clear any pending interrupt before enabling
    TIMER0_ICR_R = TIMER_ICR_CAECINT;
    NVIC_UNPEND0_R = (1 << 19);

    TIMER0_IMR_R |= TIMER_IMR_CAEIM;
    NVIC_EN0_R = (1 << 19);

    NVIC_ST_CURRENT_R = 0;
    NVIC_ST_CTRL_R = NVIC_ST_CTRL_CLK_SRC | NVIC_ST_CTRL_INTEN | NVIC_ST_CTRL_ENABLE;

    // wait for capture or 10 second timeout
    while(!captureDone && timeoutCounter < 10000);

    TIMER0_IMR_R &= ~TIMER_IMR_CAEIM;
    NVIC_ST_CTRL_R = 0;
    capturing = 0;

    if(captureDone && captureCount > 2)
    {
        uint16_t count = captureCount - 1;
        uint16_t i;
        for(i = 0; i < count && i < MAX_EDGES; i++)
            keys[keyNum - 1].times_us[i] = captureBuffer[i];
        keys[keyNum - 1].count = count;
        keys[keyNum - 1].valid = 1;

        putsUart0("Recorded ");
        printUint16(count);
        putsUart0(" edges for key ");
        printUint16(keyNum);
        putsUart0("\r\n");
    }
    else
    {
        putsUart0("Timeout - no signal received\r\n");
    }
}

// transmit stored IR signal for key N (1-16), sends 3 frames
void irXmit(uint8_t keyNum)
{
    if(keyNum < 1 || keyNum > 16)
    {
        putsUart0("Error: xmit valid for keys 1-16 only\r\n");
        return;
    }

    if(!keys[keyNum - 1].valid)
    {
        putsUart0("Key has no recorded data\r\n");
        return;
    }

    uint16_t count = keys[keyNum - 1].count;
    uint16_t i;
    uint8_t repeat;

    putsUart0("Transmitting key ");
    printUint16(keyNum);
    putsUart0(" (3 frames, ");
    printUint16(count);
    putsUart0(" edges each)...\r\n");

    TIMER0_CTL_R &= ~TIMER_CTL_TBEN;
    GPIO_PORTB_AFSEL_R &= ~IR_TX_MASK;
    GPIO_PORTB_PCTL_R &= ~GPIO_PCTL_PB7_M;
    GPIO_PORTB_DIR_R |= IR_TX_MASK;
    GPIO_PORTB_DATA_R &= ~IR_TX_MASK;

    for(repeat = 0; repeat < 3; repeat++)
    {
        for(i = 0; i < count; i++)
        {
            if((i & 1) == 0)
            {
                // mark - enable 38 kHz carrier
                GPIO_PORTB_AFSEL_R |= IR_TX_MASK;
                GPIO_PORTB_PCTL_R = (GPIO_PORTB_PCTL_R & ~GPIO_PCTL_PB7_M) | GPIO_PCTL_PB7_T0CCP1;
                TIMER0_CTL_R |= TIMER_CTL_TBEN;
            }
            else
            {
                // space - carrier off, PB7 low
                TIMER0_CTL_R &= ~TIMER_CTL_TBEN;
                GPIO_PORTB_AFSEL_R &= ~IR_TX_MASK;
                GPIO_PORTB_PCTL_R &= ~GPIO_PCTL_PB7_M;
                GPIO_PORTB_DIR_R |= IR_TX_MASK;
                GPIO_PORTB_DATA_R &= ~IR_TX_MASK;
            }

            delayUs(keys[keyNum - 1].times_us[i]);
        }

        TIMER0_CTL_R &= ~TIMER_CTL_TBEN;
        GPIO_PORTB_AFSEL_R &= ~IR_TX_MASK;
        GPIO_PORTB_PCTL_R &= ~GPIO_PCTL_PB7_M;
        GPIO_PORTB_DIR_R |= IR_TX_MASK;
        GPIO_PORTB_DATA_R &= ~IR_TX_MASK;

        if(repeat < 2)
            delayUs(40000); // 40 ms gap between frames
    }

    TIMER0_CTL_R &= ~TIMER_CTL_TBEN;
    GPIO_PORTB_AFSEL_R &= ~IR_TX_MASK;
    GPIO_PORTB_PCTL_R &= ~GPIO_PCTL_PB7_M;
    GPIO_PORTB_DIR_R |= IR_TX_MASK;
    GPIO_PORTB_DATA_R &= ~IR_TX_MASK;

    putsUart0("Transmission complete\r\n");
}

// returns true if key N has a recorded signal
bool isKeyValid(uint8_t keyNum)
{
    if(keyNum < 1 || keyNum > 16)
        return false;
    return keys[keyNum - 1].valid == 1;
}

// turn IR LED on solid for 5 seconds to verify circuit (check with phone camera)
void irTestLed(void)
{
    TIMER0_CTL_R &= ~TIMER_CTL_TBEN;
    GPIO_PORTB_AFSEL_R &= ~IR_TX_MASK;
    GPIO_PORTB_PCTL_R &= ~GPIO_PCTL_PB7_M;
    GPIO_PORTB_DIR_R |= IR_TX_MASK;
    GPIO_PORTB_DATA_R |= IR_TX_MASK;

    putsUart0("IR LED ON for 5 sec - check with phone camera...\r\n");

    delayUs(500000);
    delayUs(500000);
    delayUs(500000);
    delayUs(500000);
    delayUs(500000);
    delayUs(500000);
    delayUs(500000);
    delayUs(500000);
    delayUs(500000);
    delayUs(500000);

    GPIO_PORTB_DATA_R &= ~IR_TX_MASK;

    putsUart0("IR LED OFF\r\n");
}

// print timing info for first 10 edges of key N
void irInfo(uint8_t keyNum)
{
    if(keyNum < 1 || keyNum > 16)
    {
        putsUart0("Error: key 1-16\r\n");
        return;
    }
    if(!keys[keyNum - 1].valid)
    {
        putsUart0("Key has no recorded data\r\n");
        return;
    }

    putsUart0("Key ");
    printUint16(keyNum);
    putsUart0(": ");
    printUint16(keys[keyNum - 1].count);
    putsUart0(" edges\r\n");

    uint16_t max = keys[keyNum - 1].count;
    if(max > 10) max = 10;
    uint16_t i;
    for(i = 0; i < max; i++)
    {
        if((i & 1) == 0)
            putsUart0("  Mark:  ");
        else
            putsUart0("  Space: ");
        printUint16(keys[keyNum - 1].times_us[i]);
        putsUart0(" us\r\n");
    }
    if(keys[keyNum - 1].count > 10)
        putsUart0("  ...\r\n");
}
