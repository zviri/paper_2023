from enum import Enum
from tkinter import INSERT


class CreditorCategory(Enum):
    OTHER = "other"
    BANK = "bank"
    NONBANKING = "nonbanking"
    GOVERNMENT = "government"
    INSURANCE = "insurance"
    UTILITIES = "utilities"


CREDITOR_2_CATEGORY = {
    "27242617": CreditorCategory.NONBANKING,  # bohemia faktoring
    "4886674": CreditorCategory.OTHER,  # Jicha
    "41197518": CreditorCategory.GOVERNMENT,  # VZP
    "72043202": CreditorCategory.OTHER,  # Kubis
    "49720821": CreditorCategory.OTHER,  # Podkonicky
    "71238573": CreditorCategory.OTHER,  # Mika
    "60531355": CreditorCategory.OTHER,  # Kocian
    "6963": CreditorCategory.GOVERNMENT,  # CSSZ
    "60351268": CreditorCategory.OTHER,  # Smekal
    "61860069": CreditorCategory.NONBANKING,  # Profireal
    "47116617": CreditorCategory.INSURANCE,  # Kooperativa
    "27232433": CreditorCategory.UTILITIES,  # CEZ
    "64949681": CreditorCategory.UTILITIES,  # t-mobile
    "66253799": CreditorCategory.OTHER,  # Mares
    "26978636": CreditorCategory.NONBANKING,  # Home Creditr
    "27221971": CreditorCategory.NONBANKING,  # Intrum
    "45272956": CreditorCategory.INSURANCE,  # Generali
    "3372537": CreditorCategory.OTHER,  # Havlice
    "72080043": CreditorCategory.GOVERNMENT,  # FU
    "29027241": CreditorCategory.NONBANKING,  # CP Inkaso
    "60193336": CreditorCategory.UTILITIES,  # O2
    "45244782": CreditorCategory.BANK,  # Ceska sporitelna
    "25621351": CreditorCategory.NONBANKING,  # Probident
    "24316717": CreditorCategory.NONBANKING,  # IFIS
    "70099618": CreditorCategory.NONBANKING,  # Ceska kancelar pojistitelu
    "63998530": CreditorCategory.INSURANCE,  #  Ceska podn. pojistovna
    "24785199": CreditorCategory.NONBANKING,  # KRUK
    "71329277": CreditorCategory.OTHER,  # Prosek
    "47672234": CreditorCategory.INSURANCE,  # Ceska prumyslova zdravotni pojistovna
    "66253080": CreditorCategory.OTHER,  # Koncz
    "68404441": CreditorCategory.OTHER,  # Svecova
    "49903209": CreditorCategory.UTILITIES,  # innogy
    "27646751": CreditorCategory.NONBANKING,  # Cesky inkasni kapital
    "66248574": CreditorCategory.OTHER,  # tunkl
    "25788001": CreditorCategory.UTILITIES,  # vodafone
    "1385437": CreditorCategory.OTHER,  # sobiskova
    "62096052": CreditorCategory.OTHER,  # homola
    "3121216": CreditorCategory.OTHER,  # homola
    "1350": CreditorCategory.BANK,  # CSOB
    "4455835": CreditorCategory.NONBANKING,  # Fair Credit
    "24243744": CreditorCategory.NONBANKING,  # EC Financial services
    "66216877": CreditorCategory.OTHER,  # Ivanko
    "25672720": CreditorCategory.BANK,  # Moneta
    "10851828": CreditorCategory.NONBANKING,  # CFIG
    "66225108": CreditorCategory.OTHER,  # Peroutka
    "47114975": CreditorCategory.GOVERNMENT,  # vojenska zp
    "47114304": CreditorCategory.GOVERNMENT,  # zdravotni poj. min. vnitra
    "72065699": CreditorCategory.OTHER,  # Zwiefelhofer
    "27383": CreditorCategory.UTILITIES,  # Česká Televize
    "2975122": CreditorCategory.OTHER,  #  Koutnikova
    "66243505": CreditorCategory.OTHER,  # Cernoskova
    "72077433": CreditorCategory.OTHER,  # Svoboda
    "2112621": CreditorCategory.NONBANKING,  # Cool Credit
    "29413575": CreditorCategory.NONBANKING,  # Zaplo Finance
    "70931194": CreditorCategory.OTHER,  # Zitka
    "66201501": CreditorCategory.OTHER,  # Luhan
    "4191536": CreditorCategory.NONBANKING,  # B2 Kapital
    "24849707": CreditorCategory.NONBANKING,  # Creamfinance
    "75066874": CreditorCategory.OTHER,  # Jaros
    "26078201": CreditorCategory.UTILITIES,  # E.ON
    "7595182": CreditorCategory.OTHER,  # Suchánek
    "66250391": CreditorCategory.OTHER,  # Flajšhansová
    "29045371": CreditorCategory.BANK,  # Airbank
    "75128446": CreditorCategory.OTHER,  # Fendrych
    "49240901": CreditorCategory.BANK,  # Raiffeisenbank
    "45317054": CreditorCategory.BANK,  # Komernci banka
    "72547251": CreditorCategory.OTHER,  # Valentova
    "66241146": CreditorCategory.OTHER,  # Bednář
    "29216842": CreditorCategory.NONBANKING,  # Justrinon
    "43876439": CreditorCategory.OTHER,  # Kosina
    "5561302": CreditorCategory.NONBANKING,  # CreditPortal
    "27179907": CreditorCategory.NONBANKING,  # Cofidis
    "67967591": CreditorCategory.OTHER,  # Micka
    "8615870": CreditorCategory.NONBANKING,  # Torsion invest
    "40846415": CreditorCategory.OTHER,  # Mgr. Petr Polanský
    "28939395": CreditorCategory.NONBANKING,  # Credit Field
    "24305511": CreditorCategory.NONBANKING,  # Flexi Fin
    "26440334": CreditorCategory.NONBANKING,  # Help Financial
    "25858246": CreditorCategory.NONBANKING,  # JET Money
    "29138680": CreditorCategory.NONBANKING,  # CFIG
    "1411641": CreditorCategory.NONBANKING,  # EOS
    "bnpparibaspersonalfinance": CreditorCategory.NONBANKING,  # BNP Paribas Personal Finance
    "5886": CreditorCategory.UTILITIES,  # Dopravní podnik hl.m. Prahy, akciová společnost
    "ab4bv": CreditorCategory.NONBANKING,  # AB 4 B.V., soukromá společnost s ručením omezeným
    "26764652": CreditorCategory.NONBANKING,  # ESSOX s. r. o.
    "28218761": CreditorCategory.NONBANKING,  # I-Xon a. s.
    "1381300": CreditorCategory.NONBANKING,  # OPR-Finance s.r.o.
    "63487063": CreditorCategory.NONBANKING,  # O.K.V. Leasing, s.r.o.
    "47114321": CreditorCategory.INSURANCE,  # Oborová zdravotní pojišťovna zam. bank, pojišťoven a stavebnictví
    "845451": CreditorCategory.UTILITIES,  # Statutární město Ostrava, městský obvod Slezská Ostrava
    "71214011": CreditorCategory.GOVERNMENT,  # Celní úřad Brno
    "4488237": CreditorCategory.NONBANKING,  # Orange finance s.r.o.
    "3299309": CreditorCategory.NONBANKING,  # Emma´s credit s.r.o.
    "47115971": CreditorCategory.INSURANCE,  # Allianz pojišťovna, a.s.
    "ferratumbankplc": CreditorCategory.NONBANKING,  # Ferratum Bank p.l.c
    "26865297": CreditorCategory.NONBANKING,  # SMART Capital, a.s.
    "49241397": CreditorCategory.BANK,  # ČSOB Stavební spořitelna, a.s.
    "25262823": CreditorCategory.NONBANKING,  # OSPEN s.r.o.
    "bnpparibaspersonalfinancesa": CreditorCategory.NONBANKING,  # BNP PARIBAS PERSONAL FINANCE SA
    "27148084": CreditorCategory.NONBANKING,  # TOMMY STACHI s.r.o.
    "47116102": CreditorCategory.BANK,  # Equa bank a.s.
    "24247936": CreditorCategory.NONBANKING,  # Creditstar Czech s.r.o.
    "26425033": CreditorCategory.NONBANKING,  # Matco, s. r. o.
    "44992785": CreditorCategory.UTILITIES,  # Statutární město Brno, Magistrát města Brna - Odbor životního prostředí
    "25117483": CreditorCategory.NONBANKING,  # EOS KSI Česká republika, s.r.o.
    "61974757": CreditorCategory.UTILITIES,  # Dopravní podnik Ostrava, a.s.
    "24213276": CreditorCategory.NONBANKING,  # Czechoslovak Capital Partners a. s.
    "26289636": CreditorCategory.NONBANKING,  # WLG Invest a.s.
    "sprinterstellarltd": CreditorCategory.NONBANKING,  # SPRINTER STELLAR LTD.
    "61859869": CreditorCategory.INSURANCE,  # Pojišťovna Patricie a.s.
    "25073958": CreditorCategory.INSURANCE,  # Direct pojišťovna, a.s.
    "serraghisloanmanagementltd": CreditorCategory.NONBANKING,  # Serraghis Loan Management Ltd
    "60197609": CreditorCategory.BANK,  # Stavební spořitelna České spořitelny, a.s.
    "28210956": CreditorCategory.NONBANKING,  # Barlog Capital a.s.
    "9022902": CreditorCategory.NONBANKING,  # A.P.C. Four s.r.o.
    "25220683": CreditorCategory.UTILITIES,  # Plzeňské městské dopravní podniky, a.s.
    "24720275": CreditorCategory.NONBANKING,  # Via SMS s. r. o.
    "60197501": CreditorCategory.INSURANCE,  # Slavia pojišťovna a.s.
    "27944514": CreditorCategory.NONBANKING,  # ABEWY s.r.o.
    "9129219": CreditorCategory.NONBANKING,  # TARAKAN invest, s. r. o.
    "47673036": CreditorCategory.INSURANCE,  # RBP, zdravotní pojišťovna
    "25508881": CreditorCategory.UTILITIES,  # Dopravní podnik města Brno, a.s.
    "25120514": CreditorCategory.NONBANKING,  # Euro Benefit a. s.
    "24830801": CreditorCategory.NONBANKING,  # CASPER UNION s.r.o.
    "1497316": CreditorCategory.NONBANKING,  # FINDIGO služby s.r.o.
    "27822117": CreditorCategory.NONBANKING,  # Tessile ditta a.s.
    "3570967": CreditorCategory.NONBANKING,  # Benxy s.r.o.
    "1615165": CreditorCategory.NONBANKING,  # Twisto payments a.s.
    "81531": CreditorCategory.UTILITIES,  # Statutární město Ústí nad Labem
    "27525210": CreditorCategory.NONBANKING,  # PRONTO CREDIT s.r.o.
    "49241257": CreditorCategory.BANK,  # Raiffeisen stavební spořitelna a. s.
    "falconcreekinvestmentsltd": CreditorCategory.NONBANKING,  # FALCONCREEK INVESTMENTS LTD
    "66254949": CreditorCategory.OTHER,  # Exekutorský úřad Děčín
    "72496991": CreditorCategory.UTILITIES,  # Česká republika - Úřad práce České republiky
    "27386732": CreditorCategory.UTILITIES,  # BOHEMIA ENERGY entity s.r.o.
    "60193913": CreditorCategory.UTILITIES,  # Pražská energetika, a.s.
    "27574661": CreditorCategory.NONBANKING,  # COREFIN s.r.o.
    "63998980": CreditorCategory.BANK,  # ČSOB Leasing, a.s.
    "25864106": CreditorCategory.NONBANKING,  # Český Triangl, a.s.
    "25267": CreditorCategory.UTILITIES,  # Okresní soud v Ostravě
    "27295567": CreditorCategory.UTILITIES,  # GasNet, s.r.o.
    "25062": CreditorCategory.UTILITIES,  # Česká republika - Městský soud v Brně
    "24823546": CreditorCategory.NONBANKING,  # Simfina a.s.
    "65402367": CreditorCategory.OTHER,  # JUDr. Ing. Petr Kučera
    "28329082": CreditorCategory.NONBANKING,  # Tessile ditta services a.s.
    "25013891": CreditorCategory.UTILITIES,  # Dopravní podnik města Ústí nad Labem a.s.
    "4823541": CreditorCategory.NONBANKING,  # CreditKasa s.r.o.
    "49240480": CreditorCategory.INSURANCE,  # UNIQA pojišťovna
    "5090792": CreditorCategory.NONBANKING,  # Go Invex Finance s.r.o.
    "4424115": CreditorCategory.NONBANKING,  # Fair Credit International, SE
}
