#include <stdlib.h>

//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////
//  MARVELMIND HEDGEHOG INTERFACING CODE

long hedgehog_x, hedgehog_y; // coordinates of hedgehog (X,Y), mm
long hedgehog_z; // height of hedgehog, mm
int hedgehog_pos_updated; // flag of new data from hedgehog received

bool high_resolution_mode;

#define HEDGEHOG_BUF_SIZE 40 
#define HEDGEHOG_CM_DATA_SIZE 0x10
#define HEDGEHOG_MM_DATA_SIZE 0x16
byte hedgehog_serial_buf[HEDGEHOG_BUF_SIZE];
byte hedgehog_serial_buf_ofs;

#define POSITION_DATAGRAM_ID 0x0001
#define POSITION_DATAGRAM_HIGHRES_ID 0x0011
unsigned int hedgehog_data_id;

typedef union {byte b[2]; unsigned int w;int wi;} uni_8x2_16;
typedef union {byte b[4];float f;unsigned long v32;long vi32;} uni_8x4_32;

// Marvelmind hedgehog support initialize
void setup_hedgehog() {
  Serial1.begin(500000); // hedgehog transmits data on 500 kbps  

  hedgehog_serial_buf_ofs = 0;
  hedgehog_pos_updated = 0;
}

// Marvelmind hedgehog service loop
void loop_hedgehog() {
  int incoming_byte;
  int total_received_in_loop;
  int packet_received;
  bool good_byte;
  byte packet_size;
  uni_8x2_16 un16;
  uni_8x4_32 un32;
  
  total_received_in_loop = 0;
  packet_received = 0;
  
  while(Serial1.available() > 0) {
    if (hedgehog_serial_buf_ofs >= HEDGEHOG_BUF_SIZE) {
      hedgehog_serial_buf_ofs = 0; // restart bufer fill
      break; // buffer overflow
    }
    
    total_received_in_loop++;
    if (total_received_in_loop>100) {
      break; // too much data without required header
    }
      
    incoming_byte = Serial1.read();
    good_byte = false;
    switch(hedgehog_serial_buf_ofs) {
      case 0:
        good_byte = (incoming_byte = 0xff);
        break;
  
      case 1:
        good_byte = (incoming_byte = 0x47);
        break;
  
      case 2:
        good_byte = true;
        break;
  
      case 3:
        hedgehog_data_id = (((unsigned int) incoming_byte)<<8) + hedgehog_serial_buf[2];
        good_byte =  (hedgehog_data_id == POSITION_DATAGRAM_ID) ||
                     (hedgehog_data_id == POSITION_DATAGRAM_HIGHRES_ID);
        break;
  
      case 4:
        switch(hedgehog_data_id) {
          case POSITION_DATAGRAM_ID:
            good_byte = (incoming_byte == HEDGEHOG_CM_DATA_SIZE);
            break;
  
          case POSITION_DATAGRAM_HIGHRES_ID:
            good_byte = (incoming_byte == HEDGEHOG_MM_DATA_SIZE);
            break;
        }
        break;
   
      default:
        good_byte = true;
        break;
  }
      
    if (!good_byte) {
      hedgehog_serial_buf_ofs = 0; // restart bufer fill         
      continue;
    }     
    
    hedgehog_serial_buf[hedgehog_serial_buf_ofs++] = incoming_byte; 
    if (hedgehog_serial_buf_ofs>5) {
      packet_size =  7 + hedgehog_serial_buf[4];
      
      if (hedgehog_serial_buf_ofs == packet_size) { // received packet with required header
        packet_received = 1;
        hedgehog_serial_buf_ofs = 0; // restart bufer fill
        break; 
      }
    }
  }

  if (packet_received) {
    hedgehog_set_crc16(&hedgehog_serial_buf[0], packet_size); // calculate CRC checksum of packet
    if (    (hedgehog_serial_buf[packet_size] == 0   )
         && (hedgehog_serial_buf[packet_size+1] == 0 )) { // checksum success
    
      switch(hedgehog_data_id) {
        case POSITION_DATAGRAM_ID:
          // coordinates of hedgehog (X,Y), cm ==> mm
          un16.b[0] = hedgehog_serial_buf[9];
          un16.b[1] = hedgehog_serial_buf[10];
          hedgehog_x = 10*long(un16.wi);
          
          un16.b[0] = hedgehog_serial_buf[11];
          un16.b[1] = hedgehog_serial_buf[12];
          hedgehog_y = 10*long(un16.wi);
          
          // height of hedgehog, cm ==> mm (FW V3.97+)
          un16.b[0] = hedgehog_serial_buf[13];
          un16.b[1] = hedgehog_serial_buf[14];
          hedgehog_z = 10*long(un16.wi);
          
          hedgehog_pos_updated = 1; // flag of new data from hedgehog received
          high_resolution_mode = false;
          break;

        case POSITION_DATAGRAM_HIGHRES_ID:
          // coordinates of hedgehog (X,Y), mm
          un32.b[0] = hedgehog_serial_buf[9];
          un32.b[1] = hedgehog_serial_buf[10];
          un32.b[2] = hedgehog_serial_buf[11];
          un32.b[3] = hedgehog_serial_buf[12];
          hedgehog_x = un32.vi32;
          
          un32.b[0] = hedgehog_serial_buf[13];
          un32.b[1] = hedgehog_serial_buf[14];
          un32.b[2] = hedgehog_serial_buf[15];
          un32.b[3] = hedgehog_serial_buf[16];
          hedgehog_y = un32.vi32;
          
          // height of hedgehog, mm 
          un32.b[0] = hedgehog_serial_buf[17];
          un32.b[1] = hedgehog_serial_buf[18];
          un32.b[2] = hedgehog_serial_buf[19];
          un32.b[3] = hedgehog_serial_buf[20];
          hedgehog_z = un32.vi32;
          
          hedgehog_pos_updated = 1; // flag of new data from hedgehog received
          high_resolution_mode = true;
          break;
      }
    } 
  }
}

// Calculate CRC-16 of hedgehog packet
void hedgehog_set_crc16(byte *buf, byte size) {
  uni_8x2_16 sum;
  byte shift_cnt;
  byte byte_cnt;
  
  sum.w=0xffffU;
  
  for(byte_cnt=size; byte_cnt>0; byte_cnt--) {
    sum.w=(unsigned int) ((sum.w/256U)*256U + ((sum.w%256U)^(buf[size-byte_cnt])));
    
    for(shift_cnt=0; shift_cnt<8; shift_cnt++) {
       if((sum.w&0x1) == 1) sum.w = (unsigned int)((sum.w>>1)^0xa001U);
                     else sum.w>>=1;
    }
  }
  
  buf[size] = sum.b[0];
  buf[size+1] = sum.b[1]; // little endian
}

//  MARVELMIND HEDGEHOG INTERFACING CODE
//////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

void setup() {
  Serial.begin(500000);
  setup_hedgehog();
}

void loop() {  
  byte lcd_coord_precision;
  char lcd_buf[12];
  
  loop_hedgehog(); // Marvelmind hedgehog service loop
  
  if (hedgehog_pos_updated) { // new data from hedgehog available
    hedgehog_pos_updated = 0; // clear new data flag 

    if (high_resolution_mode) {
      lcd_coord_precision = 3;
    }
    else {
      lcd_coord_precision = 2; 
    }
    
    Serial.print("x: ");
    dtostrf(((float) hedgehog_x)/1000.0f, 4, lcd_coord_precision, lcd_buf);
    Serial.print(lcd_buf);
    
    Serial.print(" y: ");
    dtostrf(((float) hedgehog_y)/1000.0f, 4, lcd_coord_precision, lcd_buf);
    Serial.println(lcd_buf); 
  }
}
