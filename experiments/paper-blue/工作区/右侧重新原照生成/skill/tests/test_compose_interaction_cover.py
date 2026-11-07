import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from PIL import Image,ImageChops,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('cover',ROOT/'scripts/compose_interaction_cover.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

class CoverTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        im=Image.new('RGBA',(300,400))
        ImageDraw.Draw(im).rectangle((80,50,220,350),fill=(255,255,255,255))
        self.scene=self.root/'scene.png';im.save(self.scene)
        self.text={'lines':[{'text':'如何用GrokBot'},{'text':'搭建自媒体军团','emphasis':'自媒体军团'}]}
    def tearDown(self):self.tmp.cleanup()
    def test_actual_mask_black_values_and_continuity(self):
        p,base,mask,_=c.load_template()
        self.assertEqual(mask.size,(1080,1440))
        self.assertEqual([mask.getpixel((540,round(y*1439)))[3] for y in [0,.38,.50,.60,.68,.77,.9,.94,1]],[0,0,28,82,133,187,236,240,240])
        vals=[mask.getpixel((540,y))[3] for y in range(1440)]
        self.assertTrue(all(0<=b-a<=2 for a,b in zip(vals,vals[1:])))
        self.assertTrue(all(ch.getextrema()==(0,0) for ch in mask.split()[:3]))
    def test_render_really_applies_mask(self):
        im,report,layers=c.render(self.scene,self.text)
        # These pixels have no foreground or text; exact alpha compositing is observable.
        for pt in [(5,720),(5,1079),(5,1439)]:
            source=layers['background.png'].getpixel(pt)
            alpha=layers['black-mask.png'].getpixel(pt)[3]
            expected=tuple(round(ch*(255-alpha)/255) for ch in source[:3])
            self.assertEqual(im.getpixel(pt)[:3],expected)
        self.assertEqual(report['alpha_8bit_samples'],[0,0,28,82,133,187,236,240,240])
    def test_repeated_render_deterministic_and_title_only_change(self):
        first,_,l1=c.render(self.scene,self.text)
        same,_,_=c.render(self.scene,self.text)
        self.assertEqual(c.png(first),c.png(same))
        alternate={'lines':[{'text':'如何用GrokBot'},{'text':'搭建内容团队','emphasis':'内容团队'}]}
        changed,_,l2=c.render(self.scene,alternate)
        diff=ImageChops.difference(first.convert('RGB'),changed.convert('RGB'))
        union=ImageChops.lighter(l1['text.png'].getchannel('A'),l2['text.png'].getchannel('A'))
        outside=union.point(lambda v:255 if v==0 else 0)
        self.assertIsNone(ImageChops.multiply(diff,Image.merge('RGB',(outside,)*3)).getbbox())
        self.assertIsNotNone(diff.getbbox())
    def test_white_subject_stays_opaque_and_no_crop(self):
        _,report,layers=c.render(self.scene,self.text)
        scene=layers['foreground.png'];box=scene.getchannel('A').getbbox()
        self.assertEqual(scene.getpixel(((box[0]+box[2])//2,(box[1]+box[3])//2)),(255,255,255,255))
        self.assertGreaterEqual(box[0],54);self.assertLessEqual(box[2],1026)
        self.assertEqual(report['scene']['source_alpha_bbox'],[80,50,221,351])
    def test_opaque_background_and_fake_transparency_rejected(self):
        for mode in ['RGB','RGBA']:
            with self.subTest(mode=mode):
                p=self.root/f'{mode}.png';Image.new(mode,(300,400),'white').save(p)
                with self.assertRaisesRegex(ValueError,'alpha|transparent'):c.render(p,self.text)
    def test_missing_or_wrong_font_rejected(self):
        with self.assertRaisesRegex(ValueError,'Missing real font'):c.render(self.scene,self.text,font=self.root/'missing.ttf')
        wrong=Path.home()/'Library/Fonts/LXGWWenKai-Regular.ttf'
        if wrong.exists():
            with self.assertRaisesRegex(ValueError,'Font identity mismatch'):c.render(self.scene,self.text,font=wrong)
    def test_text_errors_and_overflow_rejected(self):
        for text in [{'lines':[{'text':'一行'}]}, {'lines':[{'text':'重复重复','emphasis':'重复'},{'text':'第二行'}]}, {'lines':[{'text':'过长'*100},{'text':'第二行'}]}]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):c.render(self.scene,text)
    def test_note_collision_rejected(self):
        text=dict(self.text,note={'text':'不能遮人','xy':[.49,.20],'size':30})
        with self.assertRaisesRegex(ValueError,'overlaps foreground'):c.render(self.scene,text)
    def test_template_tampering_or_double_shading_rejected(self):
        root=self.root/'skill'
        shutil.copytree(ROOT/'references',root/'references')
        shutil.copytree(ROOT/'assets',root/'assets')
        base=Image.open(root/c.BASE).convert('RGBA');mask=Image.open(root/c.MASK).convert('RGBA')
        Image.alpha_composite(base,mask).save(root/c.BASE)
        with self.assertRaisesRegex(ValueError,'asset/hash mismatch'):c.load_template(root)
    def test_reference_plate_and_clear_upper_subject(self):
        p,base,mask,_=c.load_template()
        self.assertEqual(c.digest((ROOT/c.BASE).read_bytes()),p['background']['sha256'])
        upper_right=base.getpixel((1048,144));upper_left=base.getpixel((32,144))
        middle_left=base.getpixel((32,720));middle_center=base.getpixel((540,720))
        self.assertGreater(upper_right[2]-upper_right[0],35)
        self.assertGreater(upper_left[0],upper_right[0]+40)
        self.assertGreater(middle_left[2]-middle_left[0],15)
        self.assertGreater(middle_center[0],middle_left[0]+15)
        self.assertEqual(mask.getpixel((700,500))[3],0)
        self.assertLess(mask.getpixel((700,850))[3],80)
        self.assertGreater(mask.getpixel((700,1150))[3],195)
    def test_lower_cutoff_dissolves_without_repainting_rgb(self):
        p,_=c.profile();scene,info=c.place_scene(self.scene,p)
        y0,y1=info['bottom_dissolve_y'];x=540
        self.assertEqual(scene.getpixel((x,y0))[3],255)
        self.assertEqual(scene.getpixel((x,y1-1))[3],0)
        self.assertEqual(scene.getpixel((x,(y0+y1)//2))[:3],(255,255,255))
        self.assertGreater(scene.getpixel((x,(y0+y1)//2))[3],0)
    def test_explicit_line_breaks_and_independent_size(self):
        content={'lines':[{'text':'如何发挥','size':160},{'text':'Grok Bot最强实力','emphasis':'最强实力'}]}
        _,report,layers=c.render(self.scene,content)
        self.assertEqual([r['text'] for r in report['title_runs']],['如何发挥','Grok Bot最强实力'])
        self.assertEqual(report['title_font_sizes'][0],160)
        self.assertGreater(report['title_font_sizes'][0],report['title_font_sizes'][1])
        self.assertEqual(report['title_runs'][1]['emphasis'],'最强实力')
        colors=set(layers['text.png'].getdata())
        self.assertIn((255,255,255,255),colors)
        self.assertIn((247,147,0,255),colors)
        with self.assertRaisesRegex(ValueError,'overflows'):
            c.render(self.scene,{'lines':[{'text':'如何发挥'},{'text':'Grok Bot最强实力','size':180}]})
    def test_saved_outputs_and_overwrite_rejected(self):
        im,report,layers=c.render(self.scene,self.text)
        out=self.root/'result.png';rp=self.root/'result.json';ld=self.root/'layers'
        c.save_result(im,report,layers,out,rp,ld)
        with Image.open(out) as saved: self.assertEqual(saved.size,(1080,1440))
        with Image.open(ld/'thumbnail.png') as saved: self.assertEqual(saved.size,(270,360))
        self.assertEqual(json.loads(rp.read_text())['font_family_style'],['Alibaba PuHuiTi','Bold'])
        old=out.read_bytes()
        with self.assertRaisesRegex(ValueError,'exists'):c.save_result(im,report,layers,out,rp)
        self.assertEqual(old,out.read_bytes())

if __name__=='__main__':unittest.main()
