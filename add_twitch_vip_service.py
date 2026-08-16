import json
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r"C:\Users\EFE\Desktop\mcbot\data"
SERVICES_FILE = os.path.join(DATA_DIR, "services.json")
STOCKS_FILE = os.path.join(DATA_DIR, "stocks.json")

twitch_cookie_text = """Username: kingspace_
Followers: 14

.twitch.tv\tTRUE\t/\tTRUE\t1781510597\texperiment_overrides\t{%22experiments%22:{}%2C%22disabled%22:[]}
.twitch.tv\tTRUE\t/\tTRUE\t1778746258\tapi_token\t9349a20dd6e452e982bb20913b3bb0e5
.twitch.tv\tTRUE\t/\tTRUE\t1747901458\tbits_sudo\teyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NjQ3Mjk2NTYiLCJhdWQiOlsic3VkbyIsImJpdHMiXSwiZXhwIjoxNzQ3OTAxNDU3LCJpYXQiOjE3NDcyOTY2NTd9.T4STDJ-uxVQx10NXP7dw0eP5SJw-OoKaTEz1sJEiaHfcbjr81u4C5Vtkf0URL5HVnvfHQGrBQEpj_ioR3-qypQ==
passport.twitch.tv\tFALSE\t/\tFALSE\t1747383058\tga__12_abel\t03eheANENpWcjhtnroGrh4isMiO41SKYZXsg5bKMlNNnIk0Do1pARPRQOhh5MOYuJClHxV0UE1n0lMA6Apt0YywLbBvtM3easRLzjCPO1s401LFO9yiFCrPIyurAiF9NaGgBYBVH5pZmYF61QrWCEy3Sv40eRhOXbMiDrfqsWA
passport.twitch.tv\tFALSE\t/\tTRUE\t1747383058\tga__12_abel-ssn\t03eheANENpWcjhtnroGrh4isMiO41SKYZXsg5bKMlNNnIk0Do1pARPRQOhh5MOYuJClHxV0UE1n0lMA6Apt0YywLbBvtM3easRLzjCPO1s401LFO9yiFCrPIyurAiF9NaGgBYBVH5pZmYF61QrWCEy3Sv40eRhOXbMiDrfqsWA
.twitch.tv\tTRUE\t/\tFALSE\t1778746258\tlast_login\t2025-05-15T08:10:57Z
.twitch.tv\tTRUE\t/\tFALSE\t1778746258\tname\tkingspace_
.twitch.tv\tTRUE\t/\tTRUE\t1778746258\tpersistent\t664729656%3A%3Asohbe2jcqvqy4mqzl6jsp8834psniq
.twitch.tv\tTRUE\t/\tTRUE\t0\tspare_key\teyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL3Bhc3Nwb3J0LnR3aXRjaC50diIsInN1YiI6IltcIjY2NDcyOTY1NlwiXSIsImF1ZCI6ImJydXRlLWZvcmNlLXByb3RlY3Rpb24iLCJleHAiOjE3NjI4NDg2NTcsImlhdCI6MTc0NzI5NjY1Nywibm9uY2UiOiJycXpkT1VxS3lHNE40czY1MjRmS0Z3QVZRMVZYMGNmRXhrU3kybUdVSEVRPSJ9.IEnYe1T2gIZ_NUzLi7KcomE8z2n2oSfPzs9HNWjgR9VBw8v7Cuhv6Un9hrYcKU37fSf0TlSlDoyq6DFm_RF2hg%3D%3D
gql.twitch.tv\tFALSE\t/\tFALSE\t1747396577\tKP_UIDZ_1\t02HWcOQKljiKEVt7awmRHp80MFK0b4rEDWEvwXfE8shnIocZmfIeZRpyFHHlFzgtP6xRlcmFECxJDlO8T8MD6e4NXeSfAPgQmY0QMiBwe9cGqyIF2hRLJ2jfhYNCBjmSMOpZO8WAD4pKCm9TPj0i3aOu4sr3TRZcJeAiKDrjGv
gql.twitch.tv\tFALSE\t/\tTRUE\t1747396577\tKP_UIDZ_1-ssn\t02HWcOQKljiKEVt7awmRHp80MFK0b4rEDWEvwXfE8shnIocZmfIeZRpyFHHlFzgtP6xRlcmFECxJDlO8T8MD6e4NXeSfAPgQmY0QMiBwe9cGqyIF2hRLJ2jfhYNCBjmSMOpZO8WAD4pKCm9TPj0i3aOu4sr3TRZcJeAiKDrjGv
.twitch.tv\tTRUE\t/\tTRUE\t1781524578\tauth-token\t91ycw9qwsshrzbf2v61eums046qf5d
passport.twitch.tv\tFALSE\t/\tFALSE\t1747396577\tga__15_abel\t02PCa2vghUZOC0bnBH06UKZ2dkQ3OZCC5QUeL83cmx2I3gCQDSX4z5HUmbU2BhCPJoTpPA0atSzLFaiQYp9CG52DOhUGDcPM12IfOkvEB22z98wIHL0iBue1LyK4Knp65Y7OrPORp40nXdtjdPbfflZGe6ODA5z2Ag1OqbZ7JL
passport.twitch.tv\tFALSE\t/\tTRUE\t1747396577\tga__15_abel-ssn\t02PCa2vghUZOC0bnBH06UKZ2dkQ3OZCC5QUeL83cmx2I3gCQDSX4z5HUmbU2BhCPJoTpPA0atSzLFaiQYp9CG52DOhUGDcPM12IfOkvEB22z98wIHL0iBue1LyK4Knp65Y7OrPORp40nXdtjdPbfflZGe6ODA5z2Ag1OqbZ7JL
.twitch.tv\tTRUE\t/\tTRUE\t1781524578\tlogin\tkingspace_
.twitch.tv\tTRUE\t/\tTRUE\t1781524578\ttwilight-user\t{%22authToken%22:%2291ycw9qwsshrzbf2v61eums046qf5d%22%2C%22displayName%22:%22kingspace_%22%2C%22id%22:%22664729656%22%2C%22login%22:%22kingspace_%22%2C%22roles%22:{%22isStaff%22:false}%2C%22version%22:2}
.twitch.tv\tTRUE\t/\tTRUE\t0\tserver_session_id\t825385c20e98432699dfa02a6cfbfd87
.twitch.tv\tTRUE\t/\tFALSE\t1781007469\ttwitch.lohp.countryCode\tAU
.twitch.tv\tTRUE\t/\tTRUE\t1781525869\tunique_id\tl9pHvIVxj24a5jqjDiHuhY2XzMawMnh5
.twitch.tv\tTRUE\t/\tTRUE\t1781525869\tunique_id_durable\tl9pHvIVxj24a5jqjDiHuhY2XzMawMnh5
id.twitch.tv\tFALSE\t/oauth2\tFALSE\t0\tid_csrf\tE1Be7kqDGaEivj3hwZ9qCML5PJeiUeMF3bfWmjq+Bfk="""

# Update services.json
if os.path.exists(SERVICES_FILE):
    try:
        with open(SERVICES_FILE, "r", encoding="utf-8") as f:
            services = json.load(f)
        
        exists = False
        for s in services:
            if s.get("id") == "twitch_vip":
                s["name"] = "Twitch Cookie VIP (Sınırsız)"
                s["category"] = "vip"
                s["emoji"] = "🎮"
                s["description"] = "VIP Özel Twitch Cookie Hesabı (Sınırsız)"
                s["is_unlimited"] = True
                exists = True
                break
        if not exists:
            services.append({
                "id": "twitch_vip",
                "name": "Twitch Cookie VIP (Sınırsız)",
                "category": "vip",
                "emoji": "🎮",
                "description": "VIP Özel Twitch Cookie Hesabı (Sınırsız)",
                "is_unlimited": True
            })

        with open(SERVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(services, f, ensure_ascii=False, indent=2)
        print("OK: services.json güncellendi (twitch_vip eklendi)")
    except Exception as e:
        print(f"Hata services.json: {e}")

# Update stocks.json
if os.path.exists(STOCKS_FILE):
    try:
        with open(STOCKS_FILE, "r", encoding="utf-8") as f:
            stocks = json.load(f)
        
        stocks["twitch_vip"] = [twitch_cookie_text]

        with open(STOCKS_FILE, "w", encoding="utf-8") as f:
            json.dump(stocks, f, ensure_ascii=False, indent=2)
        print("OK: stocks.json güncellendi (twitch_vip eklendi)")
    except Exception as e:
        print(f"Hata stocks.json: {e}")
