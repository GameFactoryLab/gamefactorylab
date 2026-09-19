window.GameFactory=(()=>{
  const p='gf_';
  const canonicalBase='https://gamefactorylab.github.io/gamefactorylab/';
  const games=[
    {id:'odd-one-out',title:'Odd One Out'},
    {id:'reaction-rush',title:'Reaction Rush'},
    {id:'sequence-snap',title:'Sequence Snap'},
    {id:'perfect-tap',title:'Perfect Tap'},
    {id:'flash-count',title:'Flash Count'},
    {id:'quick-sum',title:'Quick Sum'},
    {id:'memory-path',title:'Memory Path'},
    {id:'higher-lower',title:'Higher or Lower'}
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
    return Math.abs(h>>>0)%games.length;
  }
  function dailyGame(day=today()){
    const safe=validDay(day)?day:today();
    return games[dayIndex(safe)];
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
  function challengeUrl(id){
    const u=new URL(gameUrl(id));
    const day=dailyContext(id);
    if(day)u.searchParams.set('daily',day);
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
      label.textContent='Friend challenge';
      title.textContent='Beat the shared result';
      detail.textContent='Finish your run, then send your score back.';
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
    save(id,s);
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
    event(id,'share_unsupported');
    return 'unsupported';
  }
  return{open,score,event,share,stats,dailyGame,dailyUrl,challengeUrl};
})();
