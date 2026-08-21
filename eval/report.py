"""Sinh report.html TĨNH (1 file, mở bằng double-click, không cần server/mạng).

Đọc results.jsonl + verdicts.jsonl + labels.csv, nhúng toàn bộ dữ liệu vào HTML.
Nhãn pass/fail/uncertain KÈM NOTE NGẮN bấm/nhập trong report, lưu vào localStorage
của trình duyệt (dạng {label, note}; đọc được cả bản cũ lưu string thuần);
nút "Export labels.csv" tải về CSV 3 cột scenario_id,label,note để đưa lại cho
judge.py so agreement.
"""
import csv, json, os

def read_jsonl(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]

def read_labels(path="labels.csv"):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return {r["scenario_id"]: r.get("label", "").strip()
                for r in csv.DictReader(f) if r.get("scenario_id")}

def main():
    results = read_jsonl("results.jsonl")
    verdicts = {v["scenario_id"]: v for v in read_jsonl("verdicts.jsonl")}
    labels = read_labels()
    if not results:
        print("Chưa có results.jsonl — report sẽ trống. Chạy python3 eval/run_eval.py trước.")
    # Gộp 3 nguồn thành 1 list row để nhúng vào HTML
    rows = []
    for r in results:
        sid = r.get("scenario_id", "?")
        rows.append({"scenario_id": sid, "input": r.get("input", ""),
                     "slide": r.get("slide"),
                     "output": r.get("output"), "error": r.get("error"),
                     "raw_content": r.get("raw_content", ""),
                     "latency_s": r.get("latency_s"), "cost_usd": r.get("cost_usd"),
                     "verdict": verdicts.get(sid, {}).get("verdict"),
                     "rationale": verdicts.get(sid, {}).get("rationale", ""),
                     "human_label": labels.get(sid, "")})
    html = TEMPLATE.replace("__DATA__", json.dumps(rows, ensure_ascii=False))
    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Đã sinh report.html (%d dòng dữ liệu). Mở bằng: open report.html" % len(rows))

# Giao diện: mọi logic render/lọc/gán nhãn chạy hoàn toàn trong trình duyệt.
TEMPLATE = """<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Eval Report — AI Tutor</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --primary: #4f46e5;
  --primary-hover: #4338ca;
  --bg: #f8fafc;
  --surface: #ffffff;
  --border: #e2e8f0;
  --text: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --success: #10b981;
  --success-bg: #d1fae5;
  --danger: #ef4444;
  --danger-bg: #fee2e2;
  --warning: #f59e0b;
  --warning-bg: #fef3c7;
  --shadow: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
  --radius: 12px;
  --radius-sm: 8px;
}
* { box-sizing: border-box; }
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  margin: 0;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}
header {
  position: sticky;
  top: 0;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  padding: 16px 24px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
  z-index: 100;
}
h1 {
  font-size: 18px;
  font-weight: 700;
  margin: 0 16px 0 0;
  background: linear-gradient(135deg, var(--primary), #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.toolbar {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
select, button {
  font-size: 13px;
  font-weight: 500;
  padding: 8px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: var(--surface);
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text);
}
select:hover, button:hover {
  border-color: var(--primary);
  box-shadow: var(--shadow);
}
button.primary {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}
button.primary:hover {
  background: var(--primary-hover);
}
.stat {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
  margin-left: auto;
}
main {
  max-width: 900px;
  margin: 24px auto;
  padding: 0 20px;
}
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: var(--shadow);
  transition: box-shadow 0.2s;
}
.card:hover {
  box-shadow: var(--shadow-lg);
}
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 12px;
  align-items: center;
}
.meta-tag {
  background: #f1f5f9;
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.slide-context {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #eef2ff;
  color: var(--primary);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}
.slide-context::before {
  content: "📄";
  font-size: 12px;
}
.q {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 12px;
  line-height: 1.5;
}
.answer {
  font-size: 14px;
  color: var(--text);
  line-height: 1.7;
  margin-bottom: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--primary);
}
.sources {
  margin: 12px 0;
}
.source-item {
  font-size: 13px;
  background: #f8fafc;
  border-left: 3px solid #94a3b8;
  padding: 8px 12px;
  margin: 6px 0;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  color: var(--text-secondary);
}
.source-item code {
  color: var(--primary);
  font-weight: 600;
  font-size: 12px;
}
.followup {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}
.followup-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}
.followup-item {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 4px 0 4px 16px;
  position: relative;
}
.followup-item::before {
  content: "→";
  position: absolute;
  left: -16px;
  color: var(--primary);
}
.badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.badge.pass { background: var(--success-bg); color: #065f46; }
.badge.fail { background: var(--danger-bg); color: #991b1b; }
.badge.uncertain { background: var(--warning-bg); color: #92400e; }
.badge.pending {
  background: #f1f5f9;
  color: var(--text-muted);
}
.error-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--danger-bg);
  color: #991b1b;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 8px;
}
.error-detail {
  font-size: 12px;
  color: #991b1b;
  font-family: 'SF Mono', Monaco, monospace;
  background: #fef2f2;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
  margin-top: 8px;
}
.verdict-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
  flex-wrap: wrap;
}
.verdict-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}
.label-buttons {
  display: flex;
  gap: 6px;
}
.label-buttons button {
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-secondary);
  transition: all 0.2s;
}
.label-buttons button:hover {
  border-color: var(--primary);
  color: var(--primary);
}
.label-buttons button.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}
.note-input {
  font-size: 13px;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  width: 280px;
  transition: border-color 0.2s;
}
.note-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}
.raw-toggle {
  font-size: 12px;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}
.raw-toggle:hover {
  background: #f1f5f9;
  color: var(--text);
}
.raw-content {
  display: none;
  margin-top: 12px;
  padding: 16px;
  background: #1e293b;
  color: #e2e8f0;
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 12px;
  line-height: 1.6;
  border-radius: var(--radius-sm);
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}
.rat {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 8px;
  font-style: italic;
}
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-muted);
}
.empty-state h3 {
  font-size: 16px;
  margin-bottom: 8px;
  color: var(--text-secondary);
}
@media (max-width: 640px) {
  header { padding: 12px 16px; }
  main { padding: 0 12px; margin: 16px auto; }
  .card { padding: 16px; }
  .note-input { width: 100%; }
}
</style></head><body>
<header>
  <h1>Eval Report — AI Tutor</h1>
  <div class="toolbar">
    <select id="flt">
      <option value="">Tất cả</option>
      <option>pass</option>
      <option>fail</option>
      <option>uncertain</option>
      <option value="none">(chưa chấm)</option>
    </select>
    <button class="primary" onclick="exportCsv()">Export labels.csv</button>
    <span class="stat" id="stat"></span>
  </div>
</header>
<main id="list"></main>
<script>
var ROWS=__DATA__, KEY="evalkit-labels";
var saved={};try{saved=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){}
function norm(v){return typeof v=="string"?{label:v,note:""}:(v||{label:"",note:""})}
function cur(sid,human){var s=saved[sid];return s?norm(s):{label:human||"",note:""}}
function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
function badge(v){
  if(!v) return '<span class="badge pending">chưa chấm</span>';
  var cls = v==='pass'?'pass':v==='fail'?'fail':'uncertain';
  return '<span class="badge '+cls+'">'+v+'</span>';
}
function render(){
  var f=document.getElementById("flt").value;
  var el=document.getElementById("list");
  var h="",n=0;
  ROWS.forEach(function(r,i){
    if(f){
      if(f==="none" && r.verdict) return;
      if(f!=="none" && r.verdict!==f) return;
    }
    n++;
    var o=r.output||{};
    var c=cur(r.scenario_id,r.human_label);
    var lbl=c.label;
    var metaTags = [];
    metaTags.push('<span class="meta-tag">'+esc(r.scenario_id)+'</span>');
    if(o.scope) metaTags.push('<span class="meta-tag">'+esc(o.scope)+'</span>');
    if(r.latency_s!=null) metaTags.push('<span class="meta-tag">'+r.latency_s+'s</span>');
    if(r.cost_usd!=null) metaTags.push('<span class="meta-tag">~$'+r.cost_usd+'</span>');
    h+='<div class="card">';
    h+='<div class="meta">'+metaTags.join('')+'</div>';
    if(r.slide){
      h+='<div class="slide-context">Slide '+esc(r.slide.id)+' — '+esc(r.slide.title);
      if(r.slide.keyword) h+=' <span style="opacity:0.7">· '+esc(r.slide.keyword)+'</span>';
      h+='</div>';
    }
    h+='<div class="q">'+esc(r.input)+'</div>';
    if(r.error){
      h+='<div class="error-badge">⚠ lỗi chạy</div>';
      h+='<div class="error-detail">'+esc(r.error)+'</div>';
    } else {
      h+='<div class="answer">'+esc(o.answer||"(không parse được answer)")+'</div>';
      if(o.sources && o.sources.length){
        h+='<div class="sources">';
        o.sources.forEach(function(s){
          h+='<div class="source-item"><code>'+esc(s.doc_id)+'#'+esc(s.section_id)+'</code> — "'+esc(s.quote)+'"</div>';
        });
        h+='</div>';
      }
      if(o.followup_questions && o.followup_questions.length){
        h+='<div class="followup"><div class="followup-title">Gợi ý hỏi tiếp</div>';
        o.followup_questions.forEach(function(q){
          h+='<div class="followup-item">'+esc(q)+'</div>';
        });
        h+='</div>';
      }
    }
    h+='<div class="verdict-row">';
    h+='<span class="verdict-label">Nhãn người:</span>';
    h+='<div class="label-buttons">';
    ["pass","fail","uncertain"].forEach(function(v){
      var active = lbl===v ? 'active' : '';
      h+='<button data-i="'+i+'" data-v="'+v+'" class="'+active+'" onclick="setLabel(this)">'+v+'</button>';
    });
    h+='</div>';
    h+='<input type="text" class="note-input" data-i="'+i+'" placeholder="note ngắn (vd: fail vì citation)" value="'+esc(c.note)+'" onchange="setNote(this)">';
    h+='<button class="raw-toggle" data-i="'+i+'" onclick="raw(this)">xem raw</button>';
    h+='</div>';
    if(r.verdict || r.rationale){
      h+='<div style="margin-top:8px">'+badge(r.verdict);
      if(r.rationale) h+=' <span class="rat">'+esc(r.rationale)+'</span>';
      h+='</div>';
    }
    h+='<div class="raw">'+esc(r.raw_content||JSON.stringify(o,null,2))+'</div>';
    h+='</div>';
  });
  if(!h) h='<div class="empty-state"><h3>Không có dòng nào khớp bộ lọc</h3><p>Thử đổi bộ lọc ở trên</p></div>';
  el.innerHTML=h;
  document.getElementById("stat").textContent=n+"/"+ROWS.length+" dòng";
}
function setLabel(b){
  var r=ROWS[b.dataset.i];
  var c=cur(r.scenario_id,r.human_label);
  if(c.label===b.dataset.v){
    if(c.note) saved[r.scenario_id]={label:"",note:c.note};
    else delete saved[r.scenario_id];
  } else {
    saved[r.scenario_id]={label:b.dataset.v,note:c.note};
  }
  localStorage.setItem(KEY,JSON.stringify(saved));
  render();
}
function setNote(inp){
  var r=ROWS[inp.dataset.i];
  var c=cur(r.scenario_id,r.human_label);
  var n=inp.value.trim();
  if(!n&&!c.label) delete saved[r.scenario_id];
  else saved[r.scenario_id]={label:c.label,note:n};
  localStorage.setItem(KEY,JSON.stringify(saved));
}
function raw(b){
  var d=b.closest(".card").querySelector(".raw");
  d.style.display=d.style.display==="block"?"none":"block";
}
function exportCsv(){
  var s="scenario_id,label,note\\n";
  function q(x){return '"'+String(x==null?"":x).replace(/"/g,'""')+'"'}
  ROWS.forEach(function(r){
    var c=cur(r.scenario_id,r.human_label);
    s+=q(r.scenario_id)+","+q(c.label)+","+q(c.note)+"\\n";
  });
  var a=document.createElement("a");
  a.href=URL.createObjectURL(new Blob([s],{type:"text/csv"}));
  a.download="labels.csv";
  a.click();
}
document.getElementById("flt").onchange=render;
render();
</script></body></html>"""

if __name__ == "__main__":
    main()
