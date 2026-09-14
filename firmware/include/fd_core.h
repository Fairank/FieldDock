/* Copyright (c) 2026 fairank. SPDX-License-Identifier: LicenseRef-FieldDock-NC-1.0 */
#ifndef FD_CORE_H
#define FD_CORE_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
typedef enum { FD_OK=0, FD_INVALID, FD_BUSY, FD_IO, FD_TIMEOUT, FD_POWER_OFF } fd_result;
/* Callbacks are supplied by the board port; this core has no SDK dependency. */
typedef struct {
 void *context;
 bool (*lock)(void *);
 void (*unlock)(void *);
 void (*select)(void *, bool active);
 fd_result (*wait_ready)(void *, uint32_t timeout_ms);
 fd_result (*transfer)(void *, const uint8_t *, uint8_t *, size_t);
 bool (*power_and_bus_ready)(void *);
} fd_spi_bus;
typedef struct { uint8_t part; uint8_t version; } fd_cc1101_id;
fd_result fd_cc1101_read_id(const fd_spi_bus *, fd_cc1101_id *);
/* Supply advertisement values, not raw TUSB320 register bit patterns. */
typedef enum { FD_CC_UNKNOWN=0, FD_CC_DEFAULT, FD_CC_1500, FD_CC_3000 } fd_cc_current;
typedef struct {
 bool attached_sink;
 bool valid_vbus;
 bool accessory;
 bool fault;
 uint32_t age_ms;
 fd_cc_current current;
 bool usb_configured_500ma;
 bool usb_suspended;
} fd_source;
typedef struct {
 fd_source phone, aux;
 bool stop, hardware_allow, tools_requested, probe_requested;
 uint16_t requested_core_ma, requested_probe_ma;
} fd_power_inputs;
typedef struct {
 bool phone_budget_ok, aux_budget_ok, aux_probe_budget_ok;
 bool tools_permitted, probe_permitted;
 uint16_t selected_core_limit_ma;
} fd_power_outputs;
/* A policy decision only. Board-specific sequenced GPIO writes are not implemented. */
fd_power_outputs fd_power_evaluate(const fd_power_inputs *);
#endif
