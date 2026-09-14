# 发布文件的来源核查

2026-09-09。核查范围为当前项目源文件、生成方法及拟发布清单；本记录不承诺诉讼结果或排他技术权利。

- **电路描述和生成程序**：`radio_circuit.py`、`nfc_circuit.py`、`lf_circuit.py` 及其余电路文件是本项目编写的引脚表、连接表和生成代码。NFC/LF 的功能拓扑参考过 Flipper 公布的电路资料，RF 的功能分区亦有参考，必须保留这个来源说明。没有将 Flipper 的原 PDF、页面截图、原 CAD、丝印图或图纸坐标文件纳入发布。不能据此主张对相同功能、电气方法或元件数值的排他权；项目许可只覆盖可保护且由 fairank 有权许可的新增代码、文字和设计表达。
- **原生主板和原理图**：本项目的元件位置、线网命名、分页、布线、安装孔和品牌图形由本地设计过程产生。嵌入的 KiCad 符号与封装保持第三方来源，电子设计适用 KiCad 的库例外。禁止把独立库集合统一改成 NC。
- **标准 KiCad 库子集**：`cad/symbols/` 中除下述原创符号外的符号，以及 `cad/footprints/` 中标准库目录，适用 CC BY-SA 4.0 及 KiCad 库例外。作者为 KiCad 库贡献者；本项目执行了子集抽取、部分封装设置整理和引脚号调整。逐文件哈希及分类见 `library-inventory.csv`，原许可在 `cad/licenses/`。
- **混合符号库 `FieldDock.kicad_sym`**：`Q_PMOS_GSD_FD` 和 `Q_NMOS_GSD_FD` 是 KiCad MOSFET 符号的改名和引脚映射修改，继续适用 CC BY-SA 4.0 及库例外。本文件其余以矩形引脚表绘制的器件符号由项目编写，原创表达适用 FieldDock NC；库文件作为集合分发时必须保留两种许可及此逐符号说明，不得用 NC 限制其中的 KiCad 部分。
- **原创封装**：`FieldDock.pretty/` 的九个封装及 `MountingHole.pretty/MountingHole_2.4mm_M2.kicad_mod` 按器件尺寸和安装要求构造。其可保护的原创表达适用 NC；封装尺寸和通用焊盘规则是技术事实。
- **机械模型**：由本项目参数化盒体、孔、柱、盖、支架、线圈和保守器件包络构造。未导入 Flipper STEP/STL 文件。模型的尺寸与可制造性仍由机械检查和实物验证记录分别说明。
- **基础驱动**：CC1101 寄存器识别与电源许可状态逻辑为新写的 C 代码，未复制 Flipper GPL 固件。将来若引入 GPL 程序或构成其衍生实现，需另行按 GPL 处理，不能沿用 NC 覆盖上游代码。
- **品牌**：Fairank 署名及用户选定的 Niangao v1 母版。图形有 AI 辅助过程，不承诺所有部分自动取得著作权；不公开用户提供的猫照片、私人聊天或账号信息。
- **不随项目分发**：KiCad/Java/Freerouting/Zig/Python/Gmsh 可执行文件、插件、依赖缓存、厂商整份 PDF、网页截图、账户凭据和本地故障日志。

功能参考：[Flipper 官方电路资料](https://docs.flipper.net/zero/development/hardware/schematic)。库条件：[KiCad 官方许可说明](https://www.kicad.org/libraries/license/)。这些引用不代表上游授权 FieldDock 使用其商标、原始图纸或整个项目，也不代表任何上游认可本设计。

C712 uses `C_0402_1005Metric_FieldDock_NoSilk`, derived from the KiCad standard footprint with only its outline silk removed. Its land and courtyard geometry is unchanged. This derivative remains CC BY-SA 4.0 with the KiCad library exception, and is listed in the file inventory.
