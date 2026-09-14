# 第三方来源与发布范围

2026-09-09。本清单与 licensing/FILE-REVIEW.md、licensing/library-inventory.csv 共同记录本次文件审查范围，不把“网上公开”视为可任意再授权。

| 材料 | 已查明条件 | 本项目处理 |
|---|---|---|
| KiCad 官方符号、封装库及本地库集合 | CC BY-SA 4.0，电子设计适用库例外；重新分发库集合仍须保留其许可 | 保留 cad/licenses/KiCad-libraries-LICENSE.md；库集合不附加禁止商用限制；混合符号库中的两个 MOSFET 派生符号保留上游许可，其余项目自制符号按文件审查表区分 |
| Flipper 官方固件 | GPL-3.0，允许商业使用 | 当前新建基础驱动不复制该固件；未来若引入或构成衍生程序，须按其许可处理，不能统一改成 NC |
| Flipper 官方 3D 模型 | 官方仓库 LICENSE 为 GPL-3.0 | 不将其模型放入我们的 NC 模型包；当前外壳来自本项目参数化构造及元件包络，具体源文件边界见文件审查表 |
| Flipper 官方 iOS App | MIT | 尚未复制；若复用保留版权和许可证，不声称独占第三方实现 |
| Flipper 官方电路图 | 文档页写明 educational purposes only；未从该页面查得全套可再授权条款 | 当前 NFC/LF 电路参考过其拓扑，RF 参考过功能分区；本次逐项记录见 licensing/FILE-REVIEW.md；不分发官方电路图、固件、CAD 坐标或模型，不对参考功能、事实或上游作品附加本项目 NC 限制；不因重绘就宣称清除权利问题 |
| 元件厂商数据手册与参考电路 | 条款随厂商和具体资源不同 | 发布自行撰写的参数/接线解释和来源链接；工作目录中的 PDF、截图不自动打包 |
| KiCad、Freerouting、Java、Python、Zig 等工具 | 各有独立许可证 | 只用于生成和验证，不随项目源码包分发可执行文件和缓存；使用工具不等于复制其程序代码 |

依据：[KiCad 库许可](https://www.kicad.org/libraries/license/)、[Flipper 固件许可](https://github.com/flipperdevices/flipperzero-firmware/blob/dev/LICENSE)、[Flipper 模型许可](https://github.com/flipperdevices/flipperzero-3d-models/blob/master/LICENSE)、[Flipper iOS 许可](https://github.com/flipperdevices/Flipper-iOS-App/blob/dev/LICENSE)、[官方电路图说明](https://docs.flipper.net/zero/development/hardware/schematic)。

目录隔离只是工程整理方法，不能自动使本来构成衍生作品或组合程序的材料摆脱上游许可。
