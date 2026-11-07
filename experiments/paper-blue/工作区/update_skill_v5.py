from pathlib import Path
import hashlib
w=Path(__file__).resolve().parent
p=Path('skills/jacky-cover/SKILL.md')
assert hashlib.sha256(p.read_bytes()).hexdigest()==(w/'v5-skill-source.sha256').read_text(), 'Source changed'
s=p.read_text()
anchor='编辑输出也要对照全部保留项，不能因目标缺陷改善就忽略其他漂移。工具 edit 不是像素锁定保证。'
addition='\n\n出现人物白斑、脸型纵横比例变化、五官漂移，或用户反馈“不像本人”时，该候选的人物验收立即不通过。不要继续把这张失真人像或其后续版本当作下一轮编辑底图，即使同时附了原照也不能视为已经恢复身份。回到两张原始身份照；需要重建时，用文字记录已确认构图，只传原照和必要非人像素材，切断失真生成脸的引用链。将原照与新图的脸部等比例裁切并排查看，不通过拉伸脸部或任意缩放头颈修正。分别记录身份、皮肤和版式是否通过；文字或边缘修好了不能替代人物验收。若原照重建仍不像，停止叠改并说明缺口；需要原照像素不变时，提出直接合成路线，按用户授权执行。'
assert anchor in s;p.write_text(s.replace(anchor,anchor+addition,1));print('Updated identity-drift stop and original-photo recovery rule.')
