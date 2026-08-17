import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\EFE\Desktop\mcbot\data"
STOCKS_FILE = os.path.join(DATA_DIR, "stocks.json")

raw_text = """Choi.sam95@gmail.com:Youmadbruh126!
azefade@gmail.com:0129248764
asaalasaal120@hotmail.com:EEff1980
rossymtzz01@gmail.com:Rossymtz_76
oumous.2112@gmail.com:oumous@2112
01032652673:329henku$$
faizuladha19@gmail.com:EjuL1203
rocks10178@gmail.com:India@2022
hisinger@naver.com:qkrwldud230723*
08102844603:Victor2005
mrgengarxd@gmail.com:ezmeralda
01033175481:whtjdals5441
kimyn81@naver.com:1q2w3e4r
Lauraceciliagonzales@gmail.com:violeta11
gopelusa9@gmail.com:Badbunny.25
nanpuhaha@gmail.com:nfseo9328%20
01091058486:0816rudwns^^
luisantoniosanchez01@live.com:metallica222
pochoteca@gmail.com:maol6491
abdellah.hmimsa@gmail.com:poepzooi2023
ginalouisewilliams@yahoo.co.uk:geegee1978
Jairramos220@gmail.com:Yayoram
dustflix@gmail.com:19213204
3/:sharonnwachukwu00@gmail.com:amara.N2006
vonk9760@gmail.com:VonkVonk
dbgusal12@naver.com:hyunmi89+
ukonuzoidx@gmail.com:TypemeChee07#
ikieex060408@gmail.com:EMELIA5458
js.chingun@yahoo.com:Netflixsuka321
ayme_gb@hotmail.com:aymeglez86
badaouimon05@icloud.com:Mb11052005@@
xcizzy8@gmail.com:kyoungswage
renward11@hotmail.com:contraloria
Khassif0006@gmail.com:Adam2024!
joonsun0202@naver.com:aa456123
sanderbuist@gmail.com:netflixen2
paulakooistra@gmail.com:Marley06
valentinaduenasbenitez@gmail.com:@MichiCa61
morenikejideborah905@gmail.com:more1234
natalia.sevostjanov97@gmail.com:kuik1chokolate2
ahmachjoseph@gmail.com:YousseF2008
Carmonish.nyd@gmail.com:Calet0295
gagkumok@gmail.com:n82ejr01
oscartrejo32@yahoo.com:771997
Kim1013merlin@naver.com:my1004@andy
james-gamer@hotmail.com:Panadol123?
bar903@usbc.be:098712
dlalsgh2233@nate.com:alshal22
dark1910@live.com.mx:eliud160997
babalolatrust@gmail.com:D875NmRds!!niyc
6Smol/:01112979709:Idlan008
jadaitbrik@gmail.com:09876543
yddnsang@naver.com:yy971027!
saikhaek89@gmail.com:kiop12340@@
Imkeverstappen@gmail.com:Groenethee1726
f3hr.1007@gmail.com:1007
S88134648@gmail.com:Tuuguu321
bodeene@outlook.com:FlixNet1976
nicolas.marquez.urbano@gmail.com:69021079maun
ko_yunzhen@hotmail.com:catherineko0307
serralexander83@gmail.com:Voiture32
salma.kasmi@hotmail.fr:25120000
joseh.clement@laposte.net:Manois8585//AA
uwakwecynthia249@gmail.com:@Cynthia1995
al.uribe06@gmail.com:Petaldo06
nouhailaelbadi555@gmail.com:552955
brahim.bouchra@mailo.com:Bouchramavie12_
gus.malcoro.16@gmail.com:Latesla170318
spiro.migos@gmail.com:Razorstaket67
ramdebatezo@gmail.com:zapato123
dr_lalo_landa@hotmail.com:cesaritopuntocom
yamchaterricola@gmail.com:clarisa21
greyesty@outlook.com:ww332211
rondorlas@hotmail.com:Oktober1958
l.a.v@live.nl:j7adkwxg
tanggu427@naver.com:rkdxogns1@
roelofsjeannet@gmail.com:Kuuper17
asd1313@daum.net:Asd131313!
zackytech5@gmail.com:Netflixameer123
dhanujahimansana3@gmail.com:82540497
Sanaamouslim2@gmail.com:sanaa1971
naimasandele@gmail.com:#1M0m4ever
insertyours@naver.com:2930dnjs
daojiong77@gmail.com:shi0818
pym1st@gmail.com:p@53479026
eroselvert@gmail.com:4815162342
namwimatengu@gmail.com:Ceddy@27
agneguobyte@gmail.com:Troleibusiukas9
fadzliyatul@gmail.com:li060673
juliofriscione@gmail.com:03062001mebhor44
hanbi1516@gmail.com:01022447516
ouimayssoune@gmail.com:bl00dyhe11!
7411107662_rbk29@hotmail.com:alexa29
chloe.valy@gmail.com:Libres2349!
jaziimughal5@gmail.com:q+VG/U3iuuPZg)3
velazquezvargasr@yahoo.com:21682168
newiten@naver.com:rui0331@
as15968@gmail.com:tum1559!
wclark@feral.kiwi:fuckface762"""

clean_lines = []
for line in raw_text.strip().split("\n"):
    line = line.strip()
    if not line:
        continue
    # Strip prefixes like 3/: or 6Smol/:
    if "/:" in line:
        line = line.split("/:", 1)[1]
    if ":" in line:
        clean_lines.append(line)

print(f"Toplam temizlenen Netflix hesabı: {len(clean_lines)}")

free_batch = clean_lines[:25]
vip_batch = clean_lines[25:]

print(f"Free'ye eklenecek: {len(free_batch)}")
print(f"VIP'ye eklenecek: {len(vip_batch)}")

if os.path.exists(STOCKS_FILE):
    with open(STOCKS_FILE, "r", encoding="utf-8") as f:
        stocks = json.load(f)
    
    stocks.setdefault("netflix_free", []).extend(free_batch)
    stocks.setdefault("netflix_vip", []).extend(vip_batch)

    with open(STOCKS_FILE, "w", encoding="utf-8") as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)

    print(f"OK: stocks.json güncellendi!")
    print(f"Güncel netflix_free toplam stok: {len(stocks['netflix_free'])}")
    print(f"Güncel netflix_vip toplam stok: {len(stocks['netflix_vip'])}")
