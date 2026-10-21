"""2026-09-22 复核版。金额原始值：元；仅生成图表，数据口径见报告。
运行：MPLCONFIGDIR=/private/tmp/gd-mpl /Users/yangjianmin/anaconda3/bin/python3.9 本文件
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

OUT = Path(__file__).resolve().parent
font = '/System/Library/Fonts/STHeiti Medium.ttc'
font_manager.fontManager.addfont(font)
plt.rcParams.update({'font.family': font_manager.FontProperties(fname=font).get_name(),
    'axes.unicode_minus': False, 'font.size': 11, 'axes.spines.top': False,
    'axes.spines.right': False, 'axes.titleweight': 'bold', 'figure.facecolor':'#f5f7fa',
    'axes.facecolor':'#f5f7fa', 'savefig.facecolor':'#f5f7fa', 'svg.fonttype':'path'})
C = {'收入':'#2875b9','归母':'#dd8740','扣非':'#7652a1','现金':'#249683','毛利':'#c04e63','净利':'#dd8740','ROE':'#617080'}
SOURCES = {
 '2023年报':'https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=10007264',
 '2024年报':'https://static.cninfo.com.cn/finalpage/2025-04-26/1223305062.PDF',
 '2025年报':'https://static.cninfo.com.cn/finalpage/2026-03-31/1225061352.PDF',
 '2024半年报':'https://vip.stock.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=10390175&stockid=603986',
 '2025三季报':'https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=11551919&stockid=603986',
 '2026一季报':'https://static.cninfo.com.cn/finalpage/2026-04-30/1225257883.PDF',
 '2026半年报':'https://static.cninfo.com.cn/finalpage/2026-08-19/1225480384.PDF'
}
# 年报直接披露的单季收入、归母、扣非、经营现金流；2026Q2由H1减Q1。
raw = [
 ('2023Q3',1428675586.88,97693933.50,65051821.99,336642071.65),
 ('2023Q4',1366335763.95,-272534285.03,-313125907.56,205545771.69),
 ('2024Q1',1627269967.75,204785920.62,183748478.85,627484517.11),
 ('2024Q2',1981767352.42,312214093.06,289701496.85,621231196.19),
 ('2024Q3',2040559511.23,315112515.15,304019306.91,608130628.69),
 ('2024Q4',1706380845.71,270430272.85,253010066.10,175383895.02),
 ('2025Q1',1909062290.61,234630087.42,223856594.91,335849288.78),
 ('2025Q2',2241246342.27,340845518.40,320575670.11,621971642.69),
 ('2025Q3',2681325810.90,507752274.22,497699926.92,837824687.58),
 ('2025Q4',2371828680.80,564794771.66,427064360.78,332858593.44),
 ('2026Q1',4188075574.04,1461248353.08,1410064284.20,1783057278.72),
 ('2026Q2',11565760432.15-4188075574.04,6856786413.68-1461248353.08,4883033478.93-1410064284.20,6048341057.06-1783057278.72)
]
q = np.array([r[1:] for r in raw], dtype=float)/1e8
labels = [r[0].replace('Q','年Q') for r in raw[4:]]
# 累计成本差分：2024H1、9M、FY；2025Q1、H1、9M、FY；2026Q1、H1。
cost = np.array([3420278140.36-2231971107.10,4560624797.99-3420278140.36,
 1194301276.72,2605975689.03-1194301276.72,4195422101.55-2605975689.03,
 5502180091.92-4195422101.55,1797659470.90,4264243719.27-1797659470.90])/1e8
gm = (1-cost/q[4:,0])*100
annual = np.array([
 [5760823414.65,161141224.88,27400630.30,1186749309.93,3777808042.97],
 [7355977677.11,1102542801.68,1030479348.71,2032230237.01,4560624797.99],
 [9203463124.58,1648022651.70,1469196552.72,2128504212.49,5502180091.92]
])/1e8

def frame(title, rows=1, cols=1, size=(13,6)):
    fig, axs=plt.subplots(rows,cols,figsize=size,squeeze=False)
    fig.suptitle(title,x=.06,ha='left',fontsize=19,fontweight='bold',y=.975)
    for ax in axs.flat:
        ax.grid(axis='y',alpha=.18); ax.set_axisbelow(True)
    return fig,axs

def finish(fig,name,note):
    fig.text(.06,.025,'核验截至2026-09-22；财报截至2026-06-30。来源：公司定期报告（正文附原文链接）。\n'+note,fontsize=9,color='#576573')
    fig.subplots_adjust(left=.07,right=.96,top=.83,bottom=.26 if name=='05_产品结构' else .19,hspace=.55,wspace=.28)
    for ext in ['png','svg']: fig.savefig(OUT/(name+'.'+ext),dpi=180)
    plt.close(fig)

def bars(ax, xs, data, color,label,width=.34):
    b=ax.bar(xs,data,width=width,color=color,label=label)
    ax.bar_label(b,fmt='%.2f',padding=3,fontsize=10)
    ax.set_ylim(0,max(data)*1.25 if max(data)>0 else 1)

def line(ax,x,ys,color,label):
    ax.plot(x,ys,'o-',color=color,label=label,lw=2.2)
    for a,b in zip(x,ys): ax.annotate(f'{b:.1f}',(a,b),xytext=(0,7),textcoords='offset points',ha='center',fontsize=9)

if __name__=='__main__':
    # 验证年报季度加总和H1差分。
    for i,start in [(1,2),(2,6)]:
        assert np.allclose(q[start:start+4].sum(axis=0),annual[i,:4],atol=1e-8)
    assert abs(sum(cost[2:6])-annual[2,4])<1e-8
    assert abs(sum(q[-2:,2])-48.8303347893)<1e-8
    x=np.arange(3)
    fig,axs=frame('兆易创新｜年度复苏：收入修复快，ROE仍需结合周期看',cols=2)
    bars(axs[0,0],x,annual[:,0],C['收入'],'营业收入');axs[0,0].set_title('营业收入（亿元）')
    ax=axs[0,1]
    b=ax.bar(x-.18,annual[:,1],.34,label='归母净利润',color=C['归母']);ax.bar_label(b,fmt='%.2f',padding=3)
    b=ax.bar(x+.18,annual[:,2],.34,label='扣非净利润',color=C['扣非']);ax.bar_label(b,fmt='%.2f',padding=3)
    ax.set_ylim(0,20);ax.legend(loc='upper left');ax.set_title('归母与扣非净利润（亿元）')
    for ax in axs.flat: ax.set_xticks(x,['2023年','2024年','2025年'])
    finish(fig,'01_年度收入利润','2023—2025完整年度；非经常性损益差额为税后归母口径。')

    fig,axs=frame('兆易创新｜年度盈利能力：恢复趋势已确立')
    ax=axs[0,0]
    for ys,k,label in [((1-annual[:,4]/annual[:,0])*100,'毛利','综合毛利率'),(annual[:,1]/annual[:,0]*100,'净利','归母净利率'),([1.06,6.94,9.30],'ROE','加权ROE')]: line(ax,x,ys,C[k],label)
    ax.set_xticks(x,['2023年','2024年','2025年']);ax.set_ylim(0,50);ax.set_ylabel('%');ax.legend(loc='upper left',ncol=3)
    finish(fig,'02_年度盈利能力','毛利率=(收入-成本)/收入；归母净利率=归母净利润/收入；ROE为公司披露值。')

    x=np.arange(8)
    fig,axs=frame('兆易创新｜八季度：2026年二季度经营利润继续加速',rows=2,cols=2,size=(15,9))
    bars(axs[0,0],x,q[4:,0],C['收入'],'收入');axs[0,0].set_title('单季营业收入（亿元）')
    ax=axs[0,1]
    for off,col,k,label in [(-.18,1,'归母','归母净利润'),(.18,2,'扣非','扣非净利润')]:
        b=ax.bar(x+off,q[4:,col],.34,color=C[k],label=label);ax.bar_label(b,fmt='%.1f',padding=13 if off<0 else 3,fontsize=8)
    ax.set_ylim(0,65);ax.legend();ax.set_title('单季利润（亿元）')
    yoy=(q[4:,0]/q[:-4,0]-1)*100;line(axs[1,0],x,yoy,C['收入'],'收入同比');axs[1,0].set_title('单季收入同比（%）');axs[1,0].set_ylim(0,280)
    line(axs[1,1],x,gm,C['毛利'],'毛利率');line(axs[1,1],x,q[4:,2]/q[4:,0]*100,C['扣非'],'扣非净利率')
    axs[1,1].set_ylim(0,82);axs[1,1].set_title('单季利润率（%）');axs[1,1].legend(loc='upper left')
    for ax in axs.flat: ax.set_xticks(x,labels,rotation=25,ha='right');ax.tick_params(axis='x',labelsize=9)
    finish(fig,'03_八季度趋势','2024Q3—2026Q2；2026Q2流量及Q2/Q3/Q4成本根据累计数据计算，均为测算值；完整底表见正文。')

    fig,axs=frame('兆易创新｜现金与利润：扣非口径更适合评估经营质量',cols=2,size=(14,6))
    for ax,data,labs,title in [(axs[0,0],annual[:,:4],['2023年','2024年','2025年'],'完整年度（亿元）'),(axs[0,1],q[-4:],labels[-4:],'最近四季度（亿元）')]:
        x=np.arange(len(data))
        for off,col,k,lab in [(-.25,1,'归母','归母'),(0,2,'扣非','扣非'),(.25,3,'现金','经营现金流')]:
            b=ax.bar(x+off,data[:,col],.24,color=C[k],label=lab);ax.bar_label(b,fmt='%.1f',padding=3,fontsize=8)
        ax.set_xticks(x,labs);ax.set_ylim(0,max(data[:,1:].flat)*1.28);ax.set_title(title);ax.legend(ncol=3,fontsize=9)
    finish(fig,'04_现金流与利润','利润不等于现金流；应付款、存货、税款与利息都会影响经营现金流。2026Q2由H1减Q1测算。')

    product=np.array([[65.659399695,19.0989792287,3.8935494948,3.3284360057,.042215365],[98.2748058964,14.2976229693,1.0025061133,1.9064084662,.1762608763]])
    fig,axs=frame('兆易创新｜产品结构：存储占比上升，周期暴露也在上升',cols=2,size=(14,6))
    ax=axs[0,0];bottom=np.zeros(2);names=['存储','MCU','传感器','模拟','其他'];colors=[C['收入'],C['现金'],'#9ca8b4',C['扣非'],'#d7dce1']
    for j,(name,color) in enumerate(zip(names,colors)):
        values=product[:,j]/product.sum(axis=1)*100;ax.bar([0,1],values,bottom=bottom,label=name,color=color,width=.55)
        for i,v in enumerate(values):
            if v>5: ax.text(i,bottom[i]+v/2,f'{v:.1f}%',ha='center',va='center',color='white')
        bottom+=values
    ax.set_xticks([0,1],['2025全年','2026上半年']);ax.set_ylim(0,105);ax.set_title('主营收入结构（%）');ax.legend(loc='upper center',bbox_to_anchor=(.5,-.09),ncol=3,fontsize=9)
    ax=axs[0,1];x=np.arange(4);g26=(1-np.array([3186960655.16,879515137.48,80605934.03,113432093.44])/1e8/product[1,:4])*100
    for off,values,color,lab in [(-.18,[42.84,35.82,19.57,36.96],'#a9bfd2','2025全年'),(.18,g26,'#2875b9','2026上半年')]:
        b=ax.bar(x+off,values,.34,label=lab,color=color);ax.bar_label(b,fmt='%.1f',padding=3)
    ax.set_xticks(x,names[:4]);ax.set_ylim(0,83);ax.set_title('各产品毛利率（%）');ax.legend()
    finish(fig,'05_产品结构','2025与2026H1为结构及利润率对照，非同长度收入增速比较；2026H1毛利率由收入、成本测算。')

    fig,axs=frame('兆易创新｜估值敏感性：先判断可持续利润，再讨论便宜',size=(12,6))
    ax=axs[0,0];profits=np.array([40,60,80,100,120]);pes=np.array([20,25,30,35,40]);prices=pes[:,None]*profits[None,:]/7.0175
    ax.grid(False);ax.imshow(prices,cmap='Blues',aspect='auto',vmin=100,vmax=700)
    ax.set_xticks(np.arange(5),[str(v) for v in profits]);ax.set_yticks(np.arange(5),[str(v)+'倍' for v in pes]);ax.set_xlabel('假设可持续年度归母利润（亿元）');ax.set_ylabel('假设市盈率')
    for i in range(5):
        for j in range(5): ax.text(j,i,f'{prices[i,j]:.0f}元',ha='center',va='center',color='white' if prices[i,j]>430 else '#18334a',fontsize=14)
    finish(fig,'06_估值敏感性','纯假设，非目标价：假定总股本7.0175亿股，价格=利润×PE/股数；不额外加现金/投资资产，避免重复计价。')

    print('八季度底表：收入|归母|扣非|成本|毛利率|收入同比|收入环比|归母同比|归母环比|扣非同比|扣非环比|现金流')
    for i in range(4,len(raw)):
        a=q[i];p=q[i-1];b=q[i-4]
        growth=lambda v,base: '扭亏' if base<0<=v else f'{(v/base-1)*100:.2f}%'
        print('|'+raw[i][0]+'|'+'|'.join([*(f'{v:.2f}' for v in a[:3]),f'{cost[i-4]:.2f}',f'{gm[i-4]:.2f}%',growth(a[0],b[0]),growth(a[0],p[0]),growth(a[1],b[1]),growth(a[1],p[1]),growth(a[2],b[2]),growth(a[2],p[2]),f'{a[3]:.2f}'])+'|')
    print('TTM归母、扣非', annual[-1,1:3]+q[-2:,1:3].sum(0)-q[6:8,1:3].sum(0))
    print('charts=6 PNG + 6 SVG; arithmetic reconciliation passed')
