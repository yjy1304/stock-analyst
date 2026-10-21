from pathlib import Path
import json,sys,os
sys.path.insert(0,'/private/tmp/sf_plot_deps')
os.environ['MPLCONFIGDIR']='/private/tmp/sf_mplconfig'
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

root=Path('/Users/yangjianmin/workspace/股票分析/顺丰控股/01_近3年财报趋势与分析')
d=json.loads((root/'顺丰控股_2023-2026H1_核验数据_截至2026-09-28.json').read_text())
font_manager.fontManager.addfont('/System/Library/Fonts/STHeiti Medium.ttc')
plt.rcParams.update({'font.family':font_manager.FontProperties(fname='/System/Library/Fonts/STHeiti Medium.ttc').get_name(),'font.size':11,'axes.unicode_minus':False,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#334155','text.color':'#182638','axes.titleweight':'bold','figure.facecolor':'#f8fafc','axes.facecolor':'#f8fafc','savefig.facecolor':'#f8fafc'})
c={'rev':'#2866ad','profit':'#c84444','core':'#e3932b','cash':'#168875','gm':'#7655a5','roe':'#576579','net':'#b76993'}
annual=d['annual'];q=d['quarterly']; e=d['annual_extra']; yrs=list(annual)
def finish(fig,name,source,calc=False):
 fig.text(.055,.015,source+'\n统计口径：合并报表；资料截至2026-09-28。'+('  2026年二季度为根据累计数据计算的测算值。' if calc else ''),fontsize=9,color='#64748b')
 fig.savefig(root/'图表'/name,dpi=170,bbox_inches='tight');plt.close(fig)
def style(ax,unit='亿元',zero=True):
 ax.set_ylabel(unit);ax.grid(axis='y',alpha=.17);ax.set_axisbelow(True)
 if zero:ax.set_ylim(bottom=0)
def labels(ax,bars,fmt='{:.1f}'):
 ax.bar_label(bars,labels=[fmt.format(x.get_height()) for x in bars],padding=4,fontsize=10)

fig,axs=plt.subplots(1,2,figsize=(12,4.6));fig.subplots_adjust(bottom=.22,top=.80,wspace=.27)
fig.suptitle('顺丰控股 2023—2025年：收入增长，扣非利润在2025年明显减速',fontsize=17,y=.98)
x=np.arange(3)
b=axs[0].bar(x,[annual[y][0]/1e5 for y in yrs],color=c['rev'],width=.55,label='营业收入');labels(axs[0],b);axs[0].set_ylim(0,3600);axs[0].set_xticks(x,[y+'年' for y in yrs]);axs[0].legend(frameon=False);style(axs[0])
for idx,key,label,shift in [(2,'profit','归母净利润',-.17),(3,'core','扣非归母净利润',.17)]:
 b=axs[1].bar(x+shift,[annual[y][idx]/1e5 for y in yrs],width=.32,color=c[key],label=label);labels(axs[1],b)
axs[1].set_xticks(x,[y+'年' for y in yrs]);axs[1].set_ylim(0,135);axs[1].legend(frameon=False,fontsize=10);style(axs[1])
finish(fig,'01_年度收入与利润.png','来源：公司2025年年报年度比较表。金额为直接披露值换算。')

fig,axs=plt.subplots(1,2,figsize=(12,4.6));fig.subplots_adjust(bottom=.22,top=.80,wspace=.27);fig.suptitle('顺丰控股 2023—2025年：毛利率回落，归母与扣非净利率分化',fontsize=17,y=.98)
series=[(axs[0],'毛利率',[annual[y][1]/annual[y][0]*100 for y in yrs],c['gm']),(axs[0],'加权平均ROE',[e[y]['roe'] for y in yrs],c['roe']),(axs[1],'归母净利率',[annual[y][2]/annual[y][0]*100 for y in yrs],c['profit']),(axs[1],'扣非归母净利率',[annual[y][3]/annual[y][0]*100 for y in yrs],c['core'])]
for ax,label,v,col in series:
 ax.plot(x,v,'o-',color=col,label=label,lw=2.4)
 for xi,yi in zip(x,v):ax.annotate(f'{yi:.2f}%',(xi,yi),xytext=(0,9 if '扣非' not in label else -18),textcoords='offset points',ha='center',fontsize=10,color=col)
for ax in axs:ax.set_xticks(x,[y+'年' for y in yrs]);style(ax,'%');ax.legend(frameon=False,loc='lower right')
axs[0].set_ylim(0,16);axs[1].set_ylim(0,4.4)
for ax in axs:ax.set_xlim(-.28,2.28)
finish(fig,'02_年度盈利能力.png','来源：公司2025年年报；毛利率及净利率按金额计算，ROE为公司披露值。')

ks=[k for k in q if k>='2024Q1'];x=np.arange(len(ks));xt=[k[:4]+'年\n'+'一二三四'[int(k[-1])-1]+'季度'+('＊' if k=='2026Q2' else '') for k in ks]
fig,axs=plt.subplots(3,1,figsize=(13,10),sharex=True);fig.subplots_adjust(bottom=.14,top=.89,hspace=.27);fig.suptitle('顺丰控股 2024年一季度—2026年二季度\n2025年三季度承压，2026年二季度扣非增长再次放缓',fontsize=18,y=.98)
vs=[q[k][0]/1e5 for k in ks];axs[0].plot(x,vs,'o-',color=c['rev'],lw=2.4,label='营业收入')
for i,v in enumerate(vs):axs[0].annotate(f'{v:.1f}',(i,v),xytext=(0,9),textcoords='offset points',ha='center',fontsize=9)
style(axs[0]);axs[0].set_ylim(0,1000);axs[0].legend(frameon=False,loc='lower right')
for idx,key,label,shift in [(2,'profit','归母净利润',-.18),(3,'core','扣非归母净利润',.18)]:
 b=axs[1].bar(x+shift,[q[k][idx]/1e5 for k in ks],width=.34,color=c[key],label=label);labels(axs[1],b)
style(axs[1]);axs[1].set_ylim(0,45);axs[1].legend(frameon=False,ncol=2,loc='upper right')
for idx,key,label in [(0,'rev','收入同比'),(3,'core','扣非归母同比')]:
 vs=[(q[k][idx]/q[str(int(k[:4])-1)+k[4:]][idx]-1)*100 for k in ks];axs[2].plot(x,vs,'o-',color=c[key],lw=2,label=label)
 if idx==3:
  for i,v in enumerate(vs):axs[2].annotate(f'{v:+.1f}%',(i,v),xytext=(0,10),textcoords='offset points',ha='center',fontsize=9,color=c[key])
axs[2].axhline(0,lw=1,color='#94a3b8');style(axs[2],'同比（%）',False);axs[2].set_ylim(-25,65);axs[2].set_xticks(x,xt,fontsize=10);axs[2].legend(frameon=False,ncol=2,loc='upper right')
finish(fig,'03_季度收入利润与同比.png','来源：公司2023—2025年年报、2026年一季报及半年报；同比为计算值。',True)

fig,axs=plt.subplots(1,2,figsize=(12,4.8));fig.subplots_adjust(bottom=.23,top=.80,wspace=.25);fig.suptitle('顺丰控股：经营现金流覆盖利润，但2025年以来现金转换转弱',fontsize=17,y=.98)
groups=[(['2023年','2024年','2025年'],[annual[y][4]/1e5 for y in yrs],[e[y]['net']/1e5 for y in yrs],[annual[y][2]/1e5 for y in yrs]),(['2025上半年','2026上半年'],[12936690/1e5,11171404/1e5],[6012403/1e5,5970017/1e5],[5737699/1e5,5501905/1e5])]
for ax,(ticks,ocf,net,parent) in zip(axs,groups):
 x=np.arange(len(ticks))
 for offset,v,col,label in [(-.23,ocf,c['cash'],'经营现金流'),(0,net,c['net'],'合并净利润'),(.23,parent,c['profit'],'归母净利润')]:
  b=ax.bar(x+offset,v,width=.22,color=col,label=label);ax.bar_label(b,labels=[f'{z:.1f}' for z in v],padding=14 if label=='归母净利润' else 4,fontsize=9)
 ax.set_xticks(x,ticks);style(ax);ax.set_ylim(0,max(ocf)*1.25)
axs[0].legend(frameon=False,fontsize=9,ncol=3,loc='upper left');axs[0].set_title('年度比较',fontsize=12);axs[1].set_title('同期半年比较（未年化）',fontsize=12)
finish(fig,'04_经营现金流与净利润.png','来源：公司2025年年报、2026年半年报。注意：经营现金流未扣资本支出及筹资分类的租赁本金。')

fig,axs=plt.subplots(1,2,figsize=(12,4.7));fig.subplots_adjust(bottom=.23,top=.80,wspace=.25);fig.suptitle('顺丰控股：2025年非经常性收益抬高归母，2026上半年基数回落',fontsize=17,y=.98)
for ax,ticks,pa,core in [(axs[0],[y+'年' for y in yrs],[annual[y][2]/1e5 for y in yrs],[annual[y][3]/1e5 for y in yrs]),(axs[1],['2025上半年','2026上半年'],[57.37699,55.01905],[45.50987,49.74949])]:
 x=np.arange(len(ticks));diff=np.array(pa)-core
 ax.bar(x,core,color=c['core'],label='扣非归母利润',width=.55);ax.bar(x,diff,bottom=core,color=c['profit'],alpha=.65,label='非经常性损益净额',width=.55)
 for i,(a,b,dd) in enumerate(zip(pa,core,diff)):
  ax.text(i,b/2,f'{b:.2f}',ha='center',va='center',color='white');ax.text(i,b+dd/2,f'{dd:.2f}',ha='center',va='center',color='white');ax.text(i,a+2,f'归母 {a:.2f}',ha='center',fontsize=10)
 ax.set_xticks(x,ticks);style(ax);ax.set_ylim(0,max(pa)*1.26)
axs[0].legend(frameon=False,ncol=2,fontsize=10,loc='upper left')
finish(fig,'05_归母与扣非利润.png','来源：公司2025年年报、2026年半年报；非经常性净额=归母−扣非，均为税后归母口径。')

names=['时效快递','经济快递','快运','冷运及医药','同城即时配送','供应链及国际','其他']
v25=[63233100,15160431,19572650,5836978,5493390,34234325];v26=[63365292,16293567,22047671,4397144,6709255,39578020]
v25.append(146858174-sum(v25));v26.append(155506421-sum(v26))
fig,axs=plt.subplots(2,1,figsize=(12,7.4),gridspec_kw={'height_ratios':[1,2]});fig.subplots_adjust(bottom=.16,top=.86,hspace=.6);fig.suptitle('顺丰控股 2026上半年：收入增量更多来自供应链及国际',fontsize=18,y=.97)
cols=['#2866ad','#67a4d7','#168875','#87b8a6','#e3932b','#7655a5','#bcc5ce']
left=np.zeros(2)
for i,n in enumerate(names):
 vals=np.array([v25[i]/146858174,v26[i]/155506421])*100
 axs[0].barh([0,1],vals,left=left,color=cols[i],label=n,height=.55)
 for j,val in enumerate(vals):
  if val>=3:axs[0].text(left[j]+val/2,j,f'{val:.1f}%',ha='center',va='center',fontsize=10,color='white')
 left+=vals
axs[0].set_yticks([0,1],['2025上半年','2026上半年']);axs[0].invert_yaxis();axs[0].set_xlim(0,100);axs[0].set_xlabel('占合并营业收入（%）');axs[0].legend(frameon=False,ncol=4,loc='upper center',bbox_to_anchor=(.5,-.5),fontsize=10)
x=np.arange(6);b=axs[1].bar(x-.19,np.array(v25[:6])/1e5,width=.36,color='#a8bfd8',label='2025上半年');labels(axs[1],b)
b=axs[1].bar(x+.19,np.array(v26[:6])/1e5,width=.36,color=c['rev'],label='2026上半年');labels(axs[1],b)
axs[1].set_xticks(x,names[:6]);style(axs[1]);axs[1].set_ylim(0,760);axs[1].legend(frameon=False,loc='upper right',ncol=2)
finish(fig,'06_业务收入结构.png','来源：公司2026年半年报业务收入表。其他=集团收入减六项业务收入；不等同于某一经营分部。')
print('Generated six charts')
