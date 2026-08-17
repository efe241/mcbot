import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\EFE\Desktop\mcbot\data"
SERVICES_FILE = os.path.join(DATA_DIR, "services.json")
STOCKS_FILE = os.path.join(DATA_DIR, "stocks.json")

raw_text = """kurosaki0422:Mavuika422
acacius95:Sabahfaez!211
MRJG17:Jesusgeo17!
mjrshark:Thegame418
hamdacom:ehfdkdhk0
aiaqii:Steam1312.
kpp737:sjrhth!@3
hoontae02:rlaxogns02!
mikemoran19:Mm1312730.
hyzaarils.09@gmail.com:Shah3632rizal_
tema6344:3476@Daniel
Marty2772:V!h@.n.MR6hXr5y
terrobum:Wkfgoqhwk7*9
pkkk127:wlsmldi3
mugiwawra69:W3schools69
cakemoon_:Cake0812
ddeoyo1986:!qwe1169
baozi1175:Nominshipper23.
Joahanmtz2112:Joahan3001
tarquinius4:Ikennikki2505
juben3176ab:chltjdgns3176!@
kensas73:dkWkdsk22^^
FERNANFTP17:Fernanjr17
yintan0516:weihuan16@
babayagam2:MarjanchoMatevski1993
fpolice1:4658qwER
showzm:Ssoya1025
necropia1:tkarnrwl11!
Dickson1688:++SHE9xXB+B?HM&
brandonzhang69:hellobros69@254
haesu10:sgkagotn10!
pca031:phuahchernaun2004
chandanghost:f2pghost
adam20042015:@Aqwerty7890!@
zibi:NVDsgp01--
mundomty:ryuuzaki12
oscarcolima5@gmail.com:Chencho10
rshadow111:123QWEasd!!setghw4ryw
mdmdmd74:Jk141313
asdasdfasd7:91d428aa3cf
amongcrow0313:ac#20100313
ctr_cool:dragonixctr
songjw6890:asd1490610
Drzdexter:Dexter#123#
jokerjoker0102:tnguddl1002!
Luffyzoro890:sharul1234
bboena:Stupid391996!
kk543101:k2734676
kryptnosis:Lord1047
steam:Cig'42'6ft_r
eseense:steam78nine51
Ldh723:joun2002@@
btoctoc3:Luffy+456
choreeman:materesa2026chore
redsun1025@naver.com:XODNR1024`
funnypencil_02:ColaJoas@2007
buttbuster10:Wesselvd1406
ToCaToi:vtd42Steam!
kerroro1:050570aA!
lee9838:Lee750802#
prabathdb25@gmail.com:YTpancha2005
qarriz:159362hoi
N5VQ7:tnwjd945
robert19708:DragonQueen27!
widelens:Monk/123
AssasinMansion1:Hakim162004
1009kyung:RUDDLDJAAK69
Hss_Jeffrey:ElPapu$Lince41
zzziko390@gmail.com:"@$XmG5%H:PvE-M
misa1172:Terraria56
pagaez:1397003y!
Beelzex_0111:beelzex123
applinn:Chr1stan@114
rehteid0210:Cmendoza09
Zeikko1314:662607004gael.com
Only1Bryan2:05129460@Dave
lolikong63:loong5225
royarellano:anarchyftw69
syb20072:SYB4531452007
n1chqlas:02108130937N!ck
ndlu:intelCore!7
z647472:Zasdtkdrms1234
ro0oal:chenhui3833
mysticmythgaymer:Mysticsteam
negroslayer123:Lmgpvppro12
heon_lee:stanlee1331!
prdyghyz123:diego234567Zx
neverdoubtedm3:L3gobrick
markisdtdehh:Ssmartpin12@#_
Y3su41:Yesu@12@34
steamvaleverga:Ivonne1989
javi200920:JaSeJi2026
hbkk4122:rlT@tp10
Cam50505:2005Chelsea
jackczf:Jackychai22
braydux22:Tricky2883#
instag5:filantropia12
irham950730:SyedIrham30
since5am:9minubaduba"""

clean_lines = [l.strip() for l in raw_text.strip().split("\n") if l.strip() and ":" in l]
print(f"Toplam temizlenen Steam VIP hesabı: {len(clean_lines)}")

# Update services.json
if os.path.exists(SERVICES_FILE):
    with open(SERVICES_FILE, "r", encoding="utf-8") as f:
        services = json.load(f)
    
    exists = False
    for s in services:
        if s.get("id") == "steam_vip":
            s["name"] = "Steam Oyunlu VIP"
            s["category"] = "vip"
            s["emoji"] = "🎮"
            s["description"] = "VIP Özel Oyunlu Steam Hesapları"
            s["is_unlimited"] = False
            exists = True
            break
    if not exists:
        services.append({
            "id": "steam_vip",
            "name": "Steam Oyunlu VIP",
            "category": "vip",
            "emoji": "🎮",
            "description": "VIP Özel Oyunlu Steam Hesapları",
            "is_unlimited": False
        })

    with open(SERVICES_FILE, "w", encoding="utf-8") as f:
        json.dump(services, f, ensure_ascii=False, indent=2)
    print("OK: services.json güncellendi (steam_vip eklendi)")

# Update stocks.json
if os.path.exists(STOCKS_FILE):
    with open(STOCKS_FILE, "r", encoding="utf-8") as f:
        stocks = json.load(f)
    
    stocks.setdefault("steam_vip", []).extend(clean_lines)

    with open(STOCKS_FILE, "w", encoding="utf-8") as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)
    print(f"OK: stocks.json güncellendi! Güncel steam_vip stok sayısı: {len(stocks['steam_vip'])}")
