/* ============================================================
   木喜身心靈 · 互動
   1) 輕量 YouTube：先顯示縮圖，點擊才載入播放器（省流量）
   2) 有聲書朗讀：瀏覽器語音合成（Web Speech API），自動挑最自然的中文語音
   ============================================================ */

/* ---------- 1. 輕量 YouTube ---------- */
document.addEventListener('click', function(e){
  const yt = e.target.closest('.yt');
  if(!yt) return;
  const id = yt.dataset.id;
  if(!id || yt.dataset.loaded) return;
  yt.dataset.loaded = '1';
  const ifr = document.createElement('iframe');
  // 標準網域 + 帶上來源（避免錯誤 153）；file:// 開啟時 origin 為 null，YouTube 仍會擋
  const origin = (location.protocol === 'http:' || location.protocol === 'https:') ? '&origin=' + encodeURIComponent(location.origin) : '';
  ifr.src = 'https://www.youtube.com/embed/' + id + '?autoplay=1&rel=0&playsinline=1' + origin;
  ifr.title = 'YouTube';
  ifr.allow = 'accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture';
  ifr.allowFullscreen = true;
  ifr.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;border:0;';
  yt.innerHTML = '';
  yt.appendChild(ifr);
});

/* ---------- 2. 有聲書朗讀 ---------- */
(function(){
  const btn = document.getElementById('btn-read');
  if(!btn) return;
  const synth = window.speechSynthesis;
  if(!synth){ btn.style.display='none'; return; }

  // 收集要朗讀的段落
  const paras = Array.from(document.querySelectorAll('article.reading p'));
  let idx = 0, playing = false, paused = false;

  // 挑選最自然的中文語音：偏好 Google / 線上自然語音
  function pickVoice(){
    const vs = synth.getVoices();
    const zh = vs.filter(v => /zh|cmn|Chinese/i.test(v.lang + v.name));
    const prefer = ['Google 國語','Google 普通话','Google 粤語','Mei-Jia','Meijia','Tingting','Sinji','Yu-shu','美佳','Microsoft HsiaoChen','Microsoft Yating'];
    for(const name of prefer){
      const hit = zh.find(v => v.name.includes(name));
      if(hit) return hit;
    }
    return zh.find(v => /^zh-TW/i.test(v.lang)) || zh[0] || null;
  }
  let voice = pickVoice();
  if(synth.onvoiceschanged !== undefined){
    synth.onvoiceschanged = () => { voice = pickVoice(); };
  }

  function setLabel(state){
    const map = {play:'▶ 朗讀本章', pause:'⏸ 暫停', resume:'▶ 繼續'};
    btn.querySelector('.txt').textContent = state;
  }

  function speakFrom(i){
    if(i >= paras.length){ stopAll(); return; }
    idx = i;
    paras.forEach(p => p.classList.remove('speaking'));
    const p = paras[idx];
    p.classList.add('speaking');
    p.scrollIntoView({behavior:'smooth', block:'center'});
    const u = new SpeechSynthesisUtterance(p.innerText);
    if(voice) u.voice = voice;
    u.lang = (voice && voice.lang) || 'zh-TW';
    u.rate = 0.92;          // 略慢，長輩好聽
    u.pitch = 1.0;
    u.onend = () => { if(playing && !paused) speakFrom(idx+1); };
    synth.speak(u);
  }

  function stopAll(){
    synth.cancel(); playing=false; paused=false;
    paras.forEach(p => p.classList.remove('speaking'));
    btn.querySelector('.txt').textContent = '▶ 朗讀本章';
    if(stopBtn) stopBtn.style.display='none';
  }

  const stopBtn = document.getElementById('btn-stop');

  btn.addEventListener('click', function(){
    if(!playing){
      playing=true; paused=false;
      if(stopBtn) stopBtn.style.display='inline-flex';
      btn.querySelector('.txt').textContent='⏸ 暫停';
      speakFrom(idx);
    } else if(!paused){
      paused=true; synth.pause();
      btn.querySelector('.txt').textContent='▶ 繼續';
    } else {
      paused=false; synth.resume();
      btn.querySelector('.txt').textContent='⏸ 暫停';
    }
  });
  if(stopBtn) stopBtn.addEventListener('click', stopAll);

  // 離開頁面時停止
  window.addEventListener('beforeunload', () => synth.cancel());
})();

/* ---------- 3. 手機漢堡選單 ---------- */
(function(){
  const nav = document.querySelector('.nav');
  const toggle = nav && nav.querySelector('.nav-toggle');
  if(!toggle) return;
  toggle.addEventListener('click', function(){
    const open = nav.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  // 點任一連結後自動收合
  nav.querySelectorAll('.links a').forEach(a => a.addEventListener('click', () => nav.classList.remove('open')));
})();
