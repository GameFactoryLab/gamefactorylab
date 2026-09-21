window.GameFactoryLabs=(()=>{
  'use strict';

  const candidates=[
    {id:'circuit-flow',title:'Circuit Flow',key:'gf_candidate_circuit_flow_v1',total:30},
    {id:'route-once',title:'Route Once',key:'gf_candidate_route_once_v1',total:16},
    {id:'pixel-logic',title:'Pixel Logic',key:'gf_candidate_pixel_logic_v1',total:12},
    {id:'orbit-align',title:'Orbit Align',key:'gf_candidate_orbit_align_v1',total:20},
    {id:'sum-vault',title:'Sum Vault',key:'gf_candidate_sum_vault_v1',total:null},
    {id:'cluster-collapse',title:'Cluster Collapse',key:'gf_candidate_cluster_collapse_v1',total:null},
    {id:'balance-drop',title:'Balance Drop',key:'gf_candidate_balance_drop_v1',total:null},
    {id:'pulse-cascade',title:'Pulse Cascade',key:'gf_candidate_pulse_cascade_v1',total:20},
    {id:'cipher-sprint',title:'Cipher Sprint',key:'gf_candidate_cipher_sprint_v1',total:null},
    {id:'rule-shift',title:'Rule Shift',key:'gf_candidate_rule_shift_v1',total:null},
    {id:'vector-drift',title:'Vector Drift',key:'gf_candidate_vector_drift_v1',total:null}
  ];

  function read(key){
    try{return JSON.parse(localStorage.getItem(key)||'{}')}catch{return {}}
  }

  function metric(state,name){
    const value=Number(state?.metrics?.[name]||0);
    return Number.isFinite(value)&&value>0?value:0;
  }

  function progress(meta,state){
    const bestLevel=Number(state.bestLevel||0);
    const unlocked=Number(state.unlocked||0);
    if(meta.total){
      const level=Math.max(bestLevel,unlocked>0?unlocked-1:0);
      return Math.max(0,Math.min(1,level/meta.total));
    }
    const bestScore=Number(state.bestScore||0);
    if(bestScore>0)return Math.max(0,Math.min(1,Math.log1p(bestScore)/Math.log1p(2000)));
    return 0;
  }

  function scored(meta){
    const state=read(meta.key);
    const m=state.metrics||{};
    const clears=metric(state,'level_clear')||metric(state,'run_finish')||metric(state,'result_clear');
    const replays=metric(state,'replay_click');
    const shares=metric(state,'result_share_click');
    const next=metric(state,'next_level');
    const activity=Object.values(m).reduce((sum,value)=>{
      const n=Number(value||0);
      return sum+(Number.isFinite(n)&&n>0?n:0);
    },0);
    const p=progress(meta,state);
    const clearDepth=Math.min(1,clears/3);
    const replayRate=Math.min(1,replays/Math.max(1,clears));
    const shareRate=Math.min(1,shares/Math.max(1,clears));
    const activityDepth=Math.min(1,activity/30);
    const score=Math.round(100*(p*.35+clearDepth*.25+replayRate*.20+shareRate*.15+activityDepth*.05));
    const evidence=clears+replays+shares+Math.min(next,2);
    return {...meta,state,score,evidence,clears,replays,shares,next,activity,progress:p};
  }

  function board(){
    return candidates.map(scored).sort((a,b)=>b.score-a.score||b.evidence-a.evidence||a.title.localeCompare(b.title));
  }

  function winner(){
    const rows=board(),top=rows[0],second=rows[1];
    if(!top||top.clears<1||top.evidence<3||top.score<30)return null;
    if(second&&top.score-second.score<8&&top.evidence<5)return null;
    return top;
  }

  function url(id,source,base='../release-candidates/'){
    return `${base}${id}/?from=${encodeURIComponent(source)}`;
  }

  return{candidates,board,winner,url};
})();