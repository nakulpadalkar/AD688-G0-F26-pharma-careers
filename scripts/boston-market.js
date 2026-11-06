/* A transparent planning calculator; defaults are assumptions, not forecasts. */
(() => {
  const root = document.getElementById('sponsor-model');
  if (!root) return;
  const inputs = ['accounts', 'rate', 'seats', 'fee'].map(k => document.getElementById('sponsor-' + k));
  const result = document.getElementById('sponsor-result');
  const format = n => n.toLocaleString('en-US', {maximumFractionDigits: 2});
  function update() {
    if (inputs.some(el => el.value.trim() === '' || !el.checkValidity())) {
      result.textContent = 'Enter valid non-negative values within the ranges shown.';
      return;
    }
    const [accounts, rate, seats, fee] = inputs.map(el => Number(el.value));
    const sponsors = accounts * rate / 100;
    const starters = sponsors * seats;
    result.textContent = `${format(sponsors)} expected sponsoring employers × ${format(seats)} seats = ${format(starters)} expected certificate starters. ` +
      (fee ? `Illustrative tuition receipts: $${format(starters * fee)} before costs and attrition.` : 'Tuition is unspecified.') +
      ' Planning assumptions; no employer commitments are implied.';
  }
  inputs.forEach(el => el.addEventListener('input', update));
  update();
})();
