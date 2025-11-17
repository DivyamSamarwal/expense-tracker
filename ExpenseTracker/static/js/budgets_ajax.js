document.addEventListener('DOMContentLoaded', function() {
  // Read currency code from meta tag (set in layout.html)
  const currencyCode = document.querySelector('meta[name="app-currency"]')?.content || 'INR';
  const nf = new Intl.NumberFormat(undefined, { style: 'currency', currency: currencyCode });

  document.querySelectorAll('form.budget-edit-form').forEach(form => {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const action = form.action;
      const formData = new FormData(form);

      fetch(action, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: formData,
        credentials: 'same-origin'
      }).then(resp => resp.json())
        .then(data => {
          if (data && data.success) {
            const id = form.dataset.budgetId;
            const amountsEl = document.getElementById(`budgetAmounts${id}`);
            const progressEl = document.getElementById(`budgetProgress${id}`);
            if (amountsEl) {
              amountsEl.textContent = `${nf.format(data.spent)} / ${nf.format(data.available)}`;
            }
            if (progressEl) {
              const pct = Math.round(data.percent);
              progressEl.style.width = `${pct}%`;
              progressEl.setAttribute('aria-valuenow', pct);
              progressEl.textContent = `${pct}%`;
            }
            // close modal (Bootstrap)
            const modalEl = form.closest('.modal');
            if (modalEl) {
              const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
              modal.hide();
            }
          } else {
            alert('Failed to update budget');
          }
        }).catch(err => {
          console.error(err);
          alert('Error updating budget');
        });
    });
  });
});
