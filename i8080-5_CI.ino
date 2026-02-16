#include <limits.h>
#include <stddef.h>
//
#define _FEND 0xC0
#define _FESC 0xDB
#define _TFEND 0xDC
#define _TFESC 0xDD
///
#define MAX_DATA_SIZE 128 // Maximal data len = 128 byte (Total = 2*x[128*2] byte data array + 2*head)
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
//
//#define InvertControlBus
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
//#define CmdEEPROMReadByte 0x30
//#define CmdEEPROMReadBlock 0x31
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
#define AckError 0xFF
////
//#define Debug
///
void setup() {
  Disable_BUS_Ctrl(); // Disable BUS control
  //
  Serial.begin (115200); // 9600/115200;
  Serial.println ("i8080-5 CI v.0.1.b. Copyright by Sergey Dorozhkin (aka R2AKT) 2024-2026.");
  //
  Set_Internal_OutPin();
  Set_Internal_InPin();
  Set_CPUPin();
  //
  #ifdef Debug
    Serial.println ("Set to 0x00 outputs (Address+Data");
  #endif
  shiftOut (dataOutPin, clockOutPin, bitOrder, 0x0); // Data
  shiftOut (dataOutPin, clockOutPin, bitOrder, 0x0); // Data
  shiftOut (dataOutPin, clockOutPin, bitOrder, 0x0); // Data
  //
  #ifdef Debug
    Serial.println ("Latch out data.");
  #endif
  digitalWrite (latchOutPin, HIGH);
  digitalWrite (latchOutPin, LOW);
  //
  Enable_BUS_Ctrl (BusModeRead); // Enable BUS control, read mode
}
///
void loop() {
  //
  bool Active = false;
  uint16_t StartAddr = 0;
  int16_t Rx_Len = 0;
  uint8_t Rx_Buff[(MAX_DATA_SIZE*2)+3];
  uint8_t Tx_Buff[(MAX_DATA_SIZE*2)+3];
  //
  Rx_Len = receive_packet (Rx_Buff, true, 100);
  ///
  if (Rx_Len <= 0) {
    return;
  } else {
    ///
    switch (Rx_Buff[0]) {
      case CmdNOP:
        Tx_Buff[0] = CmdNOP;
        break;
      case CmdHold:
        Enable_BUS_Ctrl (BusModeRead); // Enable BUS control, read mode
        //
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
        #ifdef Debug
          Serial.println("Set 'HOLD' pin to HIGH. Wait CPU...");
        #endif
        digitalWrite(HOLDPin, HIGH);
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
          Serial.println("'HLDA' pin is HIGH. Run...");
        #endif
        //
        Tx_Buff[0] = CmdHold;
        Tx_Buff[1] = AckHoldActive;
        send_packet (Tx_Buff, 2);
        //
        Active = true;
        //
        break;
      //
      case CmdUnHold:
        Disable_BUS_Ctrl (); // Disable BUS control 
        //
        #ifdef Debug
          Serial.println("Set 'HOLD' pin to LOW.");
        #endif
        digitalWrite(HOLDPin, LOW);
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
        Tx_Buff[0] = CmdUnHold;
        Tx_Buff[1] = AckUnHold;
        send_packet (Tx_Buff, 2);
        //      
        #ifdef Debug
          Serial.println ("CPU RUN...OK!");
        #endif
        //
        Active = false;
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
        Enable_BUS_Ctrl (BusModeRead); // Enable BUS control, read mode
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
        StartAddr = (Rx_Buff[2]<<8) + Rx_Buff[3];
        //
        #ifdef Debug
          Serial.println ("Read memory block...");
        #endif
        //
        Enable_BUS_Ctrl (BusModeRead); // Enable BUS control, read mode
        //
        for (uint8_t Index = 0; Index < Rx_Buff[1]; Index++) {
          Tx_Buff[3+Index] = MemRead (StartAddr + Index);
        }
        //
        //Disable_BUS_Ctrl (); // Disable BUS control 
        //
        Tx_Buff[0] = AckMemReadBlock;
        Tx_Buff[1] = Rx_Buff[1];
        Tx_Buff[2] = Rx_Buff[2];
        send_packet (Tx_Buff, 3 + Rx_Buff[1]);
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
        Enable_BUS_Ctrl (BusModeWrite); // Enable BUS control, write mode
        //
        MemWrite (Rx_Buff[3], (Rx_Buff[1]<<8) + Rx_Buff[2]);
        //
        //Disable_BUS_Ctrl (); // Disable BUS control 
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
        Enable_BUS_Ctrl (BusModeWrite); // Enable BUS control, write mode
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
        StartAddr = (Rx_Buff[2]<<8) + Rx_Buff[3];
        //
        #ifdef Debug
          Serial.println ("Write memory block...");
        #endif
        //
        Enable_BUS_Ctrl (BusModeWrite); // Enable BUS control, write mode
        //
        for (uint8_t Index = 0; Index < Rx_Buff[1]; Index++) {
          MemWrite (Rx_Buff[Index + 4], StartAddr + Index);
        }
        //
        //Disable_BUS_Ctrl (); // Disable BUS control 
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
        Enable_BUS_Ctrl (BusModeWrite); // Enable BUS control, write mode
        //
        EEPROMWrite (Rx_Buff[3], (Rx_Buff[1]<<8) + Rx_Buff[2]);
        //
        //Disable_BUS_Ctrl (); // Disable BUS control 
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
        Enable_BUS_Ctrl (BusModeWrite); // Enable BUS control, write mode
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
        StartAddr = (Rx_Buff[2]<<8) + Rx_Buff[3];
        //
        #ifdef Debug
          Serial.println ("Write EEPROM block...");
        #endif
        //
        Enable_BUS_Ctrl (BusModeWrite); // Enable BUS control, write mode
        //
        for (uint8_t Index = 0; Index < Rx_Buff[1]; Index++) {
          EEPROMWrite (Rx_Buff[Index + 4], StartAddr + Index);
          delay (1);
        }
        //
        //Disable_BUS_Ctrl (); // Disable BUS control 
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
        Enable_BUS_Ctrl (BusModeRead); // Enable BUS control, read mode
        //
        Tx_Buff[3] = IORead ((Rx_Buff[1]<<8) + Rx_Buff[2]);
        //
        //Disable_BUS_Ctrl (); // Disable BUS control 
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
        StartAddr = (Rx_Buff[2]<<8) + Rx_Buff[3];
        //
        #ifdef Debug
          Serial.println ("Read IO block...");
        #endif
        //
        Enable_BUS_Ctrl (BusModeRead); // Enable BUS control, read mode
        //
        for (uint8_t Index = 0; Index < Rx_Buff[1]; Index++) {
          Tx_Buff[3+Index] = IORead (StartAddr + Index);
        }
        //
        //Disable_BUS_Ctrl (); // Disable BUS control 
        //
        Tx_Buff[0] = AckIOReadBlock;
        Tx_Buff[1] = Rx_Buff[1];
        Tx_Buff[2] = Rx_Buff[2];
        send_packet (Tx_Buff, 3 + Rx_Buff[1]);
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
        Enable_BUS_Ctrl (BusModeWrite); // Enable BUS control, write mode
        //
        IOWrite (Rx_Buff[3], (Rx_Buff[1]<<8) + Rx_Buff[2]);
        //
        //Disable_BUS_Ctrl (); // Disable BUS control 
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
        Enable_BUS_Ctrl (BusModeWrite); // Enable BUS control, write mode
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
        StartAddr = (Rx_Buff[2]<<8) + Rx_Buff[3];
        //
        #ifdef Debug
          Serial.println ("Write IO block...");
        #endif
        //
        Enable_BUS_Ctrl (BusModeWrite); // Enable BUS control, write mode
        //
        for (uint8_t Index = 0; Index < Rx_Buff[1]; Index++) {
          IOWrite (Rx_Buff[Index + 4], StartAddr + Index);
        }
        //
        //Disable_BUS_Ctrl (); // Disable BUS control 
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
  shiftOut (dataOutPin, clockOutPin, bitOrder, Data); // Data
  shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)(Address>>8)&0xFF); // MSB address
  shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)Address&0xFF); // LSB address
  //
  #ifdef Debug
    Serial.println ("Latch out data.");
  #endif
  digitalWrite (latchOutPin, HIGH);
  digitalWrite (latchOutPin, LOW);
  //
  #ifdef Debug
      Serial.println ("Set 'MemWR' pin to LOW.");
  #endif
  //
  #ifndef InvertControlBus
    digitalWrite (MemW_Pin, LOW);
  #else
    digitalWrite (MemW_Pin, HIGH);
  #endif
  //
  delay (1);
  //
  #ifdef Debug
    Serial.println ("Set 'MemWR' pin to HIGH.");
  #endif
  //
  #ifndef InvertControlBus
    digitalWrite (MemW_Pin, HIGH);
  #else
    digitalWrite (MemW_Pin, LOW);
  #endif
  //
  delay (2);
  //
};
///
void MemWrite (uint8_t Data, uint16_t Address) {
  //Data write to shift registers
  shiftOut (dataOutPin, clockOutPin, bitOrder, Data); // Data
  shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)(Address>>8)&0xFF); // MSB address
  shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)Address&0xFF); // LSB address
  //
  #ifdef Debug
    Serial.println ("Latch out data.");
  #endif
  digitalWrite (latchOutPin, HIGH);
  digitalWrite (latchOutPin, LOW);
  //
  #ifdef Debug
    Serial.println ("Set 'MemWR' pin to LOW.");
  #endif
  //
  #ifndef InvertControlBus
    digitalWrite (MemW_Pin, LOW);
  #else
    digitalWrite (MemW_Pin, HIGH);
  #endif
  //
  #ifdef Debug
    Serial.println ("Set 'MemWR' pin to HIGH.");
  #endif
  //
  #ifndef InvertControlBus
    digitalWrite (MemW_Pin, HIGH);
  #else
    digitalWrite (MemW_Pin, LOW);
  #endif
  //
};
//
uint8_t MemRead (uint16_t Address) {
  //Data write to shift registers
  shiftOut (dataOutPin, clockOutPin, bitOrder, 0x0); // Data
  shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)(Address>>8)&0xFF); // MSB address
  shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)Address&0xFF); // LSB address
  //
  #ifdef Debug
    Serial.println ("Latch out data.");
  #endif
  digitalWrite (latchOutPin, HIGH);
  digitalWrite (latchOutPin, LOW);
  //
  #ifdef Debug
    Serial.println ("Set 'MemRD' pin to LOW.");
  #endif
  //
  #ifndef InvertControlBus
    digitalWrite (MemR_Pin, LOW); // toggle the MRDPin
  #else
    digitalWrite (MemR_Pin, HIGH); // toggle the MRDPin
  #endif
  //
  #ifdef Debug
    Serial.println ("Latch in data.");
  #endif
  digitalWrite (latchInPin, LOW);
  digitalWrite (latchInPin, HIGH);
  //
  uint8_t IncomingValue = shiftIn (dataInPin, clockInPin, bitOrder);
  #ifdef Debug
    Serial.println (IncomingValue);
  #endif
  //
  #ifdef Debug
    Serial.println ("Set 'MemRD' pin to HIGH.");
  #endif
  //
  #ifndef InvertControlBus
    digitalWrite (MemR_Pin, HIGH); // toggle the MRDPin
  #else
    digitalWrite (MemR_Pin, LOW); // toggle the MRDPin
  #endif
  //
  return IncomingValue;
};
//
void IOWrite (uint8_t Data, uint16_t Address) {
  //Data write to shift registers
  shiftOut (dataOutPin, clockOutPin, bitOrder, Data); // Data
  shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)(Address>>8)&0xFF); // MSB address
  shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)Address&0xFF); // LSB address
  //
  #ifdef Debug
    Serial.println ("Latch out data.");
  #endif
  digitalWrite (latchOutPin, HIGH);
  digitalWrite (latchOutPin, LOW);
  //
  #ifdef Debug
    Serial.println ("Set 'IOWR' pin to LOW.");
  #endif
  //
  #ifndef InvertControlBus
    digitalWrite (IOW_Pin, LOW); // toggle the IOWRPin
  #else
    digitalWrite (IOW_Pin, HIGH); // toggle the IOWRPin 
  #endif
  //
  #ifdef Debug
    Serial.println ("Set 'IOWR' pin to HIGH.");
  #endif
  //
  #ifndef InvertControlBus
    digitalWrite (IOW_Pin, HIGH); // toggle the IOWRPin
  #else
    digitalWrite (IOW_Pin, LOW); // toggle the IOWRPin
  #endif
  //
};
//
uint8_t IORead (uint16_t Address) {
  //Data write to shift registers
  shiftOut (dataOutPin, clockOutPin, bitOrder, 0x0); // Data
  shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)(Address>>8)&0xFF); // MSB address
  shiftOut (dataOutPin, clockOutPin, bitOrder, (uint8_t)Address&0xFF); // LSB address
  //
  #ifdef Debug
    Serial.println ("Latch out data.");
  #endif
  digitalWrite (latchOutPin, HIGH);
  digitalWrite (latchOutPin, LOW);
  //
  #ifdef Debug
    Serial.println ("Set 'IORD' pin to LOW.");
  #endif
  //
  #ifndef InvertControlBus
    digitalWrite (IOR_Pin, LOW); // toggle the IORDPin
  #else
    digitalWrite (IOR_Pin, HIGH); // toggle the IORDPin
  #endif
  //
  #ifdef Debug
    Serial.println ("Latch in data.");
  #endif
  digitalWrite (latchInPin, LOW);
  digitalWrite (latchInPin, HIGH);
  //
  uint8_t IncomingValue = shiftIn(dataInPin, clockInPin, bitOrder);
  #ifdef Debug
    Serial.println (IncomingValue);
  #endif
  //
  #ifdef Debug
    Serial.println ("Set 'IORD' pin to HIGH.");
  #endif
  //
  #ifndef InvertControlBus
    digitalWrite (IOR_Pin, HIGH); // toggle the IORDPin
  #else
    digitalWrite (IOR_Pin, LOW); // toggle the IORDPin
  #endif
  //
  return IncomingValue;
};
///
void Enable_BUS_Ctrl (uint8_t BusMode) {
  // 
  #ifdef Debug
    Serial.println ("Set 'Memory' pins to output...");
  #endif
  //
  pinMode (MemW_Pin, OUTPUT);
  pinMode (MemR_Pin, OUTPUT);
  //
  #ifdef Debug
    Serial.println ("Set 'MemWR' pin to HIGH.");
  #endif
  //
  #ifndef InvertControlBus
    digitalWrite (MemW_Pin, HIGH);
  #else
    digitalWrite (MemW_Pin, LOW);
  #endif
  //
  #ifdef Debug
    Serial.println ("Set 'MemRD' pin to HIGH.");
  #endif
  //
  #ifndef InvertControlBus
    digitalWrite (MemR_Pin, HIGH);
  #else
    digitalWrite (MemR_Pin, LOW);
  #endif
  //
  #ifdef Debug
    Serial.println ("Set 'IO' pins to output...");
  #endif
  //
  pinMode (IOW_Pin, OUTPUT);
  pinMode (IOR_Pin, OUTPUT);
  //
  #ifdef Debug
    Serial.println ("Set 'IORD' pin to HIGH.");
  #endif
  //
  #ifndef InvertControlBus
    digitalWrite (IOW_Pin, HIGH);
  #else
    digitalWrite (IOW_Pin, LOW);
  #endif
  //
  #ifdef Debug
    Serial.println ("Set 'IORD' pin to HIGH.");
  #endif
  //
  #ifndef InvertControlBus
    digitalWrite (IOR_Pin, HIGH);
  #else
    digitalWrite (IOR_Pin, LOW);
  #endif
  ///
  #ifdef Debug
    Serial.println ("Enable address output.");
  #endif
  digitalWrite (AddressOutEn, LOW);
  //
  if (BusMode == BusModeRead) {
    #ifdef Debug
      Serial.println ("Disable data output.");
    #endif
    digitalWrite (DataOutEn, HIGH);
  } else {
    #ifdef Debug
      Serial.println ("Enable data output.");
    #endif
    digitalWrite (DataOutEn, LOW);
  }
  //
}
//
void Disable_BUS_Ctrl (void) {
  //
  #ifdef Debug
    Serial.println ("Disable address output.");
  #endif
  digitalWrite (AddressOutEn, HIGH);
  #ifdef Debug
    Serial.println ("Disable data output.");
  #endif
  digitalWrite (DataOutEn, HIGH);
  ///
  #ifdef Debug
    Serial.println ("Set 'Memory' pins to input...");
  #endif
  //
  pinMode (MemW_Pin, INPUT);
  pinMode (MemR_Pin, INPUT);
  //
  #ifdef Debug
    Serial.println ("Set 'IO' pins to input...");
  #endif
  //
  pinMode (IOW_Pin, INPUT);
  pinMode (IOR_Pin, INPUT);
}
//
void Set_Internal_OutPin (void) {
  #ifdef Debug
    Serial.println ("Set 'Internal Out' pins...");
  #endif
  //
  pinMode (latchOutPin, OUTPUT);
  pinMode (clockOutPin, OUTPUT);
  pinMode (dataOutPin, OUTPUT);
  pinMode (DataOutEn, OUTPUT);
  pinMode (AddressOutEn, OUTPUT);
  //
  digitalWrite (latchOutPin, LOW);
  digitalWrite (clockOutPin, LOW);
  digitalWrite (dataOutPin, LOW);
  digitalWrite (DataOutEn, LOW);
  digitalWrite (AddressOutEn, LOW);
}
//
void Set_Internal_InPin (void) {
  #ifdef Debug
    Serial.println ("Set 'Internal In' pins...");
  #endif
  //
  pinMode (latchInPin, OUTPUT);
  pinMode (clockInPin, OUTPUT);
  pinMode (dataInPin, INPUT);
  //
  digitalWrite (latchInPin, HIGH);
  digitalWrite (clockInPin, HIGH);
}
//
void Set_CPUPin (void) {
  #ifdef Debug
    Serial.println ("Set 'CPU' pins...");
  #endif
  //
  pinMode (HOLDPin, OUTPUT);
  pinMode (HLDAPin, INPUT);
  pinMode (BUSInUse, OUTPUT);
  //
  digitalWrite (HOLDPin, LOW);
  digitalWrite (HLDAPin, LOW);
  digitalWrite (BUSInUse, LOW);
}
///////
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
	int16_t RAW_BuffSize = 0;
  //
  if (size > (MAX_DATA_SIZE + 4)*2) {
    // PHY_Error_Num = error_num_oversize;
    return -1;
  }
  RAW_BuffSize = (size + 4) * 2;
  //
	uint8_t *PHY_Exchange_Tx = new uint8_t [RAW_BuffSize];
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
	delete [] PHY_Exchange_Tx;
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
        if ((ESCBuff[i] == _FESC) && (ESCBuff[i+1] == _TFEND)) {
            DeESCBuff[count++] = _FEND;
            i++;
        } else if ((ESCBuff[i] == _FESC) && (ESCBuff[i+1] == _TFESC)) {
            DeESCBuff[count++] = _FESC;
            i++;
        } else {
            DeESCBuff[count++] = ESCBuff[i];
        }
    }
    return count;
}
