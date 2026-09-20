window.GameFactory=(()=>{
  const p='gf_';
  const canonicalBase='https://gamefactorylab.github.io/gamefactorylab/';
  const dailyGames=[
    {id:'odd-one-out',title:'Odd One Out'},
    {id:'reaction-rush',title:'Reaction Rush'},
    {id:'sequence-snap',title:'Sequence Snap'},
    {id:'perfect-tap',title:'Perfect Tap'},
    {id:'flash-count',title:'Flash Count'},
    {id:'quick-sum',title:'Quick Sum'},
    {id:'memory-path',title:'Memory Path'},
    {id:'higher-lower',title:'Higher or Lower'}
  ];
  const games=[
    ...dailyGames,
    {id:'color-word-challenge',title:'Color Word Challenge'},
    {id:'number-hunt',title:'Number Hunt'},
    {id:'dot-compare',title:'Dot Compare'},
    {id:'five-second-sense',title:'Five Second Sense'},
    {id:'parity-rush',title:'Parity Rush'},
    {id:'one-back',title:'One Back'},
    {id:'direction-switch',title:'Direction Switch'},
    {id:'word-scramble-rush',title:'Word Scramble Rush'},
    {id:'maze-dash',title:'Maze Dash'},
    {id:'pair-flip',title:'Pair Flip'},
    {id:'grid-toggle',title:'Grid Toggle'},
    {id:'mini-sudoku-rush',title:'Mini Sudoku Rush'}
  ];

  function stats(id){try{return JSON.parse(localStorage.getItem(p+id)||'{}')}catch{return {}}}
  function save(id,s){localStorage.setItem(p+id,JSON.stringify(s))}
  function baseUrl(){return new URL(canonicalBase)}
  function gameUrl(id){return new URL(`games/${id}/`,baseUrl()).href}
  function today(){return new Date().toISOString().slice(0,10)}
  function validDay(day){return /^\d{4}-\d{2}-\d{2}$/.test(day||'')}
  function dayIndex(day){
    let h=2166136261;
    for(const c of day){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}
    return Math.abs(h>>>0)%dailyGames.length;
  }
  function dailyGame(day=today()){
    const safe=validDay(day)?day:today();
    return dailyGames[dayIndex(safe)];
  }
  function dailyUrl(day=today()){
    const safe=validDay(day)?day:today();
    const u=new URL(gameUrl(dailyGame(safe).id));
    u.searchParams.set('daily',safe);
    u.searchParams.set('from','daily');
    return u.href;
  }
  function dailyState(){try{return JSON.parse(localStorage.getItem(p+'daily')||'{}')}catch{return {}}}
  function saveDaily(s){localStorage.setItem(p+'daily',JSON.stringify(s))}
  function previousDay(day){
    const d=new Date(day+'T00:00:00Z');
    d.setUTCDate(d.getUTCDate()-1);
    return d.toISOString().slice(0,10);
  }
  function query(){return new URLSearchParams(location.search)}
  function dailyContext(id){
    const day=query().get('daily');
    return validDay(day)&&dailyGame(day).id===id?day:null;
  }
  function challengeTarget(){
    const raw=query().get('target');
    if(raw===null||raw==='')return null;
    const n=Number(raw);
    if(!Number.isFinite(n)||n<0||n>1000000)return null;
    return Math.round(n*1000)/1000;
  }
  function displayScore(id,n){
    if(id==='reaction-rush')return Math.max(1,1000-Math.round(n))+' ms';
    if(id==='five-second-sense')return Math.max(0,5000-Math.round(n))+' ms off';
    return String(Math.round(n*100)/100);
  }
  function challengeUrl(id,target){
    const u=new URL(gameUrl(id));
    const day=dailyContext(id);
    if(day)u.searchParams.set('daily',day);
    const value=target===undefined?stats(id).last:target;
    if(Number.isFinite(value))u.searchParams.set('target',String(Math.round(value*1000)/1000));
    u.searchParams.set('challenge','1');
    u.searchParams.set('from','share');
    return u.href;
  }
  function nextGame(id){
    const i=games.findIndex(g=>g.id===id);
    return games[(i<0?0:i+1)%games.length];
  }
  function ensureContext(id){
    if(!id||document.getElementById('gf-context'))return;
    const day=dailyContext(id);
    const shared=query().get('challenge')==='1';
    if(!day&&!shared)return;
    const wrap=document.createElement('section');
    wrap.id='gf-context';
    wrap.className='card gf-context';
    const label=document.createElement('div');
    label.className='gf-context-label muted';
    const title=document.createElement('strong');
    title.className='gf-context-title';
    const detail=document.createElement('div');
    detail.className='gf-context-detail muted';
    if(day){
      const ds=dailyState();
      label.textContent=day===today()?'Daily challenge':'Shared daily challenge';
      title.textContent=day===today()?'Today’s challenge':'Daily challenge from '+day;
      detail.textContent=day===today()&&ds.streak?`Current daily streak: ${ds.streak}`:'Finish the run, then challenge someone else.';
    }else{
      const target=challengeTarget();
      label.textContent='Friend challenge';
      title.textContent=target===null?'Beat the shared result':'Beat '+displayScore(id,target);
      detail.textContent=target===null?'Finish your run, then send your score back.':'Finish a run to see whether you beat your friend.';
    }
    wrap.append(label,title,detail);
    const main=document.querySelector('main.app')||document.body;
    const firstSection=main.querySelector(':scope > section');
    if(firstSection)main.insertBefore(wrap,firstSection);else main.prepend(wrap);
  }
  function refreshContext(id,completed=false){
    const wrap=document.getElementById('gf-context');
    const day=dailyContext(id);
    if(!wrap||!day)return;
    const title=wrap.querySelector('.gf-context-title');
    const detail=wrap.querySelector('.gf-context-detail');
    const ds=dailyState();
    if(completed&&day===today()){
      title.textContent='Daily challenge complete ✓';
      detail.textContent=`Daily streak: ${ds.streak||1} · Best: ${ds.bestStreak||ds.streak||1}`;
    }
  }
  function refreshChallenge(id,n){
    const wrap=document.getElementById('gf-context');
    const target=challengeTarget();
    if(!wrap||query().get('challenge')!=='1'||target===null)return;
    const title=wrap.querySelector('.gf-context-title');
    const detail=wrap.querySelector('.gf-context-detail');
    if(n>target){
      title.textContent='You beat the challenge ✓';
      detail.textContent=`Your result: ${displayScore(id,n)} · Friend: ${displayScore(id,target)}. Share it back.`;
    }else if(n===target){
      title.textContent='Tie challenge';
      detail.textContent=`Both results: ${displayScore(id,n)}. One more run decides it.`;
    }else{
      title.textContent='Challenge still alive';
      detail.textContent=`Your result: ${displayScore(id,n)} · Target: ${displayScore(id,target)}. Try again.`;
    }
  }
  function completeDaily(id){
    const day=dailyContext(id);
    if(!day||day!==today())return;
    const ds=dailyState();
    if(ds.lastCompleted!==day){
      ds.streak=ds.lastCompleted===previousDay(day)?(ds.streak||0)+1:1;
      ds.lastCompleted=day;
      ds.bestStreak=Math.max(ds.bestStreak||0,ds.streak);
      ds.completions=(ds.completions||0)+1;
      saveDaily(ds);
    }
    refreshContext(id,true);
  }
  function ensureNext(id){
    if(!id||document.getElementById('gf-next-challenge'))return;
    const next=nextGame(id);
    const wrap=document.createElement('section');
    wrap.id='gf-next-challenge';
    wrap.className='card gf-next';
    wrap.hidden=true;
    const label=document.createElement('div');
    label.className='gf-next-label muted';
    label.textContent='Keep the streak going';
    const title=document.createElement('strong');
    title.className='gf-next-title';
    title.textContent='Next challenge: '+next.title;
    const actions=document.createElement('div');
    actions.className='gf-next-actions';
    const play=document.createElement('a');
    play.className='btn primary gf-next-play';
    play.href=gameUrl(next.id)+`?from=${encodeURIComponent(id)}`;
    play.textContent='Play next →';
    play.addEventListener('click',()=>event(id,'next_click'));
    const daily=document.createElement('a');
    daily.className='btn secondary gf-next-daily';
    daily.href=dailyUrl();
    daily.textContent='Daily challenge';
    daily.addEventListener('click',()=>event(id,'daily_click'));
    actions.append(play,daily);
    wrap.append(label,title,actions);
    (document.querySelector('main.app')||document.body).appendChild(wrap);
  }
  function showNext(id){
    ensureNext(id);
    const wrap=document.getElementById('gf-next-challenge');
    if(wrap)wrap.hidden=false;
  }
  function hideNext(){
    const wrap=document.getElementById('gf-next-challenge');
    if(wrap)wrap.hidden=true;
  }
  function open(id){
    const s=stats(id);
    s.sessions=(s.sessions||0)+1;
    s.firstSeen=s.firstSeen||Date.now();
    s.lastSeen=Date.now();
    const q=query();
    const from=q.get('from');
    if(from){
      s.referrals=s.referrals||{};
      s.referrals[from]=(s.referrals[from]||0)+1;
    }
    if(q.get('challenge')==='1'){
      s.events=s.events||{};
      s.events.challenge_open=(s.events.challenge_open||0)+1;
    }
    if(dailyContext(id)){
      s.events=s.events||{};
      s.events.daily_open=(s.events.daily_open||0)+1;
    }
    save(id,s);
    const init=()=>{ensureContext(id);ensureNext(id)};
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
  }
  function score(id,n){
    const s=stats(id);
    s.plays=(s.plays||0)+1;
    s.best=Math.max(s.best||0,n);
    s.last=n;
    s.lastSeen=Date.now();
    const target=challengeTarget();
    if(query().get('challenge')==='1'&&target!==null){
      s.events=s.events||{};
      const outcome=n>target?'challenge_win':n===target?'challenge_tie':'challenge_loss';
      s.events[outcome]=(s.events[outcome]||0)+1;
    }
    save(id,s);
    refreshChallenge(id,n);
    return s;
  }
  function event(id,name){
    const s=stats(id);
    s.events=s.events||{};
    s.events[name]=(s.events[name]||0)+1;
    save(id,s);
    if(name==='start')hideNext();
    if(name==='finish'){
      completeDaily(id);
      showNext(id);
    }
  }
  function manualShare(title,text,target){
    let wrap=document.getElementById('gf-manual-share');
    if(!wrap){
      wrap=document.createElement('section');
      wrap.id='gf-manual-share';
      wrap.className='card gf-context';
      const label=document.createElement('strong');
      label.textContent='Share your challenge';
      const box=document.createElement('textarea');
      box.id='gf-manual-share-text';
      box.readOnly=true;
      box.style.width='100%';
      box.style.minHeight='92px';
      box.style.marginTop='8px';
      box.style.borderRadius='10px';
      box.style.padding='10px';
      box.style.background='#0b1220';
      box.style.color='#f8fafc';
      box.style.border='1px solid rgba(255,255,255,.12)';
      wrap.append(label,box);
      (document.querySelector('main.app')||document.body).appendChild(wrap);
    }
    const box=wrap.querySelector('#gf-manual-share-text');
    box.value=`${text} ${target}`;
    box.focus();
    box.select();
  }
  async function share(id,title,text,url){
    event(id,'share_attempt');
    const target=url||challengeUrl(id);
    if(navigator.share){
      try{
        await navigator.share({title,text,url:target});
        event(id,'share_success');
        return 'shared';
      }catch(e){
        if(e&&e.name==='AbortError')return 'cancelled';
      }
    }
    if(navigator.clipboard?.writeText){
      try{
        await navigator.clipboard.writeText(text+' '+target);
        event(id,'share_copy');
        return 'copied';
      }catch(e){}
    }
    manualShare(title,text,target);
    event(id,'share_manual');
    return 'manual';
  }
  return{open,score,event,share,stats,dailyGame,dailyUrl,challengeUrl};
})();