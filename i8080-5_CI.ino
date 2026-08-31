#include <limits.h>
#include <stddef.h>
//
#define _FEND 0xC0
#define _FESC 0xDB
#define _TFEND 0xDC
#define _TFESC 0xDD
///
#define MAX_DATA_SIZE 200 // Maximal data len = 200 byte
///
#define latchOutPin 9 // Out shift registers latch 
#define dataOutPin 8 // Data out to shift registers 
#define clockOutPin 5 // Data out clock
///
#define latchInPin 2 // In shift register latch 
#define dataInPin 3 // Data in from shift register
#define clockInPin 4 // Data in clock
///
#define DataOutEn 6 // Enable out data register
#define AddressOutEn 7 // Enable out address register
///
#define MemR_Pin A0
#define MemW_Pin A1
//
#define IOR_Pin A2
#define IOW_Pin A3
//
#define HOLDPin 10
#define HLDAPin 12
//
#define BUSInUse 11 // (!BUSEn)
///
#define bitOrder MSBFIRST //LSBFIRST
///
#define BusModeRead 0
#define BusModeWrite 1
////
#define CmdNOP 0x00
//
#define CmdHold 0x01
#define CmdUnHold 0x02
//
#define CmdMemReadByte 0x10
#define CmdMemReadBlock 0x11
#define CmdMemWriteByte 0x12
#define CmdMemWriteBlock 0x13
//
#define CmdIOReadByte 0x20
#define CmdIOReadBlock 0x21
#define CmdIOWriteByte 0x22
#define CmdIOWriteBlock 0x23
//
#define CmdEEPROMWriteByte 0x32
#define CmdEEPROMWriteBlock 0x33
///
#define AckNOP 0x00
//
#define AckHoldWaitLow 0x00
#define AckHoldWaitHigh 0x01
#define AckHoldActive 0x03
//
#define AckWaitUnHold 0xF1
#define AckUnHold 0xF2
//
#define AckMemReadByte 0x10
#define AckMemReadBlock 0x11
#define AckMemWriteByte 0x12
#define AckMemWriteBlock 0x13
//
#define AckIOReadByte 0x20
#define AckIOReadBlock 0x21
#define AckIOWriteByte 0x22
#define AckIOWriteBlock 0x23
//
#define AckEEPROMReadByte 0x30
#define AckEEPROMReadBlock 0x31
#define AckEEPROMWriteByte 0x32
#define AckEEPROMWriteBlock 0x33
//
#define CmdGetSizeSetup 0x40
#define AckGetSizeSetup 0x40
//
#define AckError 0xFF
////
//#define Debug
//#define DirectPortManipulation
///
uint16_t StartAddr = 0;
int16_t Rx_Len = 0;
uint8_t Rx_Buff[(MAX_DATA_SIZE+3)*2] = {};
uint8_t Tx_Buff[(MAX_DATA_SIZE+3)*2] = {};
bool Active = false;
///
void setup() {
  ///
  #ifdef Debug
    Serial.println ("Set 'CPU' pins...");
  #endif
  //
  pinMode (HOLDPin, INPUT);
  digitalWrite (HOLDPin, LOW);
  //
  pinMode (HLDAPin, INPUT);
  digitalWrite (HLDAPin, LOW);
  //
  pinMode (BUSInUse, INPUT);
  digitalWrite (BUSInUse, LOW);
  ///
  #ifdef Debug
    Serial.println ("Set 'Memory' pins to output...");
  #endif
  //
  pinMode (MemW_Pin, OUTPUT);
  digitalWrite (MemW_Pin, LOW);
  //
  pinMode (MemR_Pin, OUTPUT);
  digitalWrite (MemR_Pin, LOW);
  //
  #ifdef Debug
    Serial.println ("Set 'IO' pins to output...");
  #endif
  //
  pinMode (IOW_Pin, OUTPUT);
  digitalWrite (IOW_Pin, LOW);
  //
  pinMode (IOR_Pin, OUTPUT);
  digitalWrite (IOR_Pin, LOW);
  ///
  #ifdef Debug
    Serial.println ("Set 'Internal Out' pins...");
  #endif
  //
  pinMode (latchOutPin, OUTPUT);
  digitalWrite (latchOutPin, LOW);
  //
  pinMode (clockOutPin, OUTPUT);
  digitalWrite (clockOutPin, LOW);
  //
  pinMode (clockInPin, OUTPUT);
  digitalWrite (clockInPin, HIGH);
  //
  pinMode (dataOutPin, OUTPUT);
  digitalWrite (dataOutPin, LOW);
  //
  pinMode (DataOutEn, OUTPUT);
  digitalWrite (DataOutEn, HIGH); // Z-state DataBus
  //
  pinMode (AddressOutEn, OUTPUT);
  digitalWrite (AddressOutEn, HIGH); // Z-state AddressBus
  ///
  #ifdef Debug
    Serial.println ("Set 'Internal In' pins...");
  #endif
  //
  pinMode (latchInPin, OUTPUT);
  digitalWrite (latchInPin, HIGH);
  //
  pinMode (dataInPin, INPUT);
  digitalWrite (dataInPin, LOW);
  ///
  Serial.begin (9600); // 9600/38400/57600/115200;
  //
  #ifdef Debug
    Serial.println ("i8080-5 CI v.0.2.b. Copyright by Sergey Dorozhkin (aka R2AKT) 2024-2026.");
  #endif
  //
  #ifdef Debug
    Serial.println ("Set to 0x00 outputs (Address+Data)");
  #endif
  //
  #ifndef DirectPortManipulation
    shiftOut (dataOutPin, clockOutPin, bitOrder, 0x0); // Data
    shiftOut (dataOutPin, clockOutPin, bitOrder, 0x0); // Data
    shiftOut (dataOutPin, clockOutPin, bitOrder, 0x0); // Data
  #else
    fastShiftOut24 (0x0, 0x0, 0x0);
  #endif
  //
  #ifdef Debug
    Serial.println ("Latch out data.");
  #endif
  //
  #ifndef DirectPortManipulation
    digitalWrite (latchOutPin, HIGH);
    digitalWrite (latchOutPin, LOW);
  #else
    PORTB |= (1 << PB1);  // Установить HIGH
    __asm__("nop\n\t");   // Задержка 1 такт (62.5 нс)
    __asm__("nop\n\t");   // Задержка 1 такт
    PORTB &= ~(1 << PB1); // Установить LOW
  #endif
  //
  Active = false;
}
///
void loop() {
  //
  Rx_Len = receive_packet (Rx_Buff, true, 100);
  ///
  if (Rx_Len <= 0) {
    return;
  } else {
    ///
    switch (Rx_Buff[0]) {
      case CmdGetSizeSetup:
        #ifdef Debug
          Serial.println("'Get Block Size' command");
        #endif
        Tx_Buff[0] = AckGetSizeSetup;
        Tx_Buff[1] = MAX_DATA_SIZE;
        send_packet (Tx_Buff, 2);
        break;
      case CmdNOP:
        #ifdef Debug
          Serial.println("'NOP''command''");
        #endif
        Tx_Buff[0] = CmdNOP;
        send_packet (Tx_Buff, 1);
        break;
      case CmdHold:
        //
        if (!Active) {
          #ifdef Debug
            Serial.println("Check BUS...'HLDA' pin LOW?");
          #endif
          while (digitalRead (HLDAPin)) {
            #ifdef Debug
              Serial.println("Wait LOW 'HLDA' pin...");
            #endif
            //
            Tx_Buff[0] = CmdHold;
            Tx_Buff[1] = AckHoldWaitLow;
            send_packet (Tx_Buff, 2);
            //
            delay (10);
          }
          //
          #ifdef Debug
            Serial.println("Set 'HOLD' pin to HIGH. Wait CPU...");
          #endif
          //
          pinMode (HOLDPin, OUTPUT);
          digitalWrite(HOLDPin, HIGH); // Try HOLD bus
          //
          while (!digitalRead (HLDAPin)) {
            #ifdef Debug
              Serial.println("Wait HIGH 'HLDA' pin...");
            #endif
            Tx_Buff[0] = CmdHold;
            Tx_Buff[1] = AckHoldWaitHigh;
            send_packet (Tx_Buff, 2);
            //
            delay (10);
          }
          #ifdef Debug
            Serial.println("'HLDA' pin is HIGH.");
          #endif
          //
          pinMode (BUSInUse, OUTPUT);
          digitalWrite(BUSInUse, HIGH); // Disable bus
          //
          #ifdef Debug
            Serial.println("'~BusEn' pin is HIGH.");
          #endif
          //
          Tx_Buff[0] = CmdHold;
          Tx_Buff[1] = AckHoldActive;
          send_packet (Tx_Buff, 2);
          //
          Active = true;
          //
          pinMode (DataOutEn, OUTPUT);
          digitalWrite (DataOutEn, LOW); // Active-state DataBus
          //
          pinMode (AddressOutEn, OUTPUT);
          digitalWrite (AddressOutEn, LOW); // Active-state AddressBus
          //
          #ifdef Debug
            Serial.println("RUN...");
          #endif
        } else {
          #ifdef Debug
            Serial.println("Allready HOLD...");
          #endif
          //
          Tx_Buff[0] = CmdHold;
          Tx_Buff[1] = AckHoldActive;
          send_packet (Tx_Buff, 2);
        }
        //
        break;
      //
      case CmdUnHold:
        //
        if (Active) {
          pinMode (DataOutEn, OUTPUT);
          digitalWrite (DataOutEn, HIGH); // Z-state DataBus
          //
          pinMode (AddressOutEn, OUTPUT);
          digitalWrite (AddressOutEn, HIGH); // Z-state AddressBus
          //
          digitalWrite(BUSInUse, LOW); // Enable bus
          pinMode (BUSInUse, INPUT);
          //
          #ifdef Debug
            Serial.println("'~BusEn' pin is LOW.");
          #endif
          //
          digitalWrite(HOLDPin, LOW); // Try UnHOLD bus
          //
          #ifdef Debug
            Serial.println("Set 'HOLD' pin to LOW.");
          #endif
          //
          while (digitalRead (HLDAPin)) {
            #ifdef Debug
              Serial.println("'HLDA' pin HIGH !");
            #endif
            //
            Tx_Buff[0] = CmdUnHold;
            Tx_Buff[1] = AckWaitUnHold;
            send_packet (Tx_Buff, 2);
            //
            delay (50);
          }
          //
          #ifdef Debug
              Serial.println("'HLDA' pin LOW !");
          #endif
          //
          pinMode (HOLDPin, INPUT);
          digitalWrite (HOLDPin, LOW);
          //
          Tx_Buff[0] = CmdUnHold;
          Tx_Buff[1] = AckUnHold;
          send_packet (Tx_Buff, 2);
          //
          Active = false;
          //      
          #ifdef Debug
            Serial.println ("CPU RUN...");
          #endif
        } else {
          #ifdef Debug
            Serial.println("Allready UnHOLD...");
          #endif
          //
          Tx_Buff[0] = CmdUnHold;
          Tx_Buff[1] = AckUnHold;
          send_packet (Tx_Buff, 2);
        }
        //
        break;
      //
      case CmdMemReadByte:
        if (!Active) { // Bus NOT ready!
          #ifdef Debug
            Serial.println ("BUS NOT READY!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        #ifdef Debug
          Serial.println ("Read memory...");
        #endif
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, HIGH); // Z-state DataBus
        //
        Tx_Buff[3] = MemRead ((Rx_Buff[1]<<8) + Rx_Buff[2]);
        //
        //Disable_BUS_Ctrl (); // Disable BUS control 
        //
        Tx_Buff[0] = AckMemReadByte;
        Tx_Buff[1] = Rx_Buff[1];
        Tx_Buff[2] = Rx_Buff[2];
        send_packet (Tx_Buff, 4);
        break;
      //
      case CmdMemReadBlock:
        if (!Active) { // Bus NOT ready!
          #ifdef Debug
            Serial.println ("BUS NOT READY!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        if (Rx_Buff[1] > MAX_DATA_SIZE) { // Max data size limit!
          #ifdef Debug
            Serial.println ("Block size overflow!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        StartAddr = (((Rx_Buff[2]<<8)&0xFF00) + (Rx_Buff[3]&0xFF))&0xFFFF;
        //
        #ifdef Debug
          Serial.println ("Read memory block...");
        #endif
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, HIGH); // Z-state DataBus
        //
        for (uint8_t Index = 0; Index < Rx_Buff[1]; Index++) {
          Tx_Buff[Index + 4] = MemRead (StartAddr + Index);
        }
        //
        Tx_Buff[0] = AckMemReadBlock;
        Tx_Buff[1] = Rx_Buff[1];
        Tx_Buff[2] = Rx_Buff[2];
        Tx_Buff[3] = Rx_Buff[3];
        send_packet (Tx_Buff, 4 + Rx_Buff[1]);
        //
        break;
      //
      case CmdMemWriteByte:
        if (!Active) { // Bus NOT ready!
          #ifdef Debug
            Serial.println ("BUS NOT READY!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        #ifdef Debug
          Serial.println ("Write memory...");
        #endif
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, LOW); // Active-state DataBus
        //
        MemWrite (Rx_Buff[3], (Rx_Buff[1]<<8) + Rx_Buff[2]);
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, HIGH); // Z-state DataBus
        //
        Tx_Buff[0] = AckMemWriteByte;
        Tx_Buff[1] = Rx_Buff[1];
        Tx_Buff[2] = Rx_Buff[2];
        send_packet (Tx_Buff, 3);
        //
        break;
      //
      case CmdMemWriteBlock:
        if (!Active) { // Bus NOT ready!
          #ifdef Debug
            Serial.println ("BUS NOT READY!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        if (Rx_Buff[1] > MAX_DATA_SIZE) { // Max data size limit!
          #ifdef Debug
            Serial.println ("Block size overflow!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        if (Rx_Buff[1] > (Rx_Len - 3)) { // Data len over packet size!
          #ifdef Debug
            Serial.println ("Data size MORE packet size!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        StartAddr = (((Rx_Buff[2]<<8)&0xFF00) + (Rx_Buff[3]&0xFF))&0xFFFF;
        //
        #ifdef Debug
          Serial.println ("Write memory block...");
        #endif
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, LOW); // Active-state DataBus
        //
        for (uint8_t Index = 0; Index < Rx_Buff[1]; Index++) {
          MemWrite (Rx_Buff[Index + 4], StartAddr + Index);
        }
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, HIGH); // Z-state DataBus
        //
        Tx_Buff[0] = AckMemWriteBlock;
        Tx_Buff[1] = Rx_Buff[1];
        Tx_Buff[2] = Rx_Buff[2];
        Tx_Buff[3] = Rx_Buff[3];
        send_packet (Tx_Buff, 4);
        //
        break;
      //
      case CmdEEPROMWriteByte:
        if (!Active) { // Bus NOT ready!
          #ifdef Debug
            Serial.println ("BUS NOT READY!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        #ifdef Debug
          Serial.println ("Write EEPROM...");
        #endif
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, LOW); // Active-state DataBus
        //
        EEPROMWrite (Rx_Buff[3], (Rx_Buff[1]<<8) + Rx_Buff[2]);
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, HIGH); // Z-state DataBus
        //
        Tx_Buff[0] = AckEEPROMWriteByte;
        Tx_Buff[1] = Rx_Buff[1];
        Tx_Buff[2] = Rx_Buff[2];
        send_packet (Tx_Buff, 3);
        //
        break;
      //
      case CmdEEPROMWriteBlock:
        if (!Active) { // Bus NOT ready!
          #ifdef Debug
            Serial.println ("BUS NOT READY!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        if (Rx_Buff[1] > MAX_DATA_SIZE) { // Max data size limit!
          #ifdef Debug
            Serial.println ("Block size overflow!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        if (Rx_Buff[1] > (Rx_Len - 3)) { // Data len over packet size!
          #ifdef Debug
            Serial.println ("Data size MORE packet size!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        StartAddr = (((Rx_Buff[2]<<8)&0xFF00) + (Rx_Buff[3]&0xFF))&0xFFFF;
        //
        #ifdef Debug
          Serial.println ("Write EEPROM block...");
        #endif
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, LOW); // Active-state DataBus
        //
        for (uint8_t Index = 0; Index < Rx_Buff[1]; Index++) {
          EEPROMWrite (Rx_Buff[Index + 4], StartAddr + Index);
          delay (1);
        }
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, HIGH); // Z-state DataBus
        //
        Tx_Buff[0] = AckEEPROMWriteBlock;
        Tx_Buff[1] = Rx_Buff[1];
        Tx_Buff[2] = Rx_Buff[2];
        Tx_Buff[3] = Rx_Buff[3];
        send_packet (Tx_Buff, 4);
        //
        break;
      //
      case CmdIOReadByte:
        if (!Active) { // Bus NOT ready!
          #ifdef Debug
            Serial.println ("BUS NOT READY!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        #ifdef Debug
          Serial.println ("Read IO...");
        #endif
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, HIGH); // Z-state DataBus
        //
        Tx_Buff[3] = IORead ((Rx_Buff[1]<<8) + Rx_Buff[2]);
        //
        Tx_Buff[0] = AckIOReadByte;
        Tx_Buff[1] = Rx_Buff[1];
        Tx_Buff[2] = Rx_Buff[2];
        send_packet (Tx_Buff, 4);
        //
        break;
      //
      case CmdIOReadBlock:
        if (!Active) { // Bus NOT ready!
          #ifdef Debug
            Serial.println ("BUS NOT READY!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        if (Rx_Buff[1] > MAX_DATA_SIZE) { // Max data size limit!
          #ifdef Debug
            Serial.println ("Block size overflow!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        StartAddr = (((Rx_Buff[2]<<8)&0xFF00) + (Rx_Buff[3]&0xFF))&0xFFFF;
        //
        #ifdef Debug
          Serial.println ("Read IO block...");
        #endif
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, HIGH); // Z-state DataBus
        //
        for (uint8_t Index = 0; Index < Rx_Buff[1]; Index++) {
          Tx_Buff[Index + 4] = IORead (StartAddr + Index);
        }
        //
        Tx_Buff[0] = AckIOReadBlock;
        Tx_Buff[1] = Rx_Buff[1];
        Tx_Buff[2] = Rx_Buff[2];
        Tx_Buff[3] = Rx_Buff[3];
        send_packet (Tx_Buff, 4 + Rx_Buff[1]);
        //
        break;
      //
      case CmdIOWriteByte:
        if (!Active) { // Bus NOT ready!
          #ifdef Debug
            Serial.println ("BUS NOT READY!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        #ifdef Debug
          Serial.println ("Write IO...");
        #endif
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, LOW); // Active-state DataBus
        //
        IOWrite (Rx_Buff[3], (Rx_Buff[1]<<8) + Rx_Buff[2]);
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, HIGH); // Z-state DataBus
        //
        Tx_Buff[0] = AckIOWriteByte;
        Tx_Buff[1] = Rx_Buff[1];
        Tx_Buff[2] = Rx_Buff[2];
        send_packet (Tx_Buff, 3);
        //
        break;
      //
      case CmdIOWriteBlock:
                if (!Active) { // Bus NOT ready!
          #ifdef Debug
            Serial.println ("BUS NOT READY!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        if (Rx_Buff[1] > MAX_DATA_SIZE) { // Max data size limit!
          #ifdef Debug
            Serial.println ("Block size overflow!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        if (Rx_Buff[1] > (Rx_Len - 3)) { // Data len over packet size!
          #ifdef Debug
            Serial.println ("Data size MORE packet size!");
          #endif
          //
          Tx_Buff[0] = AckError;
          send_packet (Tx_Buff, 1);
          return;
        }
        //
        StartAddr = (((Rx_Buff[2]<<8)&0xFF00) + (Rx_Buff[3]&0xFF))&0xFFFF;
        //
        #ifdef Debug
          Serial.println ("Write IO block...");
        #endif
        //
        pinMode (DataOutEn, OUTPUT);
        digitalWrite (DataOutEn, HIGH); // Z-state DataBus
        //
        for (uint8_t Index = 0; Index < Rx_Buff[1]; Index++) {
          IOWrite (Rx_Buff[Index + 4], StartAddr + Index);
        }
        //
        Tx_Buff[0] = AckIOWriteBlock;
        Tx_Buff[1] = Rx_Buff[1];
        Tx_Buff[2] = Rx_Buff[2];
        Tx_Buff[3] = Rx_Buff[3];
        send_packet (Tx_Buff, 4);
        //
        break;
      //
      default:
        send_packet (Rx_Buff, Rx_Len); // Echo, debug purpose
        break;
    }
    //
    Rx_Len = 0;
    Rx_Buff[0] = CmdNOP;
  }
//
}
/////
void EEPROMWrite (uint8_t Data, uint16_t Address) {
  //Data write to shift registers
  #ifndef DirectPortManipulation
    shiftOut (dataOutPin, clockOutPin, bitOrder, Data); // Data
    shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)(Address>>8)&0xFF); // MSB address
    shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)Address&0xFF); // LSB address
  #else
    fastShiftOut24 (Data, (uint8_t)(Address>>8)&0xFF, (uint8_t)Address&0xFF);
  #endif
  //
  #ifdef Debug
    Serial.println ("Latch out data.");
  #endif
  #ifndef DirectPortManipulation
    digitalWrite (latchOutPin, HIGH);
    digitalWrite (latchOutPin, LOW);
  #else
    PORTB |= (1 << PB1);  // Установить HIGH
    __asm__("nop\n\t");   // Задержка 1 такт (62.5 нс)
    __asm__("nop\n\t");   // Задержка 1 такт
    PORTB &= ~(1 << PB1); // Установить LOW
  #endif
  //
  #ifdef Debug
      Serial.println ("Set 'MemWR' pin to LOW.");
  #endif
  //
  digitalWrite (MemW_Pin, HIGH);
  //
  delay (1);
  //
  #ifdef Debug
    Serial.println ("Set 'MemWR' pin to HIGH.");
  #endif
  //
  digitalWrite (MemW_Pin, LOW);
  //
  delay (2);
  //
};
///
void MemWrite (uint8_t Data, uint16_t Address) {
  //Data write to shift registers
  #ifndef DirectPortManipulation
    shiftOut (dataOutPin, clockOutPin, bitOrder, Data); // Data
    shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)(Address>>8)&0xFF); // MSB address
    shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)Address&0xFF); // LSB address
  #else
    fastShiftOut24 (Data, (uint8_t)(Address>>8)&0xFF, (uint8_t)Address&0xFF);
  #endif
  //
  #ifdef Debug
    Serial.println ("Latch out data.");
  #endif
  #ifndef DirectPortManipulation
    digitalWrite (latchOutPin, HIGH);
    digitalWrite (latchOutPin, LOW);
  #else
    PORTB |= (1 << PB1);  // Установить HIGH
    __asm__("nop\n\t");   // Задержка 1 такт (62.5 нс)
    __asm__("nop\n\t");   // Задержка 1 такт
    PORTB &= ~(1 << PB1); // Установить LOW
  #endif
  //
  #ifdef Debug
    Serial.println ("Set 'MemWR' pin to LOW.");
  #endif
  //
  digitalWrite (MemW_Pin, HIGH);
  //
  #ifdef Debug
    Serial.println ("Set 'MemWR' pin to HIGH.");
  #endif
  //
  digitalWrite (MemW_Pin, LOW);
  //
};
//
uint8_t MemRead (uint16_t Address) {
  //Data write to shift registers
  #ifndef DirectPortManipulation
    shiftOut (dataOutPin, clockOutPin, bitOrder, 0x0); // Data
    shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)(Address>>8)&0xFF); // MSB address
    shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)Address&0xFF); // LSB address
  #else
    fastShiftOut24 (0x0, (uint8_t)(Address>>8)&0xFF, (uint8_t)Address&0xFF);
  #endif
  //
  #ifdef Debug
    Serial.println ("Latch out data.");
  #endif
  #ifndef DirectPortManipulation
    digitalWrite (latchOutPin, HIGH);
    digitalWrite (latchOutPin, LOW);
  #else
    PORTB |= (1 << PB1);  // Установить HIGH
    __asm__("nop\n\t");   // Задержка 1 такт (62.5 нс)
    __asm__("nop\n\t");   // Задержка 1 такт
    PORTB &= ~(1 << PB1); // Установить LOW
  #endif
  //
  #ifdef Debug
    Serial.println ("Set 'MemRD' pin to LOW.");
  #endif
  //
  digitalWrite (MemR_Pin, HIGH); // toggle the MRDPin
  //
  #ifdef Debug
    Serial.println ("Latch in data.");
  #endif
  //
  #ifndef DirectPortManipulation
    digitalWrite (latchInPin, LOW);
    digitalWrite (latchInPin, HIGH);
  #else
    // Вместо digitalWrite(latchInPin, LOW/HIGH); (пин 2 -> PD2)
    PORTD &= ~(1 << PD2); // LOW
    __asm__("nop\n\t");   // Задержка 1 такт (62.5 нс)
    __asm__("nop\n\t");   // Задержка 1 такт
    PORTD |= (1 << PD2);  // HIGH
  #endif
  //
  #ifndef DirectPortManipulation
    uint8_t IncomingValue = shiftIn (dataInPin, clockInPin, bitOrder);
  #else
    uint8_t IncomingValue = fastShiftIn ();
  #endif
    //
  #ifdef Debug
    Serial.println (IncomingValue);
  #endif
  //
  #ifdef Debug
    Serial.println ("Set 'MemRD' pin to HIGH.");
  #endif
  //
  digitalWrite (MemR_Pin, LOW); // toggle the MRDPin
  //
  return IncomingValue;
};
//
void IOWrite (uint8_t Data, uint16_t Address) {
  // //Data write to shift registers
  #ifndef DirectPortManipulation
    shiftOut (dataOutPin, clockOutPin, bitOrder, Data); // Data
    shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)(Address>>8)&0xFF); // MSB address
    shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)Address&0xFF); // LSB address
  #else
    fastShiftOut24 (Data, (uint8_t)(Address>>8)&0xFF, (uint8_t)Address&0xFF);
  #endif
  //
  #ifdef Debug
    Serial.println ("Latch out data.");
  #endif
  #ifndef DirectPortManipulation
    digitalWrite (latchOutPin, HIGH);
    digitalWrite (latchOutPin, LOW);
  #else
    PORTB |= (1 << PB1);  // Установить HIGH
    __asm__("nop\n\t");   // Задержка 1 такт (62.5 нс)
    __asm__("nop\n\t");   // Задержка 1 такт
    PORTB &= ~(1 << PB1); // Установить LOW
  #endif
  //
  #ifdef Debug
    Serial.println ("Set 'IOWR' pin to LOW.");
  #endif
  //
  digitalWrite (IOW_Pin, HIGH); // toggle the IOWRPin
  //
  #ifdef Debug
    Serial.println ("Set 'IOWR' pin to HIGH.");
  #endif
  //
  digitalWrite (IOW_Pin, LOW); // toggle the IOWRPin
  //
};
//
uint8_t IORead (uint16_t Address) {
  //Data write to shift registers
  #ifndef DirectPortManipulation
    shiftOut (dataOutPin, clockOutPin, bitOrder, 0x0); // Data
    shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)(Address>>8)&0xFF); // MSB address
    shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)Address&0xFF); // LSB address
  #else
    fastShiftOut24 (0x0, (uint8_t)(Address>>8)&0xFF, (uint8_t)Address&0xFF);
  #endif
  //
  #ifdef Debug
    Serial.println ("Latch out data.");
  #endif
  #ifndef DirectPortManipulation
    digitalWrite (latchOutPin, HIGH);
    digitalWrite (latchOutPin, LOW);
  #else
    PORTB |= (1 << PB1);  // Установить HIGH
    __asm__("nop\n\t");   // Задержка 1 такт (62.5 нс)
    __asm__("nop\n\t");   // Задержка 1 такт
    PORTB &= ~(1 << PB1); // Установить LOW
  #endif
  //
  #ifdef Debug
    Serial.println ("Set 'IORD' pin to LOW.");
  #endif
  //
  digitalWrite (IOR_Pin, HIGH); // toggle the IORDPin
  //
  #ifdef Debug
    Serial.println ("Latch in data.");
  #endif
  //
  #ifndef DirectPortManipulation
    digitalWrite (latchInPin, LOW);
    digitalWrite (latchInPin, HIGH);
  #else
    // Вместо digitalWrite(latchInPin, LOW/HIGH); (пин 2 -> PD2)
    PORTD &= ~(1 << PD2); // LOW
    __asm__("nop\n\t");   // Задержка 1 такт (62.5 нс)
    __asm__("nop\n\t");   // Задержка 1 такт
    PORTD |= (1 << PD2);  // HIGH
  #endif
  //
  #ifndef DirectPortManipulation
    uint8_t IncomingValue = shiftIn(dataInPin, clockInPin, bitOrder);
  #else
    uint8_t IncomingValue = fastShiftIn ();
  #endif
  //
  #ifdef Debug
    Serial.println (IncomingValue);
  #endif
  //
  #ifdef Debug
    Serial.println ("Set 'IORD' pin to HIGH.");
  #endif
  //
  digitalWrite (IOR_Pin, LOW); // toggle the IORDPin
  //
  return IncomingValue;
};
///
int16_t receive_packet (uint8_t *Buff, bool Blocking, uint16_t TimeOut) {
  //
  static bool packet_Rx_Sync = false;
	static uint16_t RxBuffLen = 0;
	static unsigned long StartTime = 0;
  static unsigned int packet_Rx_Len = 0;
  //
  StartTime = millis();
  //
  do {
		if (Serial.available() > 0) {
			int8_t incomingByte = Serial.read();
			if (incomingByte != -1) { // Data present
				if ((uint8_t) incomingByte == _FEND) { // KISS (SLIP)
					if (packet_Rx_Sync) { // ReSync packet or End packet
						if (packet_Rx_Len > 0) { // End packet
							packet_Rx_Sync = false;
							////
              RxBuffLen = DeESCData (Buff, Buff, packet_Rx_Len);
              if (RxBuffLen > MAX_DATA_SIZE) {
                packet_Rx_Sync = false;
                packet_Rx_Len = 0;
                //PHY_Error_Num = error_num_oversize;
                return -1;
              }
							packet_Rx_Len = 0;
							//PHY_Error_Num = error_num_no_error;
							return RxBuffLen;
						} else { // ReSync
							packet_Rx_Len = 0;
							if (!Blocking) { 
								//PHY_Error_Num = error_num_no_error;
								return 0;
							}
						}
					} else {
						packet_Rx_Len = 0;
						packet_Rx_Sync = true;
						if (!Blocking) { 
							//PHY_Error_Num = error_num_no_error;
							return 0;
						}
					}
				} else {
					if (packet_Rx_Sync) {
						if (packet_Rx_Len > MAX_DATA_SIZE) { // Rx buffer overflow
							packet_Rx_Sync = false;
							packet_Rx_Len = 0;
							//PHY_Error_Num = error_num_oversize;
							return -1;
						} else {
							Buff[packet_Rx_Len++] = (uint8_t)(incomingByte&UCHAR_MAX);
							if (!Blocking) { 
								//PHY_Error_Num = error_num_no_error;
								return 0;
							}
						}
					} else {
						if (!Blocking) { 
							//PHY_Error_Num = error_num_error_data;
							return -1;
						}
					}
				}
			} else {
				if (!Blocking) { 
					//PHY_Error_Num = error_num_no_data;
					return 0;
				}
			}
		} else {
			if (!Blocking) { 
				//PHY_Error_Num = error_num_no_data;
				return 0;
			}
		}
		//
		if ((millis() - StartTime) > TimeOut) {
			//PHY_Error_Num = error_num_timeout;
			return -1;
		}
	} while (Blocking);
  return 0;
}
///
int16_t send_packet (const uint8_t *Buff, const size_t size) {

	int16_t RAW_Len = 0;
  //
  if (size > (MAX_DATA_SIZE + 4)*2) {
    // PHY_Error_Num = error_num_oversize;
    return -1;
  }
  //
  uint8_t PHY_Exchange_Tx[(MAX_DATA_SIZE+3)*2] = {};
	RAW_Len = ESCData (PHY_Exchange_Tx, Buff, size);
  //
	Serial.write ((uint8_t)_FEND); // Frame 'Start'
	//
	Serial.write (PHY_Exchange_Tx, RAW_Len);
  //
	Serial.write ((uint8_t)_FEND); // Frame 'End'
	//
	Serial.flush (); // Waits for the transmission to complete.
	//
	// PHY_Error_Num = error_num_no_error;
	//
	return RAW_Len;
}
///
size_t ESCData (uint8_t *ESCBuff, const uint8_t *UnESCBuff, size_t size) {
    size_t count = 0;
    for (size_t i = 0; i < size; i++) {
        if (UnESCBuff[i] == _FEND) {
            ESCBuff[count++] = _FESC;
            ESCBuff[count++] = _TFEND;
        } else if (UnESCBuff[i] == _FESC) {
            ESCBuff[count++] = _FESC;
            ESCBuff[count++] = _TFESC;
        } else {
            ESCBuff[count++] = UnESCBuff[i];
        }
    }
    return count;
}
///
size_t DeESCData (uint8_t *DeESCBuff, const uint8_t *ESCBuff, size_t size) {
    size_t count = 0;
    for (size_t i = 0; i < size; i++) {
        if (ESCBuff[i] == _FESC) {
            if (i + 1 < size) { // Проверяем, есть ли следующий байт
                if (ESCBuff[i+1] == _TFEND) {
                    DeESCBuff[count++] = _FEND;
                    i++;
                } else if (ESCBuff[i+1] == _TFESC) {
                    DeESCBuff[count++] = _FESC;
                    i++;
                } else {
                    DeESCBuff[count++] = ESCBuff[i];
                }
            } else { // Пакет оборвался на _FESC
              return 0;
            }
        } else {
            DeESCBuff[count++] = ESCBuff[i];
        }
    }
    return count;
}
///
// Отправка 3 байт (Data, AddrH, AddrL) с максимальной скоростью
// bitOrder: MSBFIRST
void fastShiftOut24(uint8_t data, uint8_t addrH, uint8_t addrL) {
    uint32_t combined = ((uint32_t)data << 16) | ((uint32_t)addrH << 8) | addrL;
    
    // Сохраняем состояние портов, чтобы не затронуть другие пины
    uint8_t oldSREG = SREG;
    cli(); // Отключаем прерывания для точного тайминга
    
    for (int8_t i = 23; i >= 0; i--) {
        // 1. Устанавливаем DATA (пин 8 -> PB0)
        if ((combined >> i) & 1) {
            PORTB |= (1 << PB0);  // HIGH
        } else {
            PORTB &= ~(1 << PB0); // LOW
        }
        
        // 2. Тактовый импульс CLOCK (пин 5 -> PD5)
        PORTD |= (1 << PD5);  // HIGH
        __asm__("nop\n\t");   // Задержка 1 такт (62.5 нс)
        __asm__("nop\n\t");   // Задержка 1 такт
        PORTD &= ~(1 << PD5); // LOW
    }
    
    SREG = oldSREG; // Восстанавливаем прерывания
}
///
// Быстрое чтение байта (пины: Data=PD3, Clock=PD4)
// bitOrder: MSBFIRST
uint8_t fastShiftIn() {
    uint8_t result = 0;
    uint8_t oldSREG = SREG;
    cli(); // Отключаем прерывания
    
    for (uint8_t i = 0; i < 8; i++) {
        // Тактовый импульс (пин 4 -> PD4)
        PORTD |= (1 << PD4);  // HIGH
        
        // Читаем DATA (пин 3 -> PD3)
        // PIND - это регистр чтения состояния порта D
        if (PIND & (1 << PD3)) {
            result |= (1 << (7 - i)); // MSBFIRST
        }
        
        PORTD &= ~(1 << PD4); // LOW
    }
    
    SREG = oldSREG; // Восстанавливаем прерывания
    return result;
}
