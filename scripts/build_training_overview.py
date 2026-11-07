"""Homepage overview derived from the saved broad-market Parquet snapshot."""
from pathlib import Path
from snapshot_io import read_snapshot

ROOT=Path(__file__).resolve().parents[1]
web=ROOT/'outputs/training-market/web'
data=read_snapshot(web/'summary.parquet')
career=data['us']['career']
early=career.get('Explicit early-career title',0)+career.get('0–3-year experience signal; review required',0)
text=f'''<section class="panel" aria-labelledby="training-overview-title">
<h2 id="training-overview-title">Broader employer training prospects</h2>
<p><strong>{data['us']['analytics']:,}</strong> US analytics-title candidates across <strong>{data['analytics_employer_labels']:,}</strong> employer labels, including <strong>{early:,}</strong> early-career review candidates and <strong>{career.get('Internship / student pathway',0):,}</strong> student pathways.</p>
<p class="tiny">Historical local-data screen across all employers; separate from the selected-employer job explorer. Candidates require review and are not verified current openings.</p>
<a href="training-market.html">Explore the broader evidence and Parquet downloads →</a>
</section>
'''
(web/'overview.html').write_text(text,encoding='utf-8')
print('TRAINING_OVERVIEW_OK')
