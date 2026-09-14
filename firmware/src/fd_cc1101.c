/* Copyright (c) 2026 fairank. SPDX-License-Identifier: LicenseRef-FieldDock-NC-1.0 */
#include "fd_core.h"
/* TI SWRS061I, sections 10.1/10.2 and status register map.
 * Read status bytes individually: 0x30/0x31 need both R/W and burst bits.
 * No transmitter configuration, strobe or FIFO writes are issued here.
 */
static fd_result read_status(const fd_spi_bus *b, uint8_t address, uint8_t *value) {
 uint8_t tx[2]={(uint8_t)(0xc0u|address),0}, rx[2]={0,0};
 fd_result result;
 b->select(b->context,true);
 result=b->wait_ready(b->context,10u);
 if(result==FD_OK) result=b->transfer(b->context,tx,rx,sizeof(tx));
 b->select(b->context,false);
 if(result==FD_OK) *value=rx[1];
 return result;
}
fd_result fd_cc1101_read_id(const fd_spi_bus *b, fd_cc1101_id *id) {
 fd_cc1101_id pending={0,0}; fd_result result;
 if(!b||!id||!b->lock||!b->unlock||!b->select||!b->wait_ready||
    !b->transfer||!b->power_and_bus_ready) return FD_INVALID;
 if(!b->lock(b->context)) return FD_BUSY;
 if(!b->power_and_bus_ready(b->context)) {b->unlock(b->context);return FD_POWER_OFF;}
 result=read_status(b,0x30u,&pending.part);
 if(result==FD_OK) result=read_status(b,0x31u,&pending.version);
 b->unlock(b->context);
 if(result==FD_OK) *id=pending;
 return result;
}
