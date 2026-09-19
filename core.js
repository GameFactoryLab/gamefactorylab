window.GameFactory=(()=>{
  const p='gf_';
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
  function baseUrl(){return new URL('../../',location.href)}
  function nextGame(id){
    const i=games.findIndex(g=>g.id===id);
    return games[(i<0?0:i+1)%games.length];
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
    play.href=new URL(`games/${next.id}/?from=${encodeURIComponent(id)}`,baseUrl()).href;
    play.textContent='Play next →';
    play.addEventListener('click',()=>event(id,'next_click'));
    const all=document.createElement('a');
    all.className='btn secondary gf-next-all';
    all.href=new URL('./',baseUrl()).href;
    all.textContent='All games';
    all.addEventListener('click',()=>event(id,'all_games_click'));
    actions.append(play,all);
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
    const from=new URLSearchParams(location.search).get('from');
    if(from){
      s.referrals=s.referrals||{};
      s.referrals[from]=(s.referrals[from]||0)+1;
    }
    save(id,s);
    if(document.readyState==='loading'){
      document.addEventListener('DOMContentLoaded',()=>ensureNext(id),{once:true});
    }else ensureNext(id);
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
    if(name==='finish')showNext(id);
  }
  async function share(id,title,text,url=location.href){
    event(id,'share_attempt');
    if(navigator.share){
      try{
        await navigator.share({title,text,url});
        event(id,'share_success');
        return 'shared';
      }catch(e){
        if(e && e.name==='AbortError') return 'cancelled';
      }
    }
    if(navigator.clipboard?.writeText){
      try{
        await navigator.clipboard.writeText(text+' '+url);
        event(id,'share_copy');
        return 'copied';
      }catch(e){}
    }
    event(id,'share_unsupported');
    return 'unsupported';
  }
  return{open,score,event,share,stats};
})();
