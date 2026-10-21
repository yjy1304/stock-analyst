"""读取原始底表，生成季度测算、Markdown底表和可复算SVG图表。标准库即可执行。"""
import json, math, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / '原始数据/财务底表.json').read_text())
A = D['annual']; C = D['cumulative']
Q = {r['period']: dict(r) for r in D['quarters_direct']}
Q['2026Q2'] = {'period':'2026Q2','source':'H26累计减Q126；全部流量为测算值'}
for k in ['rev','np','core','cfo']:
    Q['2026Q2'][k] = C['2026H1'][k]-Q['2026Q1'][k]
for y in [2024,2025,2026]:
    if y == 2024:
        Q['2024Q3']['cost'] = C['2024Q3']['cost']-C['2024H1']['cost']
        Q['2024Q4']['cost'] = A[1]['cost']-C['2024Q3']['cost']
        continue
    Q[f'{y}Q1']['cost']=C[f'{y}Q1']['cost']
    Q[f'{y}Q2']['cost']=C[f'{y}H1']['cost']-C[f'{y}Q1']['cost']
    Q[f'{y}Q3']['cost']=C[f'{y}Q3']['cost']-C[f'{y}H1']['cost']
    if y == 2025:
        Q['2025Q4']['cost']=A[2]['cost']-C['2025Q3']['cost']
Q['2026Q3']['cfo']=C['2026Q3']['cfo']-C['2026H1']['cfo']

def enrich(r):
    r['nm']=r['np']/r['rev']*100
    r['gm']=(1-r['cost']/r['rev'])*100 if 'cost' in r else None
    r['cash_profit']=r.get('cfo',0)/r['np']
for r in A:
    enrich(r); r['debt_ratio']=r['liabilities']/r['assets']*100
    r['rd_ratio']=r['rd']/r['rev']*100
for p,r in sorted(Q.items()):
    enrich(r); y,n=int(p[:4]),int(p[-1]); prev=f'{y}Q{n-1}' if n>1 else f'{y-1}Q4'
    for k in ['rev','np','core']:
        r[k+'_yoy']=(r[k]/Q[f'{y-1}Q{n}'][k]-1)*100 if f'{y-1}Q{n}' in Q else None
        r[k+'_qoq']=(r[k]/Q[prev][k]-1)*100 if prev in Q else None

checks=[]
for i,y in [(1,2024),(2,2025)]:
    for k in ['rev','np','core','cfo']:
        delta=sum(Q[f'{y}Q{n}'][k] for n in range(1,5))-A[i][k]
        assert abs(delta)<=2,(y,k,delta)
        checks.append(f'{y} {k}季度加总差额 {delta} 千元（允许披露舍入差2千元）')
for k in ['rev','cost','np','core','cfo']:
    delta=sum(Q[f'2026Q{n}'][k] for n in [1,2,3])-C['2026Q3'][k]
    assert delta==0,(k,delta)
    checks.append(f'2026前三季 {k}累计核验差额 {delta}')
for r in A:
    assert r['assets']>r['liabilities']

P=[Q[p] for p in ['2024Q4','2025Q1','2025Q2','2025Q3','2025Q4','2026Q1','2026Q2','2026Q3']]
(ROOT/'原始数据/测算结果.json').write_text(json.dumps({'annual':A,'quarters':P,'checks':checks},ensure_ascii=False,indent=2))
fmt=lambda x: '—' if x is None else f'{x:.2f}'
def table(headers, rows):
    return '| '+' | '.join(headers)+' |\n|'+'|'.join(['---']*len(headers))+'|\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)
out='# 宁德时代财务测算底表\n\n金额单位亿元，百分比与比率已单列。所有比率及差分为测算值。\n\n'
out+=table(['指标']+[r['period'] for r in A],[[label]+[fmt(r[key]/100000 if key in ['rev','cost','np','core','cfo','rd','inventory','ar','cash'] else r[key]) for r in A] for label,key in [('收入','rev'),('成本','cost'),('归母','np'),('扣非','core'),('毛利率%','gm'),('归母净利率%','nm'),('经营现金流','cfo'),('研发投入或费用*','rd'),('ROE%','roe'),('资产负债率%','debt_ratio'),('存货','inventory'),('应收账款','ar'),('货币资金','cash')]])
out+='\n*2026前三季研发为费用化研发，ROE未年化。\n\n'
out+=table(['季度','收入','归母','扣非','毛利率%','经营现金流'],[[r['period']]+[fmt(r[k]/100000) for k in ['rev','np','core']]+[fmt(r['gm']),fmt(r['cfo']/100000)] for r in P])
out+='\n'+table(['季度','收入同比%','收入环比%','归母同比%','归母环比%','扣非同比%','扣非环比%'],[[r['period']]+[fmt(r[k]) for k in ['rev_yoy','rev_qoq','np_yoy','np_qoq','core_yoy','core_qoq']] for r in P])
(ROOT/'原始数据/测算底表.md').write_text(out)

# SVG绘图：所有数轴从0起，较小利润采用独立面板，避免双轴混淆。
COL={'收入':'#2778b5','归母净利润':'#e18727','扣非净利润':'#b66c19','经营现金流':'#309674','毛利率':'#8154a8','净利率':'#e18727','ROE':'#309674'}
def txt(x,y,s,size=14,color='#263448',anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{html.escape(str(s))}</text>'
def panel(parts,x,y,w,h,labels,series,title,unit,kind='bar',percent=False):
    parts.append(txt(x,y,title,19)); parts.append(txt(x,y+25,unit,13))
    left=x+58; top=y+48; pw=w-80; ph=h-95
    ymax=max(v for _,vals in series for v in vals)*1.18
    ymin=min(0,math.floor(min(v for _,vals in series for v in vals)/5)*5)
    ymax=math.ceil(ymax/5)*5 if percent else math.ceil(ymax/10)*10
    for j in range(5):
        val=ymin+(ymax-ymin)*j/4; yy=top+ph-ph*j/4
        parts.append(f'<path d="M{left},{yy}h{pw}" stroke="#e5e9ef"/>')
        parts.append(txt(left-8,yy+5,f'{val:.0f}',12,anchor='end'))
    step=pw/len(labels)
    for i,l in enumerate(labels):parts.append(txt(left+step*(i+.5),top+ph+23,l,12,anchor='middle'))
    for si,(name,vals) in enumerate(series):
        color=COL.get(name,['#2778b5','#e18727','#309674','#8154a8'][si%4]); points=[]
        for i,val in enumerate(vals):
            cx=left+step*(i+.5); yy=top+ph-(val-ymin)/(ymax-ymin)*ph
            if kind=='bar':
                bw=step*.72/len(series); bx=cx-step*.36+si*bw
                parts.append(f'<rect x="{bx:.2f}" y="{yy:.2f}" width="{bw*.9:.2f}" height="{val/ymax*ph:.2f}" fill="{color}" rx="2"/>')
                if len(labels)<=4:parts.append(txt(bx+bw*.45,yy-6,f'{val:.1f}',12,color,'middle'))
            else:
                points.append(f'{cx:.2f},{yy:.2f}');parts.append(f'<circle cx="{cx:.2f}" cy="{yy:.2f}" r="4" fill="{color}"/>')
                if len(labels)<=8:parts.append(txt(cx,yy+(-10 if si==0 else 18),f'{val:.1f}',12,color,'middle'))
        if kind!='bar':parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        parts.append(txt(x+60+si*155,y+h-5,'● '+name,14,color))
def figure(name,title,panels,foot,height=620):
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}">','<rect width="100%" height="100%" fill="#fff"/>','<g font-family="Arial Unicode MS,PingFang SC,Microsoft YaHei,sans-serif">',txt(35,38,title,24),txt(35,65,'研究截至2026年10月21日｜中国会计准则合并口径',14)]
    for kwargs in panels:panel(s,**kwargs)
    s.append(txt(35,height-22,foot,13));s.append('</g></svg>')
    (ROOT/'图表'/f'{name}.svg').write_text('\n'.join(s))
ys=[r['period'] for r in A[:3]]
figure('01_年度收入与利润','三年收入与利润规模',[
dict(x=30,y=110,w=560,h=420,labels=ys,series=[('收入',[r['rev']/100000 for r in A[:3]])],title='营业收入',unit='亿元'),
dict(x=620,y=110,w=550,h=420,labels=ys,series=[('归母净利润',[r['np']/100000 for r in A[:3]]),('扣非净利润',[r['core']/100000 for r in A[:3]])],title='归母与扣非利润',unit='亿元')], '来源：2025年报主要指标；2023至2025年均为完整年度。')
figure('02_年度盈利能力','三年盈利能力变化',[
dict(x=30,y=110,w=560,h=420,labels=ys,series=[('毛利率',[r['gm'] for r in A[:3]]),('净利率',[r['nm'] for r in A[:3]])],title='毛利率与归母净利率',unit='百分比，均为测算值',kind='line',percent=True),
dict(x=620,y=110,w=550,h=420,labels=ys,series=[('ROE',[r['roe'] for r in A[:3]])],title='加权平均ROE',unit='百分比，公司披露',kind='line',percent=True)],'来源：2024、2025年报；营业成本统一采用质量保证费用列报调整后的比较口径。')
labs=[r['period'][2:] for r in P]
figure('03_八季度收入利润','八个单季度收入与利润',[
dict(x=30,y=100,w=1140,h=280,labels=labs,series=[('收入',[r['rev']/100000 for r in P])],title='收入',unit='亿元'),
dict(x=30,y=430,w=1140,h=280,labels=labs,series=[('归母净利润',[r['np']/100000 for r in P]),('扣非净利润',[r['core']/100000 for r in P])],title='归母与扣非利润',unit='亿元'),
dict(x=30,y=760,w=1140,h=280,labels=labs,series=[('收入',[r['rev_yoy'] for r in P]),('归母净利润',[r['np_yoy'] for r in P])],title='同比增速',unit='百分比，测算值',kind='line',percent=True)],'来源：各期财报；2026Q2根据累计数据计算，其余收入利润取直接披露值；增长率均为测算。',1110)
figure('04_现金流与利润','经营现金流与归母净利润',[
dict(x=30,y=110,w=560,h=420,labels=ys,series=[('归母净利润',[r['np']/100000 for r in A[:3]]),('经营现金流',[r['cfo']/100000 for r in A[:3]])],title='完整年度',unit='亿元'),
dict(x=620,y=110,w=550,h=420,labels=['25年前三季','26年前三季'],series=[('归母净利润',[C[k]['np']/100000 for k in ['2025Q3','2026Q3']]),('经营现金流',[C[k]['cfo']/100000 for k in ['2025Q3','2026Q3']])],title='同长度期间比较',unit='亿元')],'来源：2025年报与2026三季报；现金流与归母利润分属不同会计口径，需结合营运资金解释。')
figure('05_季度毛利与现金流','最近季度盈利与现金转化',[
dict(x=30,y=100,w=1140,h=280,labels=labs,series=[('毛利率',[r['gm'] for r in P]),('净利率',[r['nm'] for r in P])],title='单季利润率',unit='百分比，均为测算值',kind='line',percent=True),
dict(x=30,y=430,w=1140,h=300,labels=labs,series=[('经营现金流',[r['cfo']/100000 for r in P]),('归母净利润',[r['np']/100000 for r in P])],title='单季现金流与利润',unit='亿元')],'来源：各期财报；季度成本及2026Q2/Q3现金流根据累计数据计算；2024成本采用调整后的比较数。',805)
S=D['segments']['2026H1']; SS=D['segments']['2025H1']
figure('06_产品结构','2026上半年产品收入与毛利率',[
dict(x=30,y=110,w=560,h=420,labels=[r['name'] for r in S],series=[('收入',[r['rev']/100000 for r in S])],title='各产品收入',unit='亿元'),
dict(x=620,y=110,w=550,h=420,labels=[r['name'] for r in S[:3]],series=[('2025上半年',[(1-r['cost']/r['rev'])*100 for r in SS[:3]]),('2026上半年',[(1-r['cost']/r['rev'])*100 for r in S[:3]])],title='同口径产品毛利率',unit='百分比，测算值')],'来源：2026、2025半年报；材料回收与矿产合并比较；其他收入为总收入减三类产品的测算值。')
print(out)
print('核验通过：',len(checks),'项；已生成6张SVG、JSON与Markdown底表。')
