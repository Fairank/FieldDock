/* Copyright (c) 2026 fairank. SPDX-License-Identifier: LicenseRef-FieldDock-NC-1.0 */
#include "fd_core.h"
/* Conservative software policy for the present resistor-selected limits.
 * Maximum branch currents are design calculations, not measured guarantees.
 */
static bool live(const fd_source *s) {
 return s->attached_sink && s->valid_vbus && !s->accessory && !s->fault &&
        s->age_ms<=100u && s->current!=FD_CC_UNKNOWN;
}
static bool typec_high(const fd_source *s) {
 return s->current==FD_CC_1500 || s->current==FD_CC_3000;
}
fd_power_outputs fd_power_evaluate(const fd_power_inputs *i) {
 fd_power_outputs o={0}; bool p,a;
 if(!i)return o;
 p=live(&i->phone);a=live(&i->aux);
 o.phone_budget_ok=p && (typec_high(&i->phone) ||
   (i->phone.current==FD_CC_DEFAULT && i->phone.usb_configured_500ma && !i->phone.usb_suspended));
 o.aux_budget_ok=a && typec_high(&i->aux);
 o.aux_probe_budget_ok=a && i->aux.current==FD_CC_3000;
 /* The power mux prioritizes valid AUX. Never add the two source allowances.
  * A present AUX without a grant must not silently use PHONE's larger limit.
  */
 if(i->aux.valid_vbus)o.selected_core_limit_ma=o.aux_budget_ok?848u:0u;
 else if(i->phone.valid_vbus)o.selected_core_limit_ma=o.phone_budget_ok?459u:0u;
 o.tools_permitted=!i->stop && i->hardware_allow && i->tools_requested &&
   o.selected_core_limit_ma>0u && i->requested_core_ma>0u &&
   i->requested_core_ma<=o.selected_core_limit_ma;
 o.probe_permitted=o.tools_permitted && o.aux_probe_budget_ok && i->probe_requested &&
   i->requested_probe_ma>0u && i->requested_probe_ma<=848u;
 return o;
}
