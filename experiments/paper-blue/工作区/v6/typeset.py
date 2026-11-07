from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
FONT=Path('skills/jacky-cover/assets/fonts/Alibaba-PuHuiTi-Bold.ttf')
source=Image.open(HERE/'base.png').convert('RGBA')
assert abs(source.width/source.height-3/4)<0.001,'Do not distort portrait to change aspect'
base=source.resize((1080,1440),Image.Resampling.LANCZOS)
layer=Image.new('RGBA',base.size,(0,0,0,0))
draw=ImageDraw.Draw(layer)
lines=['如何用GrokBot','搭建自媒体军团']
size=150
while True:
 font=ImageFont.truetype(str(FONT),size)
 if max(font.getlength(t) for t in lines)<=960:break
 size-=1
assert font.getname()==('Alibaba PuHuiTi','Bold')
placements=[]
for text,y in zip(lines,[1098,1258]):
 x=60
 if text==lines[0]:draw.text((x,y),text,font=font,fill='#FFFFFF',anchor='lt')
 else:
  draw.text((x,y),'搭建',font=font,fill='#FFFFFF',anchor='lt')
  draw.text((x+font.getlength('搭建'),y),'自媒体军团',font=font,fill='#F79300',anchor='lt')
 box=draw.textbbox((x,y),text,font=font,anchor='lt')
 assert box[0]>=50 and box[2]<=1030 and box[3]<=1390,box
 placements.append({'text':text,'size':size,'xy':[x,y],'bbox':box})
layer.save(HERE/'title-layer.png')
out=ROOT/'输出版本/JackyCover-清爽纸蓝-普惠体-3x4-v6.png'
Image.alpha_composite(base,layer).convert('RGB').save(out)
meta={'font_file':str(FONT),'font_family_style':font.getname(),'font_sha256':hashlib.sha256(FONT.read_bytes()).hexdigest(),'font_size':size,'original_size':source.size,'final_size':base.size,'uniform_resize':True,'face_or_skin_edit':False,'main_title_generated':False,'title_placements':placements,'output':str(out)}
(HERE/'typeset-record.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
print(json.dumps(meta,ensure_ascii=False,indent=2))
im=Image.open(out);im.resize((270,360),Image.Resampling.LANCZOS).save(ROOT/'output/v6-信息流.png')
im.crop((620,110,1080,950)).save(ROOT/'output/v6-脸型与肩部.png')
