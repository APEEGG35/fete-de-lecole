// =========================================================
// Tombola Guy Gérard — script principal.
// Rend les lots (podium / coups de cœur / liste), la recherche,
// les sponsors et l'affichage des gagnants après le tirage.
// =========================================================

(function () {
  'use strict';

  const lots = (window.LOTS || []).slice();
  const winners = window.WINNERS || [];
  const drawDone = !!window.DRAW_DONE;

  // ---------- Helpers ----------
  const fmtEuro = (v) => {
    if (v == null) return '—';
    const rounded = Math.round(v);
    return rounded.toLocaleString('fr-FR') + ' €';
  };

  const escape = (s) => String(s || '').replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));

  const cleanSponsor = (s) => {
    if (!s) return '';
    return s.replace(/\s+/g, ' ').replace(/^l[''']/i, '').trim();
  };

  const winnerFor = (num) => winners.find((w) => w.num === num);

  // ---------- Hero totaux ----------
  const totalValue = lots.reduce((acc, l) => acc + (l.value || 0), 0);
  const totalEl = document.getElementById('totalValue');
  const countEl = document.getElementById('totalLots');
  if (totalEl) totalEl.textContent = fmtEuro(totalValue);
  if (countEl) countEl.textContent = lots.length;

  // ---------- Podium top 3 ----------
  const podiumEl = document.getElementById('podium');
  if (podiumEl) {
    const top3 = lots.slice(0, 3);
    // Re-order pour l'effet podium : 2e, 1er, 3e
    const order = [top3[1], top3[0], top3[2]].filter(Boolean);
    podiumEl.innerHTML = order.map((lot) => {
      const isFirst = lot.rank === 1;
      const isSecond = lot.rank === 2;
      const variant = isFirst ? 'gold' : isSecond ? 'silver' : 'bronze';
      const winner = winnerFor(lot.num);
      const crown = isFirst ? '<span class="podium__crown">Lot principal</span>' : '';
      return `
        <article class="podium__card podium__card--${variant} reveal">
          ${crown}
          <span class="podium__rank">№${lot.rank}</span>
          <h3 class="podium__title">${escape(lot.title)}</h3>
          ${lot.sponsor ? `<p class="podium__sponsor">Offert par <strong>${escape(cleanSponsor(lot.sponsor))}</strong></p>` : ''}
          <div class="podium__value">
            <span class="podium__value-label">Valeur</span>
            <span class="podium__value-amount">${fmtEuro(lot.value)}</span>
          </div>
          ${winner ? `<div class="podium__winner">Gagné par le ticket n°${escape(winner.ticket)}</div>` : ''}
        </article>
      `;
    }).join('');
  }

  // ---------- Highlights 4-10 ----------
  const highlightsEl = document.getElementById('highlights');
  if (highlightsEl) {
    const highlights = lots.slice(3, 10);
    highlightsEl.innerHTML = highlights.map((lot) => {
      const winner = winnerFor(lot.num);
      return `
        <article class="highlight reveal">
          ${winner ? '<span class="highlight__winner-badge">Attribué</span>' : ''}
          <div class="highlight__head">
            <span class="highlight__rank">№${lot.rank}</span>
            <span class="highlight__value">${fmtEuro(lot.value)}</span>
          </div>
          <h3 class="highlight__title">${escape(lot.title)}</h3>
          ${lot.sponsor ? `<p class="highlight__sponsor">Offert par ${escape(cleanSponsor(lot.sponsor))}</p>` : ''}
        </article>
      `;
    }).join('');
  }

  // ---------- Reste de la liste + recherche ----------
  const restEl = document.getElementById('restList');
  const restEmptyEl = document.getElementById('restEmpty');
  const searchEl = document.getElementById('searchLots');
  const restLots = lots.slice(10);

  const renderRest = (filter) => {
    if (!restEl) return;
    const q = (filter || '').trim().toLowerCase();
    const filtered = q
      ? restLots.filter((l) =>
          (l.title + ' ' + (l.sponsor || '') + ' ' + (l.description || ''))
            .toLowerCase()
            .includes(q))
      : restLots;

    if (filtered.length === 0) {
      restEl.innerHTML = '';
      if (restEmptyEl) restEmptyEl.hidden = false;
      return;
    }
    if (restEmptyEl) restEmptyEl.hidden = true;

    restEl.innerHTML = filtered.map((lot) => {
      const winner = winnerFor(lot.num);
      return `
        <li class="rest__item">
          <span class="rest__num">№${lot.rank}</span>
          <div class="rest__body">
            <h4 class="rest__title">${escape(lot.title)}</h4>
            ${lot.sponsor ? `<p class="rest__sponsor">${escape(cleanSponsor(lot.sponsor))}</p>` : ''}
          </div>
          <span class="rest__value">${fmtEuro(lot.value)}</span>
          ${winner ? `<div class="rest__winner">★ Ticket gagnant n°${escape(winner.ticket)}</div>` : ''}
        </li>
      `;
    }).join('');
  };

  renderRest('');
  if (searchEl) {
    searchEl.addEventListener('input', (e) => renderRest(e.target.value));
  }

  // ---------- Sponsors ----------
  const sponsorsEl = document.getElementById('sponsorsGrid');
  if (sponsorsEl) {
    const sponsors = (window.SPONSORS && window.SPONSORS.length)
      ? window.SPONSORS.slice()
      : (function () {
          // Fallback : reconstruire depuis les lots si sponsors.js absent
          const map = new Map();
          lots.forEach((lot) => {
            const s = cleanSponsor(lot.sponsor);
            if (!s) return;
            const key = s.toLowerCase();
            if (!map.has(key)) map.set(key, { name: s, count: 0, totalValue: 0, logo: null });
            const entry = map.get(key);
            entry.count += 1;
            entry.totalValue += (lot.value || 0);
          });
          return Array.from(map.values())
            .sort((a, b) => b.totalValue - a.totalValue);
        })();

    sponsorsEl.innerHTML = sponsors.map((sp) => {
      const lots_label = sp.count > 1 ? 'lots offerts' : 'lot offert';
      if (sp.logo) {
        return `
          <figure class="sponsor sponsor--logo reveal">
            <div class="sponsor__media">
              <img src="${escape(sp.logo)}" alt="${escape(sp.name)}" loading="lazy">
            </div>
            <figcaption class="sponsor__caption">
              <span class="sponsor__name">${escape(sp.name)}</span>
              <span class="sponsor__count"><strong>${sp.count}</strong> ${lots_label}</span>
            </figcaption>
          </figure>
        `;
      }
      return `
        <div class="sponsor sponsor--text reveal">
          <span class="sponsor__name">${escape(sp.name)}</span>
          <span class="sponsor__count"><strong>${sp.count}</strong> ${lots_label}</span>
        </div>
      `;
    }).join('');
  }

  // ---------- Winners section ----------
  const winnersInner = document.getElementById('winnersInner');
  if (winnersInner && drawDone && winners.length) {
    const list = winners
      .slice()
      .sort((a, b) => a.num - b.num)
      .map((w) => {
        const lot = lots.find((l) => l.num === w.num);
        if (!lot) return '';
        return `
          <li class="winners__entry">
            <span class="winners__entry-num">№${lot.rank}</span>
            <div class="winners__entry-body">
              <span class="winners__entry-title">${escape(lot.title)}</span>
              <span class="winners__entry-ticket">Ticket n°${escape(w.ticket)}${w.name ? ' — ' + escape(w.name) : ''}</span>
            </div>
          </li>
        `;
      }).join('');
    winnersInner.innerHTML = `
      <span class="winners__eyebrow">VI. Tirage du 26 juin 2026</span>
      <h2 class="winners__title">Les <em>numéros gagnants</em></h2>
      <p class="winners__placeholder">Bravo à tous les gagnants&nbsp;! Pour récupérer votre lot, contactez l'APEEGG dans le mois suivant le tirage.</p>
      <ul class="winners__list">${list}</ul>
    `;
  }

  // ---------- Reveal on scroll ----------
  if ('IntersectionObserver' in window) {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    document.querySelectorAll('.reveal').forEach((el, i) => {
      el.style.transitionDelay = (i % 8) * 40 + 'ms';
      obs.observe(el);
    });
  } else {
    document.querySelectorAll('.reveal').forEach((el) => el.classList.add('is-visible'));
  }
})();
