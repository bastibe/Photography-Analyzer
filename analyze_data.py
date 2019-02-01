import numpy
from matplotlib.pyplot import subplots
from pandas import read_pickle
df = read_pickle('metadata.pkl')

# convert columns to categories
for col in ['Camera Model Name', 'Lens']:
    df.loc[:, col] = df.loc[:, col].astype('category')

# select only relevant pictures (high rating, and my camera)
goodones = df.query('Rating > 2')
goodones = goodones[goodones.loc[:, 'Camera Model Name'] == 'NIKON D7000']
goodones.Lens = goodones.Lens.cat.remove_unused_categories()

# set up figure and subplots (adjust for different number of lenses)
fig, axes = subplots(nrows=4, ncols=2, figsize=(8,10))
axes = axes.ravel()

# plot focal length histograms for each lens:
axidx = 0
for cat, grp in goodones.groupby('Lens'):
    # calculate common histogram edges:
    _, edges = numpy.histogram(grp.loc[:, 'Focal Length'])
    # calculate histograms for every rating:
    hists = [[r, numpy.histogram(g.loc[:, 'Focal Length'], bins=edges)[0]] for r, g in grp.groupby('Rating')]

    # plot stacked histograms:
    bottom = numpy.zeros(len(edges)-1)
    for rating, hist in hists:
        axes[axidx].bar((edges[:-1]+edges[1:])/2, hist,
                        bottom=bottom, width=(edges[1]-edges[0])/2,
                        label='★' * int(rating), color=f'C{int(rating-3)}')
        bottom += hist
    axes[axidx].set(title=f'{cat} ({len(grp)} pictures)',
                    xlabel='Focal Length', ylabel='Number of Pictures')
    axes[axidx].legend()
    axidx += 1

# plot lens histograms:
lenses =[]
for idx, [lens, grp] in enumerate(goodones.groupby('Lens')):
    bottom = 0
    lenses.append(lens)
    for rating, color in zip([3, 4, 5], ['C0', 'C1', 'C2']):
        count = len(grp[grp.Rating == rating])
        axes[-2].bar([idx], [count], color=color,
                     bottom=[bottom], width=0.5,
                     label='★' * rating if idx == 0 else None)
        bottom += count
axes[-2].legend()
axes[-2].set(xticks=range(len(lenses)), xticklabels=lenses, ylabel='Number of Pictures')
axes[-2].tick_params(axis='x', rotation=30)

# plot normalized focal length histogram:
_, edges = numpy.histogram(goodones.loc[:, 'Focal Length'], bins=15)
hists = [[r, numpy.histogram(g.loc[:, 'Focal Length'], bins=edges)[0]] for r, g in goodones.groupby('Rating')]
hist_sums = numpy.histogram(goodones.loc[:, 'Focal Length'], bins=edges)[0]
bottom = numpy.zeros(len(edges)-1)
for rating, hist in hists:
    axes[-1].bar((edges[:-1]+edges[1:])/2, hist/hist_sums*100,
                 bottom=bottom, width=(edges[1]-edges[0])*0.75,
                 label='★' * int(rating), color=f'C{int(rating-3)}')
    bottom += hist/hist_sums * 100
axes[-1].set(title=f'All {len(goodones)} pictures',
             xlabel='Focal Length', ylabel='Percentage of Pictures (bars)')
newax = axes[-1].twinx()
newax.plot((edges[:-1]+edges[1:])/2, hist_sums,
           color='C3')
newax.set(ylabel='Number of Pictures (line)', ylim=[0, hist_sums.max()*1.05])

fig.tight_layout()
fig.savefig('analysis.pdf')
fig.savefig('analysis.png')
