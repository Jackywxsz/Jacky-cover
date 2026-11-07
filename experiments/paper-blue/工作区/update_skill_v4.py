from pathlib import Path
import hashlib
w=Path(__file__).resolve().parent
p=Path('skills/jacky-cover/references/visual-system.md')
assert hashlib.sha256(p.read_bytes()).hexdigest()==(w/'v4-skill-source.sha256').read_text(), 'Source changed; inspect before editing'
s=p.read_text()
a='- 手势须自然，关键接触点不被遮挡。真人外沿用简单、窄而干净的纯白描边，视觉起点约为1080px画宽上的2–3px；不要黄色、米黄色或厚纸板式人像边框。描边只在外轮廓，头发边缘避免碎白刺、脸颈不染纸纹；纸物件与芽仔仍可保留暖白纸材质。人像可以延伸至下方渐变后面，但不盖标题。'
b='- 手势须自然，关键接触点不被遮挡。真人默认不加描边：去掉白色、黄色、米黄色轮廓线、光环及纸板垫边，使用干净自然的照片边缘；头发保留自然发丝，脸颈不染纸纹。纸物件与芽仔仍可保留暖白纸材质与剪纸边缘。人像可以延伸至下方渐变后面，但不盖标题。'
assert a in s;s=s.replace(a,b,1)
a='- 默认无副标题；用户指定上方小字时放在上部合适留白，可微调构图以避开头部与主物件。字体按本次参考：若采用轻松手写小字，则用深墨色、细至中等笔画的自然手写感，明显小于底部主标，不默认加底条；没有字体源文件时只能承诺视觉匹配。'
b='- 默认无副标题；用户要求补充小字时，围绕整体构图找合适的场景留白，例如芽仔或隐喻物件下方、主标上方，作为自然的手写批注。不要机械放在画布顶部居中，也不要把某个固定坐标套到所有封面。小字保持克制，避开人脸、动作与主物件，并与主标题留出间距。字体按本次参考，用深墨色、细至中等笔画的自然手写感，明显小于主标，不默认加底条；没有字体源文件时只能承诺视觉匹配。'
assert a in s;p.write_text(s.replace(a,b,1))
print('Updated: no human outline; composition-led small handwritten annotation.')
