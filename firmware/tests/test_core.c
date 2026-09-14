/* Copyright (c) 2026 fairank. SPDX-License-Identifier: LicenseRef-FieldDock-NC-1.0 */
#include "fd_core.h"
#include "fd_board_pins.h"
#include <assert.h>
#include <stdio.h>
typedef struct {bool owned,selected,powered,busy;int transactions,unlocks,fail_at;fd_result ready;} fake;
static bool lock_bus(void *p){fake*f=p;if(f->busy)return false;assert(!f->owned);f->owned=true;return true;}
static void unlock_bus(void *p){fake*f=p;assert(f->owned&&!f->selected);f->owned=false;f->unlocks++;}
static void select_bus(void *p,bool a){fake*f=p;assert(f->owned);f->selected=a;}
static fd_result ready_bus(void*p,uint32_t timeout){fake*f=p;assert(f->selected&&timeout==10u);return f->ready;}
static bool powered_bus(void*p){return ((fake*)p)->powered;}
static fd_result transfer_bus(void*p,const uint8_t*tx,uint8_t*rx,size_t n){fake*f=p;
 assert(f->owned&&f->selected&&n==2);f->transactions++;
 /* Check against vendor command bytes, including second status read requiring new CS. */
 assert(tx[0]==(f->transactions==1?0xf0:0xf1));
 if(f->fail_at==f->transactions)return FD_IO;
 rx[0]=0;rx[1]=f->transactions==1?0:0x14;return FD_OK;
}
static void spi_tests(void){fake f={0};fd_cc1101_id id={42,42};
 fd_spi_bus b={&f,lock_bus,unlock_bus,select_bus,ready_bus,transfer_bus,powered_bus};
 assert(fd_cc1101_read_id(&b,&id)==FD_POWER_OFF&&f.transactions==0&&f.unlocks==1);
 f=(fake){0};f.powered=true;f.ready=FD_TIMEOUT;
 assert(fd_cc1101_read_id(&b,&id)==FD_TIMEOUT&&!f.selected&&!f.owned&&id.part==42);
 f=(fake){0};f.powered=true;f.fail_at=2;
 assert(fd_cc1101_read_id(&b,&id)==FD_IO&&id.part==42&&id.version==42&&!f.owned);
 f=(fake){0};f.powered=true;
 assert(fd_cc1101_read_id(&b,&id)==FD_OK&&id.part==0&&id.version==0x14&&f.transactions==2);
 f.busy=true;assert(fd_cc1101_read_id(&b,&id)==FD_BUSY&&f.transactions==2);
 assert(fd_cc1101_read_id(NULL,&id)==FD_INVALID);
}
static fd_source source(fd_cc_current c){fd_source s={0};s.attached_sink=true;s.valid_vbus=true;s.current=c;return s;}
static void policy_tests(void){fd_power_inputs i={0};fd_power_outputs o;
 i.hardware_allow=true;i.tools_requested=true;i.requested_core_ma=400;
 i.phone=source(FD_CC_DEFAULT);o=fd_power_evaluate(&i);assert(!o.tools_permitted&&!o.phone_budget_ok);
 i.phone.usb_configured_500ma=true;o=fd_power_evaluate(&i);assert(o.tools_permitted&&o.selected_core_limit_ma==459);
 i.phone.usb_suspended=true;assert(!fd_power_evaluate(&i).tools_permitted);
 i.phone=source(FD_CC_1500);i.requested_core_ma=460;assert(!fd_power_evaluate(&i).tools_permitted);
 i.requested_core_ma=400;i.aux=source(FD_CC_DEFAULT);o=fd_power_evaluate(&i);assert(o.phone_budget_ok&&!o.tools_permitted&&o.selected_core_limit_ma==0);
 i.aux=source(FD_CC_1500);i.probe_requested=true;i.requested_probe_ma=500;
 o=fd_power_evaluate(&i);assert(o.tools_permitted&&!o.probe_permitted);
 i.aux.current=FD_CC_3000;assert(fd_power_evaluate(&i).probe_permitted);
 i.aux.age_ms=101;assert(!fd_power_evaluate(&i).probe_permitted&&!fd_power_evaluate(&i).tools_permitted);
 i.aux.age_ms=0;i.aux.fault=true;assert(!fd_power_evaluate(&i).tools_permitted);
 i.aux.fault=false;i.stop=true;assert(!fd_power_evaluate(&i).tools_permitted);
 i.stop=false;i.requested_probe_ma=849;assert(!fd_power_evaluate(&i).probe_permitted);
 i.requested_probe_ma=848;i.hardware_allow=false;assert(!fd_power_evaluate(&i).tools_permitted);
 assert(!fd_power_evaluate(NULL).tools_permitted);
}
int main(void){spi_tests();policy_tests();assert(FD_PIN_COUNT==60);puts("PASS: SPI timeout/bus cleanup/atomic ID; source budget/fault/stale/suspend/overload/stop policy; 60 GPIO mappings.");return 0;}
