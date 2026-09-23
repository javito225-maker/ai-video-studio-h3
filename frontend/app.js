const $=s=>document.querySelector(s);
$("#health").onclick=async()=>{ $("#status").textContent="Vérification...";
 const r=await fetch("/api/health"); const d=await r.json();
 $("#status").textContent=`ComfyUI: ${d.comfyui.online?"EN LIGNE":"HORS LIGNE"} · Ollama: ${d.ollama.online?"EN LIGNE":"HORS LIGNE"}`;
};
$("#plan").onclick=async()=>{const story=$("#story").value.trim();if(!story)return alert("Entre une histoire.");
 $("#sequences").textContent="Llama prépare les séquences...";
 try{const r=await fetch("/api/plan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({story})});
 const d=await r.json(); const seq=d.sequences||d;
 $("#sequences").innerHTML=(Array.isArray(seq)?seq:[]).map((s,i)=>`<article><b>Séquence ${i+1} — ${s.title||""}</b><p>${s.prompt||""}</p><small>${s.duration||15}s · ${s.camera||""}</small></article>`).join("")||"<pre>"+JSON.stringify(d,null,2)+"</pre>";
 }catch(e){$("#sequences").textContent="Erreur: "+e.message;}
};
