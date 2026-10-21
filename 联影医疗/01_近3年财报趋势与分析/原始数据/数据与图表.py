"""录入财报原始金额（元），计算单季成本/派生指标，生成JSON、核验表和图表。"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

ROOT = Path(__file__).resolve().parent.parent
FONT = FontProperties(fname='/System/Library/Fonts/STHeiti Medium.ttc')
plt.rcParams.update({'font.family': FONT.get_name(), 'axes.unicode_minus': False,
                     'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False,
                     'savefig.dpi': 170, 'svg.fonttype': 'none'})
FIELDS=['收入','归母净利润','扣非归母净利润','经营现金流','营业成本','研发投入','研发费用','ROE','应收账款','存货','总资产','总负债']
A={
'2023':[11410765602.39,1974292317.49,1664876441.28,132511079.76,6039158708.50,1918617388.39,1728541428.81,10.79,3227657250.54,3893420190.62,25336140321.96,6454724356.28],
'2024':[10300104386.97,1261869451.27,1010323448.82,-619024253.25,5300161724.44,2260827099.47,1761466670.35,6.53,4358808221.15,5528382408.16,28035688872.48,8129447799.81],
'2025':[13800251663.95,1869300805.65,1769843181.21,2679018849.49,7312582446.96,2621356983.46,1841943294.35,9.00,5590248672.01,5728954000.61,32784579366.01,11223198760.08],
'2025H1':[6015901402.16,998018064.12,965612481.04,48759799.77,3132664301.76,1140031078.43,766458924.01,4.90,5080080731.16,5962281307.39,28679059289.45,7892267510.76],
'2026H1':[7051579098.09,896995952.14,826729990.53,-242020101.49,3724610123.40,1382940567.04,1010648325.79,4.12,5866601509.12,7238105817.88,34435499315.37,12414497872.28]}
Q={
'2023Q1':[2212870463.39,329659181.62,276621420.07,-313565330.56],
'2023Q2':[3058475338.25,608117759.25,510359632.27,-197894357.84],
'2023Q3':[2161093385.39,126510279.22,41758148.70,-330624952.90],
'2023Q4':[3978326415.36,910005097.40,836137240.24,974595721.06],
'2024Q1':[2350478362.11,363297720.56,300194937.03,-657050656.93],
'2024Q2':[2983007891.06,586914201.32,497739475.57,32458238.76],
'2024Q3':[1620796921.38,-279048838.22,-333838043.64,-880226438.51],
'2024Q4':[3345821212.42,590706367.61,546227079.86,885794603.43],
'2025Q1':[2477948927.49,370082216.76,378502314.92,-353474219.65],
'2025Q2':[3537952474.67,627935847.36,587110166.12,402234019.42],
'2025Q3':[2843014990.57,122216265.88,87614052.62,58453464.68],
'2025Q4':[4941335271.22,749066475.65,716616647.55,2571805585.04],
'2026Q1':[2907566494.56,398869282.78,371861638.80,-959099481.97]}
Q['2026Q2']=[round(A['2026H1'][i]-Q['2026Q1'][i],2) for i in range(4)]
# 2024累计成本全部使用2025对应报告比较列（质保费用重分类后）；不可混用2024原季报。
COST={'2024':[1185383044.59,2708826710.47,3649810278.99,5300161724.44],
      '2025':[1240455707.69,3132664301.76,4693777044.50,7312582446.96],
      '2026':[1536316521.02,3724610123.40]}
for y, values in COST.items():
    for i,v in enumerate(values): Q[f'{y}Q{i+1}'].append(round(v-(values[i-1] if i else 0),2))
for y in ['2023','2024','2025']:
    for i in range(4): assert abs(sum(Q[f'{y}Q{q}'][i] for q in range(1,5))-A[y][i])<.02
for y in ['2024','2025']: assert abs(sum(Q[f'{y}Q{q}'][4] for q in range(1,5))-A[y][4])<.02
SOURCE={
'2023年报':'https://dataclouds.cninfo.com.cn/shgonggao/2024/2024-04-27/1b62f47c03d311efb2f6fa163e26e5de.pdf',
'2024年报':'https://static.cninfo.com.cn/finalpage/2025-04-29/1223362977.PDF',
'2025年报':'https://global.united-imaging.com/-/media/uih/pdf/investor/20260618cn/summary-of-shanghai-united-imaging-healthcare-co-ltd-2025-annual-report.pdf',
'2024半年报':'https://dataclouds.cninfo.com.cn/shgonggao/2024/2024-08-31/ca4a895866b811ef9e6efa163e26e5de.pdf',
'2024三季报':'https://static.cninfo.com.cn/finalpage/2024-10-31/1221569847.PDF',
'2025一季报':'https://static.cninfo.com.cn/finalpage/2025-04-29/1223362997.PDF',
'2025半年报':'https://global.united-imaging.com/-/media/uih/pdf/investor/20260309-cn/united-imaging-healthcare-first-half-year-report-for-2025.pdf',
'2025三季报':'https://global.united-imaging.com/-/media/uih/pdf/investor/20260309-cn/united-imaging-healthcare-third-quarter-report-for-2025.pdf',
'2026一季报':'https://static.cninfo.com.cn/finalpage/2026-04-29/1225233744.PDF',
'2026半年报':'https://file.finance.sina.com.cn/211.154.219.97%3A9494/MRGG/CNSESH_STOCK/2026/2026-8/2026-08-20/12505097.PDF'}
data={'公司':'联影医疗688271','核验日期':'2026-09-27','金额单位':'人民币元','年度字段':FIELDS,'年度及半年度':A,
      '季度字段':FIELDS[:5],'季度':Q,'累计营业成本原始披露':COST,'来源':SOURCE,
      '口径':'2023年度成本用2024年报重分类后值；2024季度成本用2025对应报告比较列；Q2/Q3/Q4成本累计相减测算；2026Q2四项主指标H1-Q1测算；其余四项季度主指标直接取年报分季度表。ROE为百分比，半年不年化。'}
(ROOT/'原始数据/财务数据.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def growth(a,b):
    if b<=0: return '扭亏' if a>0 else '不适用'
    if a<0: return '转亏'
    return f'{(a/b-1)*100:+.2f}%'
def gm(v): return (1-v[4]/v[0])*100
def table(headers, rows): return '\n'.join(['|'+'|'.join(headers)+'|','|'+'|'.join(['---']*len(headers))+'|']+['|'+'|'.join(map(str,r))+'|' for r in rows])
rows=[]
for i,f in enumerate(FIELDS): rows.append([f]+['—' if A[y][i] is None else f'{A[y][i]:.2f}%' if f=='ROE' else f'{A[y][i]/1e8:.2f}' for y in A])
rows += [['综合毛利率']+[f'{gm(v):.2f}%' for v in A.values()],['归母净利率']+[f'{v[1]/v[0]*100:.2f}%' for v in A.values()],['研发资本化比例']+[f'{(v[5]-v[6])/v[5]*100:.2f}%' for v in A.values()],['资产负债率']+['—' if v[11] is None else f'{v[11]/v[10]*100:.2f}%' for v in A.values()]]
annual_table=table(['指标/亿元',*A.keys()],rows)
qr=[]; gr=[]; keys=list(Q)
for k in keys[4:]:
    v=Q[k]; prev=Q[keys[keys.index(k)-1]]; yoy=Q[f'{int(k[:4])-1}{k[4:]}']
    qr.append([k]+[f'{n/1e8:.2f}' for n in v[:4]]+[f'{gm(v):.2f}%',growth(v[0],yoy[0]),growth(v[0],prev[0])])
    gr.append([k,growth(v[1],yoy[1]),growth(v[1],prev[1]),growth(v[2],yoy[2]),growth(v[2],prev[2])])
qtable=table(['季度','收入','归母','扣非','经营现金流','毛利率*','收入同比','收入环比'],qr)
gtable=table(['季度','归母同比','归母环比','扣非同比','扣非环比'],gr)
(ROOT/'原始数据/核验数据表.md').write_text('# 财报数据核验表\n\n金额亿元；合并口径；净利率为归母净利润/收入。\n\n'+annual_table+'\n\n'+qtable+'\n\n'+gtable+'\n\n*季度毛利率均计算；Q2/Q3/Q4成本由累计差额测算，2026Q2全部金额测算。负基数不报告常规增长百分比。\n',encoding='utf-8')
print(annual_table+'\n'+qtable+'\n'+gtable)
colors={'收入':'#3468b0','归母':'#e58b35','扣非':'#9267ae','现金':'#219c88'}
def finish(fig,name):
    fig.text(.06,.016,'来源：联影医疗定期报告；数据截至2026年6月，核验日2026-09-27。季度成本及2026Q2按累计差额测算。',fontsize=9,color='#596579')
    fig.savefig(ROOT/'图表'/f'{name}.png',bbox_inches='tight'); fig.savefig(ROOT/'图表'/f'{name}.svg',bbox_inches='tight');plt.close(fig)
def style(ax,title,unit):
    ax.set_title(title,loc='left',fontweight='bold',pad=14);ax.set_ylabel(unit);ax.axhline(0,color='#a7afbb',lw=.8);ax.grid(axis='y',alpha=.16);ax.set_axisbelow(True)
years=['2023','2024','2025']; xx=np.arange(3)
fig,axs=plt.subplots(1,2,figsize=(12,4.8));fig.subplots_adjust(bottom=.18,wspace=.25)
for ax,idx,label,color in [(axs[0],0,'营业收入',colors['收入']),(axs[1],1,'归母净利润',colors['归母'])]:
    vals=[A[y][idx]/1e8 for y in years];b=ax.bar(years,vals,color=color,width=.5);ax.bar_label(b,fmt='%.2f',padding=5);ax.set_ylim(0,max(vals)*1.25);style(ax,label+'：2023—2025年','亿元')
finish(fig,'01_年度收入利润')
fig,ax=plt.subplots(figsize=(10,4.8));fig.subplots_adjust(bottom=.2)
for vals,label,color in [([gm(A[y]) for y in years],'综合毛利率',colors['收入']),([A[y][1]/A[y][0]*100 for y in years],'归母净利率',colors['归母']),([A[y][7] for y in years],'加权ROE',colors['扣非'])]:
    ax.plot(years,vals,'o-',label=label,color=color,lw=2)
    for x,v in zip(years,vals):ax.annotate(f'{v:.2f}',(x,v),xytext=(0,9),textcoords='offset points',ha='center',fontsize=10)
ax.set_ylim(0,60);ax.legend(loc='upper center',ncol=3);style(ax,'盈利能力：收入恢复，但利润率尚未回到2023年','%');finish(fig,'02_盈利能力')
ks=keys[4:];x=np.arange(len(ks));fig,axs=plt.subplots(3,1,figsize=(13,10),sharex=True);fig.subplots_adjust(bottom=.1,hspace=.34)
b=axs[0].bar(x,[Q[k][0]/1e8 for k in ks],color=colors['收入'],width=.58);axs[0].bar_label(b,fmt='%.2f',padding=3,fontsize=10);axs[0].set_ylim(0,60);style(axs[0],'十个单季度：2024—2025年完整八季＋2026上半年','收入/亿元')
for idx,label,c,off in [(1,'归母',colors['归母'],-.18),(2,'扣非',colors['扣非'],.18)]:
    axs[1].bar(x+off,[Q[k][idx]/1e8 for k in ks],width=.34,label=label,color=c)
axs[1].legend(ncol=2,loc='upper left');style(axs[1],'2024Q3亏损 → 2025修复 → 2026Q2同比回落','利润/亿元')
ys=[(Q[k][0]/Q[f'{int(k[:4])-1}{k[4:]}'][0]-1)*100 for k in ks]
axs[2].plot(x,ys,'o-',color=colors['收入']);
for i,v in enumerate(ys):axs[2].annotate(f'{v:+.1f}%',(i,v),xytext=(0,9),textcoords='offset points',ha='center',fontsize=9)
axs[2].set_ylim(-40,95);style(axs[2],'收入同比：2025年下半年高增长包含低基数效应','%');axs[2].set_xticks(x,ks);finish(fig,'03_单季度趋势')
fig,axs=plt.subplots(1,2,figsize=(13,5));fig.subplots_adjust(bottom=.2,wspace=.25)
for ax,ks2,title in [(axs[0],years,'年度现金转化'),(axs[1],['2025H1','2026H1'],'同口径上半年比较')]:
    x=np.arange(len(ks2))
    for idx,label,c,off in [(1,'归母净利润',colors['归母'],-.18),(3,'经营现金流',colors['现金'],.18)]:
        b=ax.bar(x+off,[A[k][idx]/1e8 for k in ks2],width=.34,label=label,color=c);ax.bar_label(b,fmt='%.2f',padding=4)
    ax.set_xticks(x,ks2);ax.margins(y=.32);ax.legend(loc='upper center',fontsize=10,ncol=2);style(ax,title,'亿元')
finish(fig,'04_现金流与利润')
fig,axs=plt.subplots(1,2,figsize=(13,5));fig.subplots_adjust(bottom=.2,wspace=.3)
ks2=years+['2026H1'];x=np.arange(4)
for idx,label,c,off in [(8,'应收账款',colors['收入'],-.18),(9,'存货',colors['扣非'],.18)]:
 b=axs[0].bar(x+off,[A[k][idx]/1e8 for k in ks2],width=.34,label=label,color=c);axs[0].bar_label(b,fmt='%.1f',padding=3)
axs[0].set_xticks(x,ks2);axs[0].set_ylim(0,90);axs[0].legend(loc='upper left');style(axs[0],'资产占用仍高：期末账面净额','亿元')
ks3=years+['2025H1','2026H1'];v=[(A[k][5]-A[k][6])/A[k][5]*100 for k in ks3];b=axs[1].bar(ks3,v,color=colors['扣非'],width=.5);axs[1].bar_label(b,fmt='%.2f%%',padding=5);axs[1].set_ylim(0,42);style(axs[1],'研发资本化：2026H1同比回落','%');finish(fig,'05_资产占用与研发')
fig,ax=plt.subplots(figsize=(11,5));fig.subplots_adjust(bottom=.18)
cats=['MR磁共振','CT断层扫描','MI分子影像','XR射线','RT放疗','维修服务'];a=np.array([319227.51,304816.27,129909.62,58688.93,31851.79,135592.530309])/1e4;b=np.array([454768.60,354530.90,190786.87,79807.33,59090.95,170798.32])/1e4
x=np.arange(6);ax.bar(x-.18,a,width=.34,label='2024',color='#b8cdea');bars=ax.bar(x+.18,b,width=.34,label='2025',color=colors['收入']);ax.bar_label(bars,fmt='%.2f',padding=4);ax.set_xticks(x,cats);ax.set_ylim(0,56);ax.legend();style(ax,'产品收入：增长由多条产品线共同贡献','亿元');finish(fig,'06_产品结构')
