/* Small, progressive enhancements. All research content is in the HTML. */
(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.site-nav');
  function closeMenu() {
    if (!toggle || !nav) return;
    toggle.setAttribute('aria-expanded', 'false');
    nav.classList.remove('is-open');
  }
  toggle?.addEventListener('click', () => {
    const opening = toggle.getAttribute('aria-expanded') !== 'true';
    toggle.setAttribute('aria-expanded', String(opening));
    nav.classList.toggle('is-open', opening);
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && toggle?.getAttribute('aria-expanded') === 'true') {
      closeMenu(); toggle.focus();
    }
  });
  nav?.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));

  const search = document.querySelector('#pub-search');
  const year = document.querySelector('#pub-year');
  const chips = Array.from(document.querySelectorAll('[data-topic]'));
  const pubs = Array.from(document.querySelectorAll('[data-publication]'));
  let selectedTopic = 'all';
  function filterPublications() {
    const query = (search?.value || '').trim().toLowerCase();
    const selectedYear = year?.value || 'all';
    let count = 0;
    pubs.forEach(pub => {
      const matches = (selectedYear === 'all' || pub.dataset.year === selectedYear) &&
        (selectedTopic === 'all' || pub.dataset.topics.split('|').includes(selectedTopic)) &&
        query.split(/\s+/).every(word => pub.dataset.search.includes(word));
      pub.hidden = !matches;
      if (matches) count++;
    });
    const counter = document.querySelector('#pub-count');
    if (counter) counter.textContent = `${count} ${count === 1 ? 'publication' : 'publications'}${query || selectedTopic !== 'all' || selectedYear !== 'all' ? ' found' : ' selected'}`;
    const empty = document.querySelector('#no-results');
    if (empty) empty.hidden = count !== 0;
  }
  search?.addEventListener('input', filterPublications);
  year?.addEventListener('change', filterPublications);
  chips.forEach(chip => chip.addEventListener('click', () => {
    selectedTopic = chip.dataset.topic;
    chips.forEach(c => { const active = c === chip; c.classList.toggle('active', active); c.setAttribute('aria-pressed', String(active)); });
    filterPublications();
  }));
  document.querySelector('#pub-reset')?.addEventListener('click', () => {
    search.value = ''; year.value = 'all'; selectedTopic = 'all';
    chips.forEach(c => { const active = c.dataset.topic === 'all'; c.classList.toggle('active', active); c.setAttribute('aria-pressed', String(active)); });
    filterPublications(); search.focus();
  });
  let toastTimer;
  function toast(message) {
    const box = document.querySelector('#toast');
    if (!box) return;
    clearTimeout(toastTimer); box.textContent = message; box.hidden = false;
    toastTimer = setTimeout(() => { box.hidden = true; }, 3500);
  }
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(button.dataset.copy);
      toast(button.classList.contains('copy-citation') ? 'Citation copied.' : 'Email address copied.');
    } catch {
      toast('Copy is unavailable in this browser. Please select and copy the text directly.');
    }
  }));
})();
