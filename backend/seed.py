import asyncio
import edge_tts
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base, SessionLocal
from app.models import Category, Phrase, AdminUser
from app.auth import hash_password
from app.utils.audio_gen import generate_audio_file
from app.config import DEFAULT_USERNAME, DEFAULT_PASSWORD, AUDIO_DIR

os.makedirs(AUDIO_DIR, exist_ok=True)
Base.metadata.create_all(bind=engine)

VOICE = "zh-CN-XiaoxiaoNeural"
RATE = "-10%"
PITCH = "+0Hz"

SENTENCE_DATA = {
    "basic": {
        "name": "บทสนทนาพื้นฐาน",
        "icon": "💬",
        "sentences": [
            {"chinese": "我来自泰国，是泰国人。", "pinyin": "Wǒ láizì Tàiguó, shì Tàiguó rén.", "thai": "ฉันมาจากประเทศไทย เป็นคนไทย"},
            {"chinese": "你是从哪里来的？", "pinyin": "Nǐ shì cóng nǎ lǐ lái de?", "thai": "คุณมาจากที่ไหนเหรอ"},
            {"chinese": "请问，我可以问你一个问题吗？", "pinyin": "Qǐngwèn, wǒ kěyǐ wèn nǐ yí gè wèntí ma?", "thai": "ขอถามหน่อย ฉันขอถามอะไรคุณสักอย่างได้ไหม"},
            {"chinese": "不好意思，我听不懂，可以再解释一下吗？", "pinyin": "Bù hǎoyìsi, wǒ tīng bù dǒng, kěyǐ zài jiěshì yíxià ma?", "thai": "ขอโทษนะ ฉันฟังไม่เข้าใจ ช่วยอธิบายอีกครั้งได้ไหม"},
            {"chinese": "请问，你会说英文吗？我中文不太好。", "pinyin": "Qǐngwèn, nǐ huì shuō Yīngwén ma? Wǒ Zhōngwén bú tài hǎo.", "thai": "คุณพูดภาษาอังกฤษได้ไหม ภาษาจีนฉันยังไม่ค่อยดี"},
            {"chinese": "不好意思，可以帮我一下吗？", "pinyin": "Bù hǎoyìsi, kěyǐ bāng wǒ yíxià ma?", "thai": "ขอโทษนะ ช่วยฉันหน่อยได้ไหม"},
            {"chinese": "如果方便的话，可以给我你的联系方式吗？", "pinyin": "Rúguǒ fāngbiàn de huà, kěyǐ gěi wǒ nǐ de liánxì fāngshì ma?", "thai": "ถ้าสะดวก ขอช่องทางติดต่อของคุณได้ไหม"},
            {"chinese": "不好意思，请说慢一点，我听得不太清楚。", "pinyin": "Bù hǎoyìsi, qǐng shuō màn yìdiǎn, wǒ tīng de bú tài qīngchu.", "thai": "ขอโทษนะ ช่วยพูดช้าหน่อย ฉันฟังไม่ค่อยชัด"},
            {"chinese": "可以给我看一下具体的内容吗？", "pinyin": "Kěyǐ gěi wǒ kàn yíxià jùtǐ de nèiróng ma?", "thai": "ขอดูรายละเอียดหน่อยได้ไหม"},
            {"chinese": "如果可以的话，能写下来给我吗？", "pinyin": "Rúguǒ kěyǐ de huà, néng xiě xiàlái gěi wǒ ma?", "thai": "ช่วยเขียนให้ฉันหน่อยได้ไหม"},
            {"chinese": "请问，这里可以拍照留念吗？", "pinyin": "Qǐngwèn, zhèlǐ kěyǐ pāizhào liúniàn ma?", "thai": "ที่นี่ถ่ายรูปได้ไหม"},
        ]
    },
    "shopping": {
        "name": "การช้อปปิ้ง",
        "icon": "🛍️",
        "sentences": [
            {"chinese": "这个可以便宜一点吗？", "pinyin": "Zhège kěyǐ piányí yìdiǎn ma?", "thai": "อันนี้ลดราคาได้อีกหน่อยไหม"},
            {"chinese": "可以便宜一点吗？我马上付款。", "pinyin": "Kěyǐ piányí yìdiǎn ma? Wǒ mǎshàng fùkuǎn.", "thai": "ลดได้อีกหน่อยไหม ถ้าลดฉันจ่ายเลย"},
            {"chinese": "请问，这个款式有小号吗？", "pinyin": "Qǐngwèn, zhège kuǎnshì yǒu xiǎo hào ma?", "thai": "ขอสอบถาม รุ่นนี้มีไซส์เล็กไหม"},
            {"chinese": "这个有大号的吗？我想试一下。", "pinyin": "Zhège yǒu dà hào de ma? Wǒ xiǎng shì yíxià.", "thai": "รุ่นนี้มีไซส์ใหญ่ไหม ฉันอยากลองดู"},
            {"chinese": "请问，我可以试穿一下这件衣服吗？", "pinyin": "Qǐngwèn, wǒ kěyǐ shìchuān yíxià zhè jiàn yīfu ma?", "thai": "ขออนุญาตลองเสื้อตัวนี้ได้ไหม"},
            {"chinese": "这个款式还有别的颜色可以选择吗？", "pinyin": "Zhège kuǎnshì hái yǒu bié de yánsè kěyǐ xuǎnzé ma?", "thai": "รุ่นนี้มีสีอื่นให้เลือกไหม"},
            {"chinese": "我要这个尺寸的，可以给我拿一件新的吗？", "pinyin": "Wǒ yào zhège chǐcùn de, kěyǐ gěi wǒ ná yí jiàn xīn de ma?", "thai": "ฉันเอาไซส์นี้ ช่วยหยิบตัวใหม่ให้หน่อยได้ไหม"},
            {"chinese": "如果不合适，可以退货或者换货吗？", "pinyin": "Rúguǒ bú héshì, kěyǐ tuìhuò huòzhě huàn huò ma?", "thai": "ถ้าใส่ไม่พอดี สามารถคืนหรือเปลี่ยนได้ไหม"},
            {"chinese": "如果我多买几件，可以再给我优惠吗？", "pinyin": "Rúguǒ wǒ duō mǎi jǐ jiàn, kěyǐ zài gěi wǒ yōuhuì ma?", "thai": "ถ้าฉันซื้อหลายชิ้น สามารถลดเพิ่มได้ไหม"},
            {"chinese": "这个产品的质量有保证吗？", "pinyin": "Zhège chǎnpǐn de zhìliàng yǒu bǎozhèng ma?", "thai": "สินค้านี้มีการรับประกันคุณภาพไหม"},
            {"chinese": "可以开发票吗？", "pinyin": "Kěyǐ kāi fāpiào ma?", "thai": "สามารถออกใบกำกับภาษี / ใบเสร็จได้ไหม"},
            {"chinese": "可以帮我看一下这个尺寸合不合适吗？", "pinyin": "Kěyǐ bāng wǒ kàn yíxià zhège chǐcùn hé bú héshì ma?", "thai": "ช่วยดูให้หน่อยได้ไหมว่าไซส์นี้เหมาะหรือเปล่า"},
            {"chinese": "这个有现货吗？还是需要预订？", "pinyin": "Zhège yǒu xiànhuò ma? Háishi xūyào yùdìng?", "thai": "อันนี้มีของพร้อมขายไหม หรือว่าต้องสั่งจอง"},
            {"chinese": "这是最后的价格吗？还能再便宜一点吗？", "pinyin": "Zhè shì zuìhòu de jiàgé ma? Hái néng zài piányí yìdiǎn ma?", "thai": "นี่ราคาสุดท้ายแล้วใช่ไหม ยังลดได้อีกไหม"},
            {"chinese": "如果产品有问题，可以免费换货吗？", "pinyin": "Rúguǒ chǎnpǐn yǒu wèntí, kěyǐ miǎnfèi huàn huò ma?", "thai": "ถ้าสินค้ามีปัญหา สามารถเปลี่ยนฟรีได้ไหม"},
            {"chinese": "可以帮我算一下总共多少钱吗？", "pinyin": "Kěyǐ bāng wǒ suàn yíxià zǒnggòng duōshǎo qián ma?", "thai": "ช่วยคำนวณราคารวมให้หน่อยได้ไหม"},
            {"chinese": "这个有保修期吗？", "pinyin": "Zhège yǒu bǎoxiū qī ma?", "thai": "อันนี้มีระยะเวลารับประกันไหม"},
            {"chinese": "我想先看看其他款式，再做决定。", "pinyin": "Wǒ xiǎng xiān kàn kan qítā kuǎnshì, zài zuò juédìng.", "thai": "ฉันอยากดูรุ่นอื่นก่อน แล้วค่อยตัดสินใจ"},
            {"chinese": "我再考虑一下，谢谢。", "pinyin": "Wǒ zài kǎolǜ yíxià, xièxie.", "thai": "ฉันขอคิดดูก่อน ขอบคุณนะ"},
            {"chinese": "可以帮我包一下吗？我要送人。", "pinyin": "Kěyǐ bāng wǒ bāo yíxià ma? Wǒ yào sòng rén.", "thai": "ช่วยห่อให้หน่อยได้ไหม ฉันจะเอาไปเป็นของขวัญ"},
        ]
    },
    "restaurant": {
        "name": "ร้านอาหาร",
        "icon": "🍜",
        "sentences": [
            {"chinese": "请问，有菜单可以给我看看吗？", "pinyin": "Qǐngwèn, yǒu càidān kěyǐ gěi wǒ kàn kan ma?", "thai": "ขอสอบถามมีเมนูให้ดูไหม"},
            {"chinese": "我们在等朋友，到了再点菜。", "pinyin": "Wǒmen zài děng péngyou, dàole zài diǎn cài.", "thai": "พวกเรากำลังรอเพื่อนมาถึงแล้วค่อยสั่งอาหาร"},
            {"chinese": "你好，我想点菜。", "pinyin": "Nǐ hǎo, wǒ xiǎng diǎn cài.", "thai": "สวัสดีค่ะ/ครับ ฉันต้องการสั่งอาหาร"},
            {"chinese": "请问，这个菜是什么做的？", "pinyin": "Qǐngwèn, zhège cài shì shénme zuò de?", "thai": "ขอถามหน่อย เมนูนี้ทำจากอะไร"},
            {"chinese": "这个菜不要辣，可以吗？", "pinyin": "Zhège cài bú yào là, kěyǐ ma?", "thai": "เมนูนี้ไม่เอาเผ็ดได้ไหม"},
            {"chinese": "可以做成少辣吗？", "pinyin": "Kěyǐ zuò chéng shǎo là ma?", "thai": "ทำเผ็ดน้อยได้ไหม"},
            {"chinese": "请问，有什么推荐的招牌菜吗？", "pinyin": "Qǐngwèn, yǒu shénme tuījiàn de zhāopái cài ma?", "thai": "มีเมนูแนะนำหรือเมนูเด็ดไหม"},
            {"chinese": "服务员，麻烦结账。", "pinyin": "Fúwùyuán, máfan jiézhàng.", "thai": "พนักงานคะ/ครับ รบกวนคิดเงินด้วย"},
            {"chinese": "这个饮料不要冰，谢谢。", "pinyin": "Zhège yǐnliào bú yào bīng, xièxie.", "thai": "เครื่องดื่มนี้ไม่เอาน้ำแข็ง ขอบคุณ"},
            {"chinese": "这个很好吃，再来一份。", "pinyin": "Zhège hěn hǎochī, zài lái yí fèn.", "thai": "อันนี้อร่อยมาก เอาเพิ่มอีกหนึ่งที่"},
            {"chinese": "可以快一点吗？我们有点赶时间。", "pinyin": "Kěyǐ kuài yìdiǎn ma? Wǒmen yǒudiǎn gǎn shíjiān.", "thai": "ช่วยเร็วหน่อยได้ไหม พวกเราค่อนข้างรีบ"},
            {"chinese": "请问，这个菜多少钱一份？", "pinyin": "Qǐngwèn, zhège cài duōshǎo qián yí fèn?", "thai": "ขอถามหน่อย จานนี้ราคาเท่าไหร่"},
            {"chinese": "请问，上菜大概需要多久？", "pinyin": "Qǐngwèn, shàng cài dàgài xūyào duō jiǔ?", "thai": "อาหารจะใช้เวลาประมาณเท่าไหร่"},
            {"chinese": "我付现金，没有微信和支付宝。", "pinyin": "Wǒ fù xiànjīn, méiyǒu Wēixìn hé Zhīfùbǎo.", "thai": "ฉันจ่ายเป็นเงินสด ไม่มี WeChat และ Alipay"},
            {"chinese": "我是穆斯林，请不要给我猪肉。", "pinyin": "Wǒ shì Mùsīlín, qǐng búyào gěi wǒ zhūròu.", "thai": "ฉันเป็นมุสลิม กรุณาอย่าเสิร์ฟเมนูที่มีหมู"},
            {"chinese": "请不要放香菜。", "pinyin": "Qǐng búyào fàng xiāngcài.", "thai": "กรุณาไม่ใส่ผักชี"},
            {"chinese": "我对虾过敏，请不要放虾。", "pinyin": "Wǒ duì xiā guòmǐn, qǐng búyào fàng xiā.", "thai": "ฉันแพ้กุ้ง กรุณาไม่ใส่กุ้ง"},
            {"chinese": "这个菜适合几个人一起吃？", "pinyin": "Zhège cài shìhé jǐ gè rén yìqǐ chī?", "thai": "จานนี้เหมาะสำหรับกี่คน"},
            {"chinese": "请问，可以刷国际信用卡吗？", "pinyin": "Qǐngwèn, kěyǐ shuā guójì xìnyòngkǎ ma?", "thai": "สามารถใช้บัตรเครดิตต่างประเทศได้ไหม"},
            {"chinese": "麻烦来点冰块。", "pinyin": "Máfan lái diǎn bīngkuài.", "thai": "รบกวนเอาน้ำแข็งหน่อย"},
            {"chinese": "有冰块吗？", "pinyin": "Yǒu bīngkuài ma?", "thai": "มีน้ำแข็งไหม"},
            {"chinese": "麻烦给个公勺。", "pinyin": "Máfan gěi ge gōngsháo.", "thai": "รบกวนขอช้อนกลางหน่อย"},
            {"chinese": "麻烦给个小碗。", "pinyin": "Máfan gěi ge xiǎowǎn.", "thai": "รบกวนขอถ้วยเล็กหน่อย"},
            {"chinese": "麻烦再给个杯子。", "pinyin": "Máfan zài gěi ge bēizi.", "thai": "รบกวนขอแก้วเพิ่มอีกใบ"},
        ]
    },
    "hotel": {
        "name": "โรงแรม",
        "icon": "🏨",
        "sentences": [
            {"chinese": "请问，可以帮我换一个房间吗？", "pinyin": "Qǐngwèn, kěyǐ bāng wǒ huàn yí gè fángjiān ma?", "thai": "ขอสอบถามหน่อยค่ะ/ครับ สามารถช่วยเปลี่ยนห้องให้ได้ไหม"},
            {"chinese": "不好意思，房间的空调坏了，可以找人来修一下吗？", "pinyin": "Bù hǎoyìsi, fángjiān de kōngtiáo huài le, kěyǐ zhǎo rén lái xiū yíxià ma?", "thai": "ขอโทษค่ะ/ครับ แอร์ในห้องเสีย ช่วยส่งช่างมาซ่อมหน่อยได้ไหม"},
            {"chinese": "可以再给我一条毛巾吗？", "pinyin": "Kěyǐ zài gěi wǒ yì tiáo máojīn ma?", "thai": "ขอผ้าเช็ดตัวเพิ่มอีกผืนได้ไหม"},
            {"chinese": "不好意思，洗手间堵了，可以帮我处理一下吗？", "pinyin": "Bù hǎoyìsi, xǐshǒujiān dǔ le, kěyǐ bāng wǒ chǔlǐ yíxià ma?", "thai": "ขอโทษค่ะ/ครับ ห้องน้ำตัน ช่วยจัดการให้หน่อยได้ไหม"},
            {"chinese": "请问，可以帮我叫一辆出租车吗？", "pinyin": "Qǐngwèn, kěyǐ bāng wǒ jiào yí liàng chūzūchē ma?", "thai": "ช่วยเรียกรถแท็กซี่ให้หน่อยได้ไหม"},
            {"chinese": "不好意思，我把房卡弄丢了，可以补办一张吗？", "pinyin": "Bù hǎoyìsi, wǒ bǎ fángkǎ nòng diū le, kěyǐ bǔbàn yì zhāng ma?", "thai": "ขอโทษค่ะ/ครับ ฉันทำคีย์การ์ดหาย สามารถออกใบใหม่ให้ได้ไหม"},
            {"chinese": "不好意思，这个房间不太干净，可以重新打扫一下吗？", "pinyin": "Bù hǎoyìsi, zhège fángjiān bú tài gānjìng, kěyǐ chóngxīn dǎsǎo yíxià ma?", "thai": "ขอโทษค่ะ/ครับ ห้องนี้ไม่ค่อยสะอาด ช่วยทำความสะอาดใหม่ได้ไหม"},
            {"chinese": "床单看起来不太干净，可以帮我更换一下吗？", "pinyin": "Chuángdān kàn qǐlái bú tài gānjìng, kěyǐ bāng wǒ gēnghuàn yíxià ma?", "thai": "ผ้าปูเตียงดูไม่ค่อยสะอาด ช่วยเปลี่ยนให้หน่อยได้ไหม"},
            {"chinese": "房间里没有吹风机，可以送一个过来吗？", "pinyin": "Fángjiān lǐ méiyǒu chuīfēngjī, kěyǐ sòng yí gè guòlái ma?", "thai": "ในห้องไม่มีไดร์เป่าผม ช่วยนำมาให้หน่อยได้ไหม"},
            {"chinese": "我想要一间无烟房，我对烟味比较敏感。", "pinyin": "Wǒ xiǎng yào yì jiān wúyān fáng, wǒ duì yānwèi bǐjiào mǐngǎn.", "thai": "ฉันต้องการห้องปลอดบุหรี่ เพราะค่อนข้างไวต่อกลิ่นควัน"},
            {"chinese": "我想寄存行李，我要出去玩，晚一点再回来拿。", "pinyin": "Wǒ xiǎng jìcún xíngli, wǒ yào chūqù wán, wǎn yìdiǎn zài huílái ná.", "thai": "ฉันขอฝากกระเป๋า จะออกไปเที่ยว แล้วจะกลับมารับทีหลัง"},
            {"chinese": "可以给我一个一次性剃须刀吗？谢谢。", "pinyin": "Kěyǐ gěi wǒ yí gè yícìxìng tìxūdāo ma? Xièxie.", "thai": "ขอมีดโกนแบบใช้ครั้งเดียวหน่อยได้ไหม ขอบคุณค่ะ/ครับ"},
            {"chinese": "这个房间包含早餐吗？餐厅在哪里？几点开始用餐？", "pinyin": "Zhège fángjiān bāohán zǎocān ma? Cāntīng zài nǎlǐ? Jǐ diǎn kāishǐ yòngcān?", "thai": "ห้องนี้รวมอาหารเช้าไหม ห้องอาหารอยู่ที่ไหน เริ่มทานได้กี่โมง"},
            {"chinese": "房间的洗发水和沐浴露用完了。", "pinyin": "Fángjiān de xǐfàshuǐ hé mùyùlù yòng wán le.", "thai": "แชมพูและสบู่อาบน้ำในห้องหมดแล้ว"},
            {"chinese": "可以帮我把行李送到房间吗？", "pinyin": "Kěyǐ bāng wǒ bǎ xíngli sòng dào fángjiān ma?", "thai": "ช่วยนำกระเป๋าไปส่งที่ห้องให้หน่อยได้ไหม"},
            {"chinese": "不好意思，房间的灯不亮，可以检查一下吗？", "pinyin": "Bù hǎoyìsi, fángjiān de dēng bù liàng, kěyǐ jiǎnchá yíxià ma?", "thai": "ขอโทษค่ะ/ครับ ไฟในห้องไม่ติด ช่วยตรวจสอบหน่อยได้ไหม"},
            {"chinese": "如果可以的话，我想要高一点的楼层。", "pinyin": "Rúguǒ kěyǐ de huà, wǒ xiǎng yào gāo yìdiǎn de lóucéng.", "thai": "ถ้าเป็นไปได้ ขอห้องชั้นสูงหน่อย"},
            {"chinese": "房间今天还没有打扫，可以安排清洁吗？", "pinyin": "Fángjiān jīntiān hái méiyǒu dǎsǎo, kěyǐ ānpái qīngjié ma?", "thai": "วันนี้ห้องยังไม่ได้ทำความสะอาด ช่วยจัดแม่บ้านได้ไหม"},
            {"chinese": "空调不太制冷，房间有点热，可以帮我看看吗？", "pinyin": "Kōngtiáo bú tài zhìlěng, fángjiān yǒudiǎn rè, kěyǐ bāng wǒ kàn kan ma?", "thai": "แอร์ไม่ค่อยเย็น ห้องค่อนข้างร้อน ช่วยตรวจสอบให้หน่อยได้ไหม"},
            {"chinese": "我想换到一个比较安静的房间，可以帮我安排吗？", "pinyin": "Wǒ xiǎng huàn dào yí gè bǐjiào ānjìng de fángjiān, kěyǐ bāng wǒ ānpái ma?", "thai": "ฉันอยากเปลี่ยนไปห้องที่เงียบกว่านี้ ช่วยจัดการให้ได้ไหม"},
        ]
    },
    "transport": {
        "name": "การเดินทาง",
        "icon": "🚄",
        "sentences": [
            {"chinese": "请问，这个地方怎么去？", "pinyin": "Qǐngwèn, zhège dìfang zěnme qù?", "thai": "ขอถามหน่อย ที่นี่ไปยังไง"},
            {"chinese": "不好意思，请问洗手间在哪里？", "pinyin": "Bù hǎoyìsi, qǐngwèn xǐshǒujiān zài nǎlǐ?", "thai": "ขอโทษนะคะ/ครับ ห้องน้ำอยู่ตรงไหน"},
            {"chinese": "从这里走路大概需要多久？", "pinyin": "Cóng zhèlǐ zǒulù dàgài xūyào duō jiǔ?", "thai": "จากตรงนี้เดินไปใช้เวลาประมาณกี่นาที"},
            {"chinese": "谢谢你帮我指路。", "pinyin": "Xièxie nǐ bāng wǒ zhǐlù.", "thai": "ขอบคุณที่ช่วยบอกทาง"},
            {"chinese": "不好意思，我好像迷路了，可以帮我吗？", "pinyin": "Bù hǎoyìsi, wǒ hǎoxiàng mílù le, kěyǐ bāng wǒ ma?", "thai": "ขอโทษนะคะ/ครับ เหมือนฉันจะหลงทาง ช่วยหน่อยได้ไหม"},
            {"chinese": "可以帮我看一下地图吗？", "pinyin": "Kěyǐ bāng wǒ kàn yíxià dìtú ma?", "thai": "ช่วยดูแผนที่ให้หน่อยได้ไหม"},
            {"chinese": "请问，是一直直走吗？", "pinyin": "Qǐngwèn, shì yìzhí zhí zǒu ma?", "thai": "ขอถามหน่อย ต้องเดินตรงไปเรื่อย ๆ ใช่ไหม"},
            {"chinese": "是在右边吗？", "pinyin": "Shì zài yòubiān ma?", "thai": "อยู่ทางขวาใช่ไหม"},
            {"chinese": "是在左边吗？", "pinyin": "Shì zài zuǒbiān ma?", "thai": "อยู่ทางซ้ายใช่ไหม"},
            {"chinese": "离这里远吗？", "pinyin": "Lí zhèlǐ yuǎn ma?", "thai": "จากที่นี่ไกลไหม"},
            {"chinese": "请问，最近的地铁站在哪里？", "pinyin": "Qǐngwèn, zuìjìn de dìtiě zhàn zài nǎlǐ?", "thai": "สถานีรถไฟใต้ดินที่ใกล้ที่สุดอยู่ไหน"},
            {"chinese": "如果坐地铁的话，应该怎么走？", "pinyin": "Rúguǒ zuò dìtiě de huà, yīnggāi zěnme zǒu?", "thai": "ถ้าจะนั่งรถไฟใต้ดิน ควรไปทางไหน"},
            {"chinese": "如果方便的话，可以带我过去吗？", "pinyin": "Rúguǒ fāngbiàn de huà, kěyǐ dài wǒ guòqù ma?", "thai": "ถ้าสะดวก ช่วยพาไปหน่อยได้ไหม"},
            {"chinese": "到了以后，请告诉我一声。", "pinyin": "Dàole yǐhòu, qǐng gàosu wǒ yì shēng.", "thai": "พอถึงแล้ว ช่วยบอกฉันด้วย"},
            {"chinese": "请问，出口在哪里？", "pinyin": "Qǐngwèn, chūkǒu zài nǎlǐ?", "thai": "ขอถามหน่อย ทางออกอยู่ตรงไหน"},
        ]
    },
    "health": {
        "name": "สุขภาพ",
        "icon": "🏥",
        "sentences": [
            {"chinese": "这两天身体有点不舒服。", "pinyin": "Zhè liǎng tiān shēntǐ yǒudiǎn bù shūfu.", "thai": "ช่วงสองวันนี้ฉันรู้สึกไม่ค่อยสบายตัว"},
            {"chinese": "我生病了，这几天身体不太好。", "pinyin": "Wǒ shēngbìng le, zhè jǐ tiān shēntǐ bú tài hǎo.", "thai": "ฉันป่วย หลายวันนี้ร่างกายไม่ค่อยดี"},
            {"chinese": "我需要看医生，因为感觉不太舒服。", "pinyin": "Wǒ xūyào kàn yīshēng, yīnwèi gǎnjué bú tài shūfu.", "thai": "ฉันต้องการพบหมอ เพราะรู้สึกไม่ค่อยสบาย"},
            {"chinese": "我感冒了，有点咳嗽和流鼻涕。", "pinyin": "Wǒ gǎnmào le, yǒudiǎn késòu hé liú bítì.", "thai": "ฉันเป็นหวัด มีอาการไอและน้ำมูกไหลเล็กน้อย"},
            {"chinese": "我发烧了，体温有点高。", "pinyin": "Wǒ fāshāo le, tǐwēn yǒudiǎn gāo.", "thai": "ฉันมีไข้ อุณหภูมิร่างกายค่อนข้างสูง"},
            {"chinese": "我头痛，感觉头很沉。", "pinyin": "Wǒ tóutòng, gǎnjué tóu hěn chén.", "thai": "ฉันปวดหัว รู้สึกหนักศีรษะ"},
            {"chinese": "我肚子痛，肚子有点不舒服。", "pinyin": "Wǒ dùzi tòng, dùzi yǒudiǎn bù shūfu.", "thai": "ฉันปวดท้อง รู้สึกไม่ค่อยสบายท้อง"},
            {"chinese": "我拉肚子，这两天常常上厕所。", "pinyin": "Wǒ lādùzi, zhè liǎng tiān chángcháng shàng cèsuǒ.", "thai": "ฉันท้องเสีย สองวันนี้เข้าห้องน้ำบ่อย"},
            {"chinese": "有治拉肚子的药吗？我一直拉肚子。", "pinyin": "Yǒu zhì lādùzi de yào ma? Wǒ yìzhí lādùzi.", "thai": "มียาแก้ท้องเสียไหม ฉันท้องเสียตลอด"},
            {"chinese": "我过敏，身上有点痒。", "pinyin": "Wǒ guòmǐn, shēnshang yǒudiǎn yǎng.", "thai": "ฉันแพ้ รู้สึกคันตามร่างกายเล็กน้อย"},
            {"chinese": "有退烧药吗？我现在发烧了。", "pinyin": "Yǒu tuìshāo yào ma? Wǒ xiànzài fāshāo le.", "thai": "มียาลดไข้ไหม ตอนนี้ฉันมีไข้"},
            {"chinese": "有止痛药吗？我现在很痛。", "pinyin": "Yǒu zhǐtòng yào ma? Wǒ xiànzài hěn tòng.", "thai": "มียาแก้ปวดไหม ตอนนี้ฉันปวดมาก"},
            {"chinese": "有感冒药吗？我有点感冒。", "pinyin": "Yǒu gǎnmào yào ma? Wǒ yǒudiǎn gǎnmào.", "thai": "มียาแก้หวัดไหม ฉันเป็นหวัดเล็กน้อย"},
            {"chinese": "我咳嗽，还有喉咙痛。", "pinyin": "Wǒ késòu, hái yǒu hóulóng tòng.", "thai": "ฉันไอ และเจ็บคอ"},
            {"chinese": "这个怎么吃？要怎么服用？", "pinyin": "Zhège zěnme chī? Yào zěnme fúyòng?", "thai": "ยานี้ต้องกินอย่างไร ควรรับประทานแบบไหน"},
            {"chinese": "一天吃几次？一次吃多少？", "pinyin": "Yì tiān chī jǐ cì? Yí cì chī duōshao?", "thai": "ต้องกินวันละกี่ครั้ง และครั้งละเท่าไหร่"},
            {"chinese": "我现在需要医生，请帮我叫救护车。", "pinyin": "Wǒ xiànzài xūyào yīshēng, qǐng bāng wǒ jiào jiùhùchē.", "thai": "ตอนนี้ฉันต้องการหมอ ช่วยเรียกรถพยาบาลให้หน่อย"},
            {"chinese": "请问，最近的医院在哪里？", "pinyin": "Qǐngwèn, zuìjìn de yīyuàn zài nǎlǐ?", "thai": "ขอถามหน่อย โรงพยาบาลที่ใกล้ที่สุดอยู่ที่ไหน"},
            {"chinese": "我受伤了，需要马上处理伤口。", "pinyin": "Wǒ shòushāng le, xūyào mǎshàng chǔlǐ shāngkǒu.", "thai": "ฉันบาดเจ็บ ต้องทำแผลด่วน"},
            {"chinese": "请问，这附近有药店吗？我需要买药。", "pinyin": "Qǐngwèn, zhè fùjìn yǒu yàodiàn ma? Wǒ xūyào mǎi yào.", "thai": "ขอถามหน่อย แถวนี้มีร้านขายยาไหม ฉันต้องการซื้อยา"},
        ]
    },
    "airport": {
        "name": "สนามบิน",
        "icon": "✈️",
        "sentences": [
            {"chinese": "我是来旅游的。", "pinyin": "Wǒ shì lái lǚyóu de.", "thai": "ฉันเดินทางมาท่องเที่ยว"},
            {"chinese": "我会在这里待几天。", "pinyin": "Wǒ huì zài zhèlǐ dài jǐ tiān.", "thai": "ฉันจะอยู่ที่นี่แค่ไม่กี่วัน"},
            {"chinese": "我只是来短期旅游。", "pinyin": "Wǒ zhǐ shì lái duǎnqī lǚyóu.", "thai": "ฉันมาเที่ยวระยะสั้นเท่านั้น"},
            {"chinese": "我是免签入境。", "pinyin": "Wǒ shì miǎnqiān rùjìng.", "thai": "ฉันเข้าประเทศแบบฟรีวีซ่า"},
            {"chinese": "我是跟旅游团一起来的。", "pinyin": "Wǒ shì gēn lǚyóutuán yìqǐ lái de.", "thai": "ฉันเดินทางมากับคณะทัวร์"},
            {"chinese": "这是我们的团队行程表。", "pinyin": "Zhè shì wǒmen de tuánduì xíngchéng biǎo.", "thai": "นี่คือตารางการเดินทางของคณะทัวร์"},
            {"chinese": "我们的导游在外面等我们。", "pinyin": "Wǒmen de dǎoyóu zài wàimiàn děng wǒmen.", "thai": "ไกด์ของพวกเรารออยู่ด้านนอก"},
            {"chinese": "我会跟着团队一起行动。", "pinyin": "Wǒ huì gēnzhe tuánduì yìqǐ xíngdòng.", "thai": "ฉันจะเดินทางพร้อมกับคณะทัวร์"},
            {"chinese": "这是团队的酒店预订单。", "pinyin": "Zhè shì tuánduì de jiǔdiàn yùdìng dān.", "thai": "นี่คือใบจองโรงแรมของคณะ"},
            {"chinese": "这是我的酒店地址。", "pinyin": "Zhè shì wǒ de jiǔdiàn dìzhǐ.", "thai": "นี่คือที่อยู่โรงแรมของฉัน"},
            {"chinese": "这是我的往返机票。", "pinyin": "Zhè shì wǒ de wǎngfǎn jīpiào.", "thai": "นี่คือตั๋วไป-กลับของฉัน"},
            {"chinese": "我的回程机票已经安排好了。", "pinyin": "Wǒ de huíchéng jīpiào yǐjīng ānpái hǎo le.", "thai": "ตั๋วขากลับของฉันจัดการเรียบร้อยแล้ว"},
            {"chinese": "我是第一次来中国。", "pinyin": "Wǒ shì dì yī cì lái Zhōngguó.", "thai": "นี่เป็นครั้งแรกที่ฉันมาประเทศจีน"},
            {"chinese": "我只是在这里转机。", "pinyin": "Wǒ zhǐ shì zài zhèlǐ zhuǎnjī.", "thai": "ฉันแค่แวะเปลี่ยนเครื่องที่นี่"},
            {"chinese": "我喜欢中国，所以我又来了。", "pinyin": "Wǒ xǐhuān Zhōngguó, suǒyǐ wǒ yòu lái le.", "thai": "ฉันชอบประเทศจีน เลยกลับมาอีกครั้ง"},
            {"chinese": "这是我的学校录取通知书。", "pinyin": "Zhè shì wǒ de xuéxiào lùqǔ tōngzhīshū.", "thai": "นี่คือหนังสือตอบรับเข้าเรียนของฉัน"},
            {"chinese": "我已经买了保险。", "pinyin": "Wǒ yǐjīng mǎi le bǎoxiǎn.", "thai": "ฉันได้ทำประกันการเดินทางแล้ว"},
            {"chinese": "我有足够的资金。", "pinyin": "Wǒ yǒu zúgòu de zījīn.", "thai": "ฉันมีเงินเพียงพอสำหรับการเดินทาง"},
            {"chinese": "我会按时离境。", "pinyin": "Wǒ huì ànshí líjìng.", "thai": "ฉันจะออกนอกประเทศตามกำหนด"},
            {"chinese": "请问，还需要别的材料吗？", "pinyin": "Qǐngwèn, hái xūyào bié de cáiliào ma?", "thai": "ต้องใช้เอกสารอย่างอื่นอีกไหม"},
        ]
    },
    "internet": {
        "name": "อินเทอร์เน็ต & การติดต่อ",
        "icon": "📱",
        "sentences": [
            {"chinese": "我的手机没电了。", "pinyin": "Wǒ de shǒujī méi diàn le.", "thai": "โทรศัพท์ฉันแบตหมดแล้ว"},
            {"chinese": "可以借用一下充电器吗？", "pinyin": "Kěyǐ jièyòng yíxià chōngdiànqì ma?", "thai": "ขอยืมที่ชาร์จได้ไหม"},
            {"chinese": "这里有充电的地方吗？", "pinyin": "Zhèlǐ yǒu chōngdiàn de dìfang ma?", "thai": "ที่นี่มีจุดชาร์จไหม"},
            {"chinese": "我的手机没有信号。", "pinyin": "Wǒ de shǒujī méiyǒu xìnhào.", "thai": "มือถือฉันไม่มีสัญญาณ"},
            {"chinese": "这里有WiFi吗？", "pinyin": "Zhèlǐ yǒu WiFi ma?", "thai": "ที่นี่มี WiFi ไหม"},
            {"chinese": "WiFi密码是多少？", "pinyin": "WiFi mìmǎ shì duōshao?", "thai": "รหัส WiFi คืออะไร"},
            {"chinese": "我的手机连不上WiFi。", "pinyin": "Wǒ de shǒujī lián bú shàng WiFi.", "thai": "มือถือฉันเชื่อม WiFi ไม่ได้"},
            {"chinese": "网络断了，可以帮我看一下吗？", "pinyin": "Wǎngluò duàn le, kěyǐ bāng wǒ kàn yíxià ma?", "thai": "อินเทอร์เน็ตหลุด ช่วยดูให้หน่อยได้ไหม"},
            {"chinese": "这是我导游的电话，可以帮我联系一下吗？", "pinyin": "Zhè shì wǒ dǎoyóu de diànhuà, kěyǐ bāng wǒ liánxì yíxià ma?", "thai": "นี่คือเบอร์ไกด์ของฉัน ช่วยติดต่อให้หน่อยได้ไหม"},
            {"chinese": "这是我司机的电话，可以帮我联系一下吗？", "pinyin": "Zhè shì wǒ sījī de diànhuà, kěyǐ bāng wǒ liánxì yíxià ma?", "thai": "นี่คือเบอร์ของคนขับรถของฉัน ช่วยติดต่อเขาให้หน่อยได้ไหม"},
        ]
    },
    "others": {
        "name": "สถานการณ์อื่นๆ",
        "icon": "📌",
        "sentences": [
            {"chinese": "你可以帮我翻译一下吗？", "pinyin": "Nǐ kěyǐ bāng wǒ fānyì yíxià ma?", "thai": "คุณช่วยแปลให้หน่อยได้ไหม"},
            {"chinese": "这个是做什么用的？", "pinyin": "Zhège shì zuò shénme yòng de?", "thai": "อันนี้ใช้ทำอะไรเหรอ"},
            {"chinese": "可以帮我拍一张照片吗？", "pinyin": "Kěyǐ bāng wǒ pāi yì zhāng zhàopiàn ma?", "thai": "ช่วยถ่ายรูปให้หน่อยได้ไหม"},
            {"chinese": "请帮我们拍一张合照。", "pinyin": "Qǐng bāng wǒmen pāi yì zhāng hézhào.", "thai": "ช่วยถ่ายรูปหมู่ให้หน่อย"},
            {"chinese": "你可以告诉他，我现在的位置吗？", "pinyin": "Nǐ kěyǐ gàosu tā, wǒ xiànzài de wèizhì ma?", "thai": "คุณช่วยบอกเขาได้ไหมว่าตอนนี้ฉันอยู่ที่ไหน"},
            {"chinese": "我好像迷路了，可以帮我一下吗？", "pinyin": "Wǒ hǎoxiàng mílù le, kěyǐ bāng wǒ yíxià ma?", "thai": "ฉันเหมือนจะหลงทาง ช่วยฉันหน่อยได้ไหม"},
            {"chinese": "不好意思，我来晚了。", "pinyin": "Bù hǎoyìsi, wǒ lái wǎn le.", "thai": "ขอโทษที่ฉันมาสาย"},
            {"chinese": "需要排队吗？", "pinyin": "Xūyào páiduì ma?", "thai": "ต้องต่อคิวไหม"},
            {"chinese": "还要等多久？", "pinyin": "Hái yào děng duō jiǔ?", "thai": "ต้องรออีกนานไหม"},
            {"chinese": "可以帮我预约吗？", "pinyin": "Kěyǐ bāng wǒ yùyuē ma?", "thai": "ช่วยจองให้หน่อยได้ไหม"},
            {"chinese": "非常感谢你的帮助。", "pinyin": "Fēicháng gǎnxiè nǐ de bāngzhù.", "thai": "ขอบคุณมากสำหรับความช่วยเหลือของคุณ"},
        ]
    },
}


def seed_db():
    db = SessionLocal()
    try:
        existing_cats = db.query(Category).count()
        if existing_cats > 0:
            print("Database already has data, skipping seed.")
            return

        print("Seeding database...")
        sort_idx = 0
        for slug, cat_data in SENTENCE_DATA.items():
            cat = Category(name=cat_data["name"], icon=cat_data["icon"], sort_order=sort_idx)
            db.add(cat)
            db.flush()
            sort_idx += 1
            for i, s in enumerate(cat_data["sentences"]):
                db.add(Phrase(
                    category_id=cat.id,
                    chinese=s["chinese"],
                    pinyin=s["pinyin"],
                    thai=s["thai"],
                    sort_order=i,
                ))

        db.add(AdminUser(
            username=DEFAULT_USERNAME,
            password_hash=hash_password(DEFAULT_PASSWORD),
        ))
        db.commit()
        print(f"Seeded: {sort_idx} categories with phrases, admin user created.")
    finally:
        db.close()


async def seed_audio():
    db = SessionLocal()
    try:
        phrases = db.query(Phrase).all()
        if not phrases:
            return
        for p in phrases:
            if p.audio_file and os.path.isfile(os.path.join(AUDIO_DIR, p.audio_file)):
                continue
            filename = f"phrase_{p.id}.mp3"
            filepath = os.path.join(AUDIO_DIR, filename)
            try:
                communicate = edge_tts.Communicate(p.chinese, VOICE, rate=RATE, pitch=PITCH)
                await communicate.save(filepath)
                p.audio_file = filename
                try:
                    print(f"  Generated: {filename}")
                except UnicodeEncodeError:
                    print(f"  Generated: {filename} [{p.id}]")
            except Exception as e:
                try:
                    print(f"  Failed [{p.id}]: {e}")
                except UnicodeEncodeError:
                    print(f"  Failed phrase {p.id}: {e}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
    print("\nGenerating audio files (this may take a while)...")
    asyncio.run(seed_audio())
    print("\nDone! Run: cd backend && python -m uvicorn app.main:app --reload")
