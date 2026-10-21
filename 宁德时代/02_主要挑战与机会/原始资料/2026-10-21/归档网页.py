"""下载本次研究采用的官方网页，记录URL、访问时间、摘要哈希及下载失败。"""
import concurrent.futures, datetime, hashlib, json, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCES=[
 ('P1_消费税调整','2026-07-17','https://szs.mof.gov.cn/zhengcefabu/202607/t20260717_3993743.htm'),
 ('P2_出口退税调整','2026-01-09','https://szs.mof.gov.cn/zhengcefabu/202601/t20260109_3981637.htm'),
 ('P3_消费税问答','2026-08-27','https://www.chinatax.gov.cn/chinatax/c102414/c5252006/content.html'),
 ('P4_美国PFE指引','2026-03-09公报','https://www.irs.gov/irb/2026-11_IRB'),
 ('P5_欧盟电池护照指引','2026-08-21','https://single-market-economy.ec.europa.eu/news/guidance-support-preparations-digital-batteries-passport-2026-08-21_en'),
 ('P6_欧盟电池护照FAQ','访问于2026-10-21','https://single-market-economy.ec.europa.eu/single-market/digital-product-passport/eu-digital-product-passport-faq-batteries_en'),
 ('M1_SNE非中国市场','2026-10-07','https://sneresearch.com/kr/insight/release_view/750/page/372?s_cat=%7C&s_keyword='),
 ('C1_钠电储能发布','2026-06-22','https://www.catl.com/en/news/6861.html'),
 ('C2_Alfen钠电合作','2026-07-16','https://www.catl.com/en/news/6900.html'),
 ('C3_赛力斯合作','2026-10-10','https://www.catl.com/en/news/7014.html'),
 ('G1_匈牙利政府许可说明','2026-08-25','https://kormanyhivatalok.hu/hirek/vizsgalat-es-elutasitott-engedely-catl-nel')
]

def download(item):
    name,date,url=item
    record={'id':name,'published':date,'url':url,'accessed':'2026-10-21','file':name+'.html'}
    dest=ROOT/record['file']
    try:
        if dest.exists():
            data=dest.read_bytes()
        else:
            request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(request,timeout=30) as response:data=response.read()
            dest.write_bytes(data)
        record.update(status='downloaded',bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
    except Exception as exc:record.update(status='failed',error=str(exc))
    return record

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    result=list(pool.map(download,SOURCES))
(ROOT/'来源归档记录.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
for r in result:print(r['id'],r['status'],r.get('bytes',r.get('error')))
