const secure = {
  apiVersion: "apps/v1", kind: "Deployment", metadata: {name: "secure-api"},
  spec: {template: {spec: {automountServiceAccountToken: false,
    securityContext: {runAsNonRoot: true, seccompProfile: {type: "RuntimeDefault"}},
    containers: [{name: "api", image: "nginx:1.27.4-alpine",
      securityContext: {allowPrivilegeEscalation: false, readOnlyRootFilesystem: true, capabilities: {drop: ["ALL"]}},
      resources: {requests: {cpu: "50m", memory: "64Mi"}, limits: {cpu: "200m", memory: "128Mi"}}}]}}}
};
const insecure = {apiVersion:"apps/v1",kind:"Deployment",metadata:{name:"unsafe-api"},spec:{template:{spec:{containers:[{name:"api",image:"nginx:latest",securityContext:{privileged:true}}]}}}};
const input = document.querySelector("#manifest");
const results = document.querySelector("#results");
const load = value => { input.value = JSON.stringify(value, null, 2); results.className="results"; results.textContent="Ready to analyze."; };
document.querySelector("#secureExample").onclick = () => load(secure);
document.querySelector("#insecureExample").onclick = () => load(insecure);
document.querySelector("#analyze").onclick = () => {
  let w; try { w=JSON.parse(input.value); } catch(e) { results.className="results fail"; results.textContent=`Invalid JSON: ${e.message}`; return; }
  const pod=w?.spec?.template?.spec||{}, findings=[], podSC=pod.securityContext||{};
  if(pod.automountServiceAccountToken!==false) findings.push("K8S-001 Disable service-account token automount");
  if(podSC.runAsNonRoot!==true) findings.push("K8S-002 Require non-root execution");
  if(podSC.seccompProfile?.type!=="RuntimeDefault") findings.push("K8S-003 Use RuntimeDefault seccomp");
  if(!pod.containers?.length) findings.push("K8S-004 Define at least one container");
  (pod.containers||[]).forEach(c=>{ const n=c.name||"unnamed",sc=c.securityContext||{},r=c.resources||{};
    if(!c.image||c.image.endsWith(":latest")||!c.image.includes(":")) findings.push(`K8S-005 ${n}: use an explicit non-latest image tag`);
    if(sc.allowPrivilegeEscalation!==false) findings.push(`K8S-006 ${n}: disable privilege escalation`);
    if(sc.readOnlyRootFilesystem!==true) findings.push(`K8S-007 ${n}: use a read-only root filesystem`);
    if(!sc.capabilities?.drop?.includes("ALL")) findings.push(`K8S-008 ${n}: drop all Linux capabilities`);
    if(!r.requests||!r.limits) findings.push(`K8S-009 ${n}: declare resource requests and limits`);
  });
  if(!findings.length){results.className="results pass";results.innerHTML="<strong>PASS</strong> — workload satisfies the baseline.";}
  else{results.className="results fail";results.innerHTML=`<strong>FAIL — ${findings.length} finding${findings.length===1?"":"s"}</strong><ul>${findings.map(x=>`<li>${x}</li>`).join("")}</ul>`;}
};
load(secure);
