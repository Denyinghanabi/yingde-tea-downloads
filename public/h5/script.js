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
    experience.dataset.currentPage = String(current + 1);
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
  stage.addEventListener('touchstart', event => { if (event.target.closest('button,[role=tablist]')) { startY = startX = NaN; return; } startY = event.touches[0].clientY; startX = event.touches[0].clientX; }, { passive: true });
  stage.addEventListener('touchend', event => {
    const dx = event.changedTouches[0].clientX - startX;
    const dy = event.changedTouches[0].clientY - startY;
    if (Math.abs(dy) > 60 && Math.abs(dy) > Math.abs(dx) * 1.2) show(current + (dy < 0 ? 1 : -1));
  }, { passive: true });
  const steps = [
    { title: '鲜叶', text: '从茶园采下一片鲜叶\n留住山间自然的清新', image: '素材精选/品质切换/process_leaf.jpg', alt: '采摘鲜叶' },
    { title: '制作', text: '鲜叶经过细致加工\n逐渐形成红茶的色与香', image: '素材精选/品质切换/process_craft.jpg', alt: '鲜叶投入制茶设备' },
    { title: '成茶', text: '制成的茶叶乌黑红润\n香气在时间里慢慢凝聚', image: '素材精选/品质切换/process_dry.jpg', alt: '干茶与红茶汤' },
    { title: '入杯', text: '热水注入 茶汤红艳明亮\n香气随热气缓缓舒展', image: '素材精选/品质切换/process_cup.jpg', alt: '茶汤斟入白瓷盖碗' }
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
  // Keep semantic state independent of animation completion, including rapid clicks.
  const qualityTabs = [...document.querySelectorAll('[data-quality]')];
  const qualityPhotos = [...document.querySelectorAll('[data-quality-image]')];
  const captions = ['茶汤红艳，入口醇滑', '一盏透亮，细品甜爽', '热水唤醒，鲜香徐来'];
  let qualityIndex = 0;
  qualityPhotos.forEach(image => { image.loading = 'eager'; image.decoding = 'async'; image.decode().catch(() => {}); });
  steps.forEach(step => { const preload = new Image(); preload.src = step.image; });
  function selectQuality(index, focus = false) {
    qualityIndex = index;
    qualityTabs.forEach((tab, i) => {
      tab.setAttribute('aria-selected', String(i === index));
      tab.tabIndex = i === index ? 0 : -1;
    });
    qualityPhotos.forEach((image, i) => {
      image.classList.toggle('is-selected', i === index);
      image.setAttribute('aria-hidden', String(i !== index));
    });
    document.querySelector('#qualityCaption').textContent = captions[index];
    document.querySelector('#qualityPanel').setAttribute('aria-labelledby', qualityTabs[index].id);
    if (focus) qualityTabs[index].focus();
  }
  qualityTabs.forEach((tab, index) => {
    tab.addEventListener('click', event => { event.stopPropagation(); selectQuality(index); });
    tab.addEventListener('keydown', event => {
      let next = qualityIndex;
      if (event.key === 'ArrowRight') next = (qualityIndex + 1) % 3;
      else if (event.key === 'ArrowLeft') next = (qualityIndex + 2) % 3;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = 2;
      else return;
      event.preventDefault(); event.stopPropagation(); selectQuality(next, true);
    });
  });
  const tasteTabs = [...document.querySelectorAll('[data-taste]')];
  const tasteImages = [...document.querySelectorAll('[data-taste-image]')];
  tasteImages.forEach(image => { image.decode().catch(() => {}); });
  tasteTabs.forEach((tab, index) => tab.addEventListener('click', event => {
    event.stopPropagation();
    tasteTabs.forEach((t,i) => t.setAttribute('aria-selected', String(i === index)));
    tasteImages.forEach((image,i) => { image.classList.toggle('is-selected', i === index); image.setAttribute('aria-hidden',String(i !== index)); });
  }));
  sound.addEventListener('click', async () => {
    if (!audio.paused) { audio.pause(); sound.setAttribute('aria-pressed', 'false'); sound.setAttribute('aria-label', '开启环境声音'); return; }
    try { await audio.play(); sound.setAttribute('aria-pressed', 'true'); sound.setAttribute('aria-label', '关闭环境声音'); }
    catch { sound.setAttribute('aria-label', '声音无法播放，请检查设备设置'); }
  });
})();

