# FieldDock 基础 C 驱动

Copyright (c) 2026 fairank。原创文件适用 LicenseRef-FieldDock-NC-1.0。未复制 Flipper 固件或 ST HAL 实现。

当前包含：CC1101 的 SPI PARTNUM/VERSION 读取、共享总线锁定及错误清理；双口供电预算纯函数；从当前原理图资源表生成的 60 个 GPIO 映射。来源是本项目接线表及 [TI CC1101 数据手册](https://www.ti.com/lit/ds/symlink/cc1101.pdf) 的协议事实。状态寄存器必须逐字节读取，每次头字节设置读和 burst 位，不能误用连续自增读取。

`fd_power_evaluate()` 只计算许可输出；实际电压检测、TUSB320LAI 寄存器读取、热点切换处理、上电等待、GPIO 顺序、USB 枚举、RTOS/中断和 STM32WB 启动链接均未实现。它不能独立控制硬件，也不能被称为可烧录整机固件。MCU 复位到主循环前的上拉/下拉和最低启动电流需硬件验证。

对缺失、过期或无效电源报告保持低额度；AUX 有电但额度不足时，不错误借用手机额度。核心电流预算不能把两个端口相加；外部探头只允许 AUX 3 A 广告条件，且仍受板上支路上限限制。预算常量来自当前阻值计算，样板实测后仍需复核。

编译：使用 C99 编译器把 `src/fd_cc1101.c`、`src/fd_power.c`、`tests/test_core.c` 一起编译，头文件路径设为 `include`，然后运行生成的主机测试程序。`tools/verify.py` 接受 Zig 可执行文件路径，将主机测试和 Cortex-M4 freestanding 对象编译结果保存到 build/。对象编译不是完整镜像链接、烧录或上板验证。

NFC、LF RFID、红外、iButton、microSD 和探头协议实现待后续添加；不会用空函数伪装成已支持功能。
