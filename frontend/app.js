const API_BASE_URL = "https://resume-analyzer-v2-production.up.railway.app"; // Change to Render URL after deployment
const UPLOAD_URL = `${API_BASE_URL}/upload`;
const RESULTS_URL = `${API_BASE_URL}/results`;

function getScoreColor(score){if(score>=80)return"#16a34a";if(score>=60)return"#f59e0b";return"#dc2626"}
function scoreLabel(score){if(score>=85)return"Excellent";if(score>=70)return"Strong";if(score>=55)return"Average";return"Needs Work"}
function renderTags(items,type=""){if(!items||items.length===0)return`<p class="empty">None</p>`;return`<div class="tags">${items.map(i=>`<span class="tag ${type}">${i}</span>`).join("")}</div>`}
function renderSuggestions(items){if(!items||items.length===0)return`<p class="empty">No suggestions available.</p>`;return`<ul class="suggestionList">${items.map(i=>`<li>⚠️ ${i}</li>`).join("")}</ul>`}
function barRow(label,score,color){score=score??0;return`<div class="barRow"><strong>${label}</strong><div class="barTrack"><div class="barFill" style="width:${score}%;background:${color};"></div></div><div class="barScore" style="color:${color};">${score}/100</div></div>`}
function normalize(data){const ai=data.ai_analysis||{};return{final:data.final_score??0,keyword:data.match_percent??0,category:data.category_score??0,ai:ai.score??data.ai_score??0,summary:ai.summary||data.summary||"No summary available.",suggestions:ai.suggestions||data.suggestions||[],matched:data.matched_skills||[],missing:data.missing_skills||[],cats:data.matched_categories||[],skills:data.resume_skills||[],filename:data.filename||localStorage.getItem("last_file_name")||"Uploaded resume",provider:data.provider||document.getElementById("provider")?.value||"gemini"}}

function renderResult(data){
  const r=normalize(data), result=document.getElementById("result");
  result.className="";
  result.innerHTML=`
    <div class="metaStrip">
      <div class="metaItem"><strong>Resume:</strong> ${r.filename}</div>
      <div class="metaItem"><strong>Provider:</strong> ${r.provider}</div>
      <div class="metaItem"><strong>Status:</strong> ✅ Analysis Complete</div>
    </div>
    <div class="resultTop">
      <div class="scoreGauge">
        <h2>Resume Score</h2><div class="gauge"></div>
        <div class="gaugeScore" style="color:${getScoreColor(r.final)}">${r.final}<span>/100</span></div>
        <div class="scoreLabel">${scoreLabel(r.final)} Overall Score</div>
        <div class="note">☆ ${r.final>=70?"Your resume is strong and optimized.":"Your resume needs improvement for this role."}</div>
      </div>
      <div class="scoreBars">
        <h2>Score by Category</h2>
        ${barRow("Keyword Match",r.keyword,"#2563eb")}
        ${barRow("Category Score",r.category,"#16a34a")}
        ${barRow("AI Score",r.ai,"#7c3aed")}
        ${barRow("Final Score",r.final,getScoreColor(r.final))}
      </div>
    </div>
    <div class="feedbackGrid">
      <div class="feedbackCard"><h2>AI Response</h2><p>${r.summary}</p><div class="note"><strong>Recommendation:</strong> ${scoreLabel(r.final)} Candidate</div></div>
      <div class="feedbackCard"><h2>Top Suggestions</h2>${renderSuggestions(r.suggestions)}</div>
      <div class="feedbackCard"><h2>Matched Skills</h2>${renderTags(r.matched)}<h2 style="margin-top:24px">Missing Skills</h2>${renderTags(r.missing,"missing")}</div>
    </div>
    <div class="feedbackGrid">
      <div class="feedbackCard"><h2>Matched Categories</h2>${renderTags(r.cats,"category")}</div>
      <div class="feedbackCard"><h2>Resume Skills Detected</h2>${renderTags(r.skills)}</div>
      <div class="feedbackCard"><h2>Actions</h2><p>Saved analysis can be downloaded from History page.</p><a href="history.html" class="primary">Open History</a></div>
    </div>`;
}

async function handleAnalyze(){
  const file=document.getElementById("resumeFile").files[0], job=document.getElementById("jobDescription").value, provider=document.getElementById("provider").value;
  if(!file){
    alert("Please upload a PDF resume first.");
    return}
  localStorage.setItem("last_file_name",file.name);
  localStorage.setItem("last_job_description",job);
  localStorage.setItem("last_provider",provider);
  const fd=new FormData();
  fd.append("file",file);
  fd.append("job_description",job);
  fd.append("provider",provider);
  const btn=document.getElementById("analyzeBtn"), loading=document.getElementById("loading");
  loading.style.display="block";
  btn.disabled=true;
  btn.textContent="Analyzing...";
  try{
    const res=await fetch(UPLOAD_URL,{method:"POST",body:fd});
    const data=await res.json();
  if(!res.ok)
    throw new Error(data.detail||data.error||"Something went wrong");
  localStorage.setItem("last_analysis_result",JSON.stringify(data));
  window.location.href="result.html"}
  catch(e){
    const result=document.getElementById("result");result.className="placeholder";
    result.innerHTML=`Error: ${e.message}`}
  finally{
    loading.style.display="none";
    btn.disabled=false;
    btn.textContent="Analyze Resume"}
}
function clearSession(){
  ["last_analysis_result","last_file_name","last_job_description","last_provider"].forEach(k=>localStorage.removeItem(k));location.href="index.html"}

async function loadHistory(){
  const box=document.getElementById("historyList");
  if(!box)
    return;
  box.innerHTML=`<div class="card">Loading history...</div>`;
  try{
    const res=await fetch(RESULTS_URL);
    const data=await res.json();
    if(!data.length){
      box.innerHTML=`<div class="card empty">No history found.</div>`;
      return}
  box.innerHTML=data.map(item=>`<div class="historyCard"><h3 onclick="loadAnalysisDetail(${item.id})">${item.filename}</h3><p><strong>Provider:</strong> ${item.provider}</p><p><strong>Final Score:</strong> ${item.final_score??0}/100</p><p><strong>Keyword Match:</strong> ${item.match_percent??0}%</p><p><strong>AI Score:</strong> ${item.ai_score??0}/100</p><p><strong>Summary:</strong> ${item.summary||"No summary available."}</p><a href="${RESULTS_URL}/${item.id}/pdf" target="_blank" class="pdfBtn">Download PDF Report</a><br><br><small>${item.created_at||""}</small></div>`).join("")}
  catch(e){
    box.innerHTML=`<div class="card">Error loading history: ${e.message}</div>`}
}
async function loadAnalysisDetail(id){
  const modal=document.getElementById("modal"), body=document.getElementById("modalBody");
  if(!modal||!body)
    return;
  modal.style.display="block";
  body.innerHTML="Loading analysis...";
  try{
    const res=await fetch(`${RESULTS_URL}/${id}`);
    const data=await res.json();
    const r=normalize(data);
    body.innerHTML=`<h2>${r.filename}</h2><div class="resultTop"><div class="scoreGauge"><h2>Resume Score</h2><div class="gauge"></div><div class="gaugeScore" style="color:${getScoreColor(r.final)}">${r.final}<span>/100</span></div><div class="scoreLabel">${scoreLabel(r.final)} Overall Score</div></div><div class="scoreBars"><h2>Score by Category</h2>${barRow("Keyword Match",r.keyword,"#2563eb")}${barRow("Category Score",r.category,"#16a34a")}${barRow("AI Score",r.ai,"#7c3aed")}${barRow("Final Score",r.final,getScoreColor(r.final))}</div></div><div class="feedbackGrid"><div class="feedbackCard"><h2>Summary</h2><p>${r.summary}</p></div><div class="feedbackCard"><h2>Suggestions</h2>${renderSuggestions(r.suggestions)}</div><div class="feedbackCard"><h2>Skills</h2><h3>Matched</h3>${renderTags(r.matched)}<h3>Missing</h3>${renderTags(r.missing,"missing")}</div></div><a href="${RESULTS_URL}/${id}/pdf" target="_blank" class="pdfBtn">Download PDF Report</a>`}
  catch(e){
    body.innerHTML=`Error loading analysis: ${e.message}`}
}
function init(){
  const analyze=document.getElementById("analyzeBtn"), clear=document.getElementById("clearBtn"), refresh=document.getElementById("refreshHistoryBtn"), file=document.getElementById("resumeFile"), fileText=document.getElementById("fileNameText"), job=document.getElementById("jobDescription"), provider=document.getElementById("provider"), close=document.getElementById("closeModal");
  if(analyze)analyze.onclick=handleAnalyze;if(clear)clear.onclick=clearSession;if(refresh)refresh.onclick=loadHistory;
  if(file&&fileText)file.onchange=()=>{if(file.files[0])fileText.textContent=`Selected File: ${file.files[0].name}`};
  if(localStorage.getItem("last_file_name")&&fileText)fileText.textContent=`Last Selected File: ${localStorage.getItem("last_file_name")}`;
  if(localStorage.getItem("last_job_description")&&job)job.value=localStorage.getItem("last_job_description");
  if(localStorage.getItem("last_provider")&&provider)provider.value=localStorage.getItem("last_provider");
  if(localStorage.getItem("last_analysis_result")&&document.getElementById("result"))renderResult(JSON.parse(localStorage.getItem("last_analysis_result")));
  if(document.getElementById("historyList"))loadHistory();
  if(close)close.onclick=()=>document.getElementById("modal").style.display="none";
  window.onclick=e=>{const m=document.getElementById("modal");if(e.target===m)m.style.display="none"}
}
document.addEventListener("DOMContentLoaded",init);