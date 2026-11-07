# 素材完整性与来源

当前两套 Skill 的全部35个图片资产均与交接时源文件逐字节一致，包括4张人物参考、10张动作参考、纸蓝底图/母版/蒙版、芽仔锚点与示例。主标题及两种副标题字体也已打包，便于私有开发复现。所有图片/字体见 ASSET_MANIFEST.json；程序运行 tools/verify_assets.py 逐项验hash。

`archive/` 的7个旧备份从tar解包后保存，Git自动去重相同素材，避免只交一串不可检查的压缩包。备份内文本同样经过路径脱敏；历史hash仍是历史证据，当前交接hash以ASSET_MANIFEST为准。原压缩包保留在本地，没有改变活动Skill。

真人原照和Jacky/芽仔品牌资产按用户本次明确要求交接，不赋予第三方任意公开传播权限。用户给的科技博主截图只用于动作/构图参考，不继承他人的身份、品牌或整套画面。

配套 Illustration 的 MIT LICENSE 与 NOTICE、gbro 的许可均原样保留。仓库整体不追加统一开源许可证覆盖私人素材。

字体位于 `skills/jacky-cover/assets/fonts/`：
- Alibaba-PuHuiTi-Bold.ttf，内部family/style要求 Alibaba PuHuiTi / Bold。
- LXGWWenKai-Regular.ttf，默认全局手写副标题字体。
- 字体传奇南安体-免费商用.ttf，仅当前Opus项目副标题采用。

字体来自用户本机制作环境，以原字节用于本次私有交接；文件名中的“免费商用”不是整个仓库公开再分发授权，后续若公开发布需另核对相关许可。

历史报告里已去除个人主目录、临时目录与机器路径，源素材名称和必要品牌名仍保留。没有携带凭据、浏览器会话、venv、缓存或.git历史。
