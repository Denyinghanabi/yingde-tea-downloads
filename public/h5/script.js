(() => {
  const pages = Array.from(document.querySelectorAll('.page'));
  const prev = document.querySelector('#prev');
  const next = document.querySelector('#next');
  const number = document.querySelector('#pageNumber');
  const fill = document.querySelector('#lineFill');
  const sound = document.querySelector('#sound');
  const audio = document.querySelector('#ambience');
  let current = 0;
  let finishTransition = null;
  const stage = document.querySelector('.pages');
  const experience = document.querySelector('#experience');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const wash = document.createElement('div');
  wash.className = 'transition-wash';
  wash.setAttribute('aria-hidden', 'true');
  stage.appendChild(wash);

  function show(index) {
    if (index < 0 || index >= pages.length || index === current) return;
    if (finishTransition) finishTransition();
    const from = pages[current];
    const to = pages[index];
    const direction = index > current ? 1 : -1;
    current = index;
    from.classList.remove('active');
    to.hidden = false;
    to.classList.add('active');
    experience.classList.toggle('light-ui', [0, 2, 4, 5, 7, 8].includes(current));
    number.textContent = String(current + 1).padStart(2, '0');
    fill.style.width = `${(current + 1) / pages.length * 100}%`;
    prev.disabled = current === 0;
    next.disabled = current === pages.length - 1;
    prev.setAttribute('aria-label', `上一页，${Math.max(1, current)} / ${pages.length}`);
    next.setAttribute('aria-label', `下一页，${Math.min(pages.length, current + 2)} / ${pages.length}`);

    if (reduceMotion.matches || !to.animate) { from.hidden = true; return; }
    from.classList.add('page-leaving');
    to.classList.add('page-entering');
    const opts = { duration: 760, easing: 'cubic-bezier(.22,.72,.18,1)', fill: 'both' };
    const incoming = to.animate([
      { clipPath: direction > 0 ? 'inset(100% 0 0 0)' : 'inset(0 0 100% 0)', transform: `translateY(${direction * 3}%) scale(1.025)` },
      { clipPath: 'inset(0 0 0 0)', transform: 'translateY(0) scale(1)' }
    ], opts);
    const outgoing = from.animate([
      { transform: 'translateY(0) scale(1)', filter: 'brightness(1)' },
      { transform: `translateY(${-direction * 7}%) scale(.98)`, filter: 'brightness(.72)' }
    ], opts);
    const sweep = wash.animate([
      { opacity: 0, transform: `translateY(${direction * 70}%)` },
      { opacity: .6, offset: .38 },
      { opacity: 0, transform: `translateY(${-direction * 70}%)` }
    ], { duration: 760, easing: 'ease-in-out' });
    let done = false;
    const finish = () => {
      if (done) return;
      done = true;
      from.hidden = true;
      from.classList.remove('page-leaving');
      to.classList.remove('page-entering');
      incoming.cancel(); outgoing.cancel(); sweep.cancel();
      if (finishTransition === finish) finishTransition = null;
    };
    finishTransition = finish;
    incoming.finished.then(finish, finish);
  }
  prev.disabled = true;
  fill.style.width = `${100 / pages.length}%`;
  prev.addEventListener('click', () => show(current - 1));
  next.addEventListener('click', () => show(current + 1));
  document.querySelector('#home').addEventListener('click', () => show(1));
  document.addEventListener('keydown', event => {
    if (event.target.closest('[role=tablist]')) return;
    if (event.key === 'ArrowDown' || event.key === 'ArrowRight') { event.preventDefault(); show(current + 1); }
    if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') { event.preventDefault(); show(current - 1); }
  });
  let startY = 0, startX = 0;
  stage.addEventListener('touchstart', event => { startY = event.touches[0].clientY; startX = event.touches[0].clientX; }, { passive: true });
  stage.addEventListener('touchend', event => {
    const dx = event.changedTouches[0].clientX - startX;
    const dy = event.changedTouches[0].clientY - startY;
    if (Math.abs(dy) > 60 && Math.abs(dy) > Math.abs(dx) * 1.2) show(current + (dy < 0 ? 1 : -1));
  }, { passive: true });
  const steps = [
    { title: '鲜叶', text: '从茶园采下鲜叶，留住山间的清新。', image: '素材精选/tea_picker.jpg', alt: '采摘鲜叶' },
    { title: '制作', text: '鲜叶经过加工，逐渐形成红茶的色与香。', image: '素材精选/tea_garden_main.jpg', alt: '山地茶园' },
    { title: '成茶', text: '制成的茶叶色泽乌黑红润，香气渐成。', image: '素材精选/tea_set.jpg', alt: '茶具与茶叶' },
    { title: '入杯', text: '热水注入，茶汤红艳明亮，香气随之舒展。', image: '素材精选/tea_pour.jpg', alt: '冲泡茶汤' }
  ];
  document.querySelectorAll('[data-step]').forEach(button => button.addEventListener('click', () => {
    const index = Number(button.dataset.step), step = steps[index];
    document.querySelectorAll('[data-step]').forEach(item => item.setAttribute('aria-selected', String(item === button)));
    document.querySelector('#stepNumber').textContent = `${String(index + 1).padStart(2, '0')} / 04`;
    document.querySelector('#stepTitle').textContent = step.title;
    document.querySelector('#stepText').textContent = step.text;
    const image = document.querySelector('#stepImage'); image.src = step.image; image.alt = step.alt;
    const card = document.querySelector('.process-card');
    if (!reduceMotion.matches && card.animate) {
      card.getAnimations().forEach(animation => animation.cancel());
      card.animate([{ opacity: .55, transform: 'translateY(8px) scale(.985)' }, { opacity: 1, transform: 'translateY(0) scale(1)' }], { duration: 420, easing: 'cubic-bezier(.2,.7,.2,1)' });
    }
  }));
  sound.addEventListener('click', async () => {
    if (!audio.paused) { audio.pause(); sound.setAttribute('aria-pressed', 'false'); sound.setAttribute('aria-label', '开启环境声音'); return; }
    try { await audio.play(); sound.setAttribute('aria-pressed', 'true'); sound.setAttribute('aria-label', '关闭环境声音'); }
    catch { sound.setAttribute('aria-label', '声音无法播放，请检查设备设置'); }
  });
})();

