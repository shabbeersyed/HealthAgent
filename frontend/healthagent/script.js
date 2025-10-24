document.addEventListener('DOMContentLoaded', () => {
  /* ===============================
   * Globals + Navigation
   * =============================== */
  const screens = document.querySelectorAll('.screen');
  const homeBg  = document.getElementById('homeBg');

  function toTop() { document.documentElement.scrollTop = 0; document.body.scrollTop = 0; }
  function byId(id) { return document.getElementById(id); }

  // Public navigation helpers (used by buttons in HTML)
  window.openScreen = (id, autoLoad = false) => {
    screens.forEach(s => s.classList.remove('active'));
    const tgt = document.getElementById(id);
    if (tgt) tgt.classList.add('active');

    // Show bg video only on home
    if (id === 'homeSection') homeBg?.classList.remove('hide');
    else homeBg?.classList.add('hide');

    toTop();

    // First-time build & optional auto-select
    if (id === 'doctorSection') {
      buildDoctorPatientsOnce();
      buildTestsOnce();
      if (autoLoad) autoSelectDoctorFirst();
    }
    if (id === 'nurseSection') {
      buildNursePatientsOnce();
      if (autoLoad) autoSelectNurseFirst();
    }
    if (id === 'studentSection') {
      buildStudentPatientsOnce();
      if (autoLoad) autoSelectStudentFirst();
    }
  };

  window.goHome = () => {
    screens.forEach(s => s.classList.remove('active'));
    document.getElementById('homeSection')?.classList.add('active');
    homeBg?.classList.remove('hide');
    toTop();
  };

  /* ===============================
   * Data store (dummy)
   * =============================== */
  const patients = [
    { name:"Shabbeer Basha Syed", age:50, weight:84, reason:" Chest Pain",        email:"shabbeerbashasyed773@gmail.com",
      summaries:{ doctor:"", patient:"", nurse:"", student:"" }, tests:[] },
    { name:"Rohit Sharma",         age:35, weight:70, reason:"Headache",         email:"rohit.sharma@gmail.com",
      summaries:{ doctor:"", patient:"", nurse:"", student:"" }, tests:[] },
    { name:"Priya Nair",           age:29, weight:62, reason:"Fever",            email:"priya.nair@gmail.com",
      summaries:{ doctor:"", patient:"", nurse:"", student:"" }, tests:[] },
    { name:"Aman Verma",           age:42, weight:80, reason:"Diabetes Checkup", email:"aman.verma@gmail.com",
      summaries:{ doctor:"", patient:"", nurse:"", student:"" }, tests:[] },
    { name:"Sneha Patel",          age:31, weight:56, reason:"Cough & Cold",     email:"sneha.patel@gmail.com",
      summaries:{ doctor:"", patient:"", nurse:"", student:"" }, tests:[] },
  ];

  /* ===============================
   * Doctor: patient list + details
   * =============================== */
  let docBuilt = false;
  let currentDoctorIndex = 0;

  function buildDoctorPatientsOnce() {
    if (docBuilt) return;
    const container = byId('patientsContainer');
    if (!container) return;

    patients.forEach((p, i) => {
      const card = document.createElement('div');
      card.className = 'patient-card';
      card.innerHTML = `
        <h4>${p.name}</h4>
        <p><b>Age:</b> ${p.age} &nbsp;|&nbsp; <b>Weight:</b> ${p.weight}kg</p>
        <p><b>Reason:</b> ${p.reason}</p>
        <button type="button">View</button>
      `;
      card.addEventListener('click', () => loadDoctorPatient(i));
      card.querySelector('button').addEventListener('click', (e) => { e.stopPropagation(); loadDoctorPatient(i); });
      container.appendChild(card);
    });

    docBuilt = true;
  }

  function autoSelectDoctorFirst() {
    if (patients.length) {
      loadDoctorPatient(0);
      markActiveCard('#patientsContainer', 0);
    }
  }

  function loadDoctorPatient(index) {
    currentDoctorIndex = index;
    const p = patients[index];

    byId('patientName').value   = p.name;
    byId('patientAge').value    = p.age;
    byId('patientWeight').value = p.weight;
    byId('patientEmail').value  = p.email;
    byId('patientReason').value = p.reason;

    byId('summaryText').value   = p.summaries.doctor || '';

    renderSelectedTests(p.tests);
    syncCheckboxes(p.tests);

    markActiveCard('#patientsContainer', index);
  }

  /* ===============================
   * Doctor: tests (built-in + custom)
   * =============================== */
  const builtinTests = [
    "CBC","CMP","Lipid Panel","HbA1c","Chest X-Ray","ECG","MRI","CT Scan","Urinalysis","COVID-19 PCR"
  ];
  let testsBuilt = false;

  function buildTestsOnce() {
    if (testsBuilt) return;
    const wrap = byId('testsWrap');
    if (!wrap) return;

    builtinTests.forEach(name => {
      const id = `t_${name.replace(/\W/g,'_')}`;
      const label = document.createElement('label');
      label.innerHTML = `<input type="checkbox" id="${id}" data-name="${name}"> ${name}`;
      wrap.appendChild(label);

      label.querySelector('input').addEventListener('change', (e) => {
        const testName = e.target.dataset.name;
        toggleTest(currentDoctorIndex, testName, e.target.checked);
      });
    });

    byId('addCustomTest').addEventListener('click', () => {
      const val = byId('customTestInput').value.trim();
      if (!val) return;
      toggleTest(currentDoctorIndex, val, true);
      byId('customTestInput').value = "";
    });

    testsBuilt = true;
  }

  function toggleTest(pIndex, testName, add) {
    const arr = patients[pIndex].tests;
    const exists = arr.includes(testName);
    if (add && !exists) arr.push(testName);
    if (!add && exists) patients[pIndex].tests = arr.filter(t => t !== testName);

    renderSelectedTests(patients[pIndex].tests);
    syncCheckboxes(patients[pIndex].tests);
  }

  function syncCheckboxes(selected) {
    document.querySelectorAll('#testsWrap input[type="checkbox"]').forEach(cb => {
      cb.checked = selected.includes(cb.dataset.name);
    });
  }

  function renderSelectedTests(selected) {
    const box = byId('selectedTests');
    if (!box) return;
    box.innerHTML = '';
    selected.forEach(t => {
      const chip = document.createElement('span');
      chip.className = 'chip';
      chip.innerHTML = `${t} <span class="x" title="Remove">×</span>`;
      chip.querySelector('.x').addEventListener('click', () => toggleTest(currentDoctorIndex, t, false));
      box.appendChild(chip);
    });
  }

  /* ===============================
   * Nurse: patient list + summary
   * =============================== */
  let nurseBuilt = false;
  let currentNurseIndex = 0;

  function buildNursePatientsOnce() {
    if (nurseBuilt) return;
    const container = byId('nursePatientsContainer');
    if (!container) return;

    patients.forEach((p, i) => {
      const card = document.createElement('div');
      card.className = 'patient-card';
      card.innerHTML = `
        <h4>${p.name}</h4>
        <p><b>Age:</b> ${p.age} &nbsp;|&nbsp; <b>Weight:</b> ${p.weight}kg</p>
        <p><b>Reason:</b> ${p.reason}</p>
        <textarea rows="2" readonly style="width:100%; resize:vertical;">${p.summaries.nurse || 'No summary yet.'}</textarea>
        <button type="button">View Summary</button>
      `;
      card.addEventListener('click', () => loadNursePatient(i));
      card.querySelector('textarea').addEventListener('click', (e) => { e.stopPropagation(); loadNursePatient(i); });
      card.querySelector('button').addEventListener('click', (e) => { e.stopPropagation(); loadNursePatient(i); });
      container.appendChild(card);
    });

    nurseBuilt = true;
  }

  function autoSelectNurseFirst() {
    if (patients.length) {
      loadNursePatient(0);
      markActiveCard('#nursePatientsContainer', 0);
    }
  }

  function loadNursePatient(index) {
    currentNurseIndex = index;
    const p = patients[index];

    byId('nurseSelectedName').textContent = `${p.name} — ${p.reason}`;
    byId('nurseSummaryBox').value = p.summaries.nurse || 'No summary received yet.';
    renderChips('nurseTests', p.tests);

    markActiveCard('#nursePatientsContainer', index);
  }

  /* ===============================
   * Students: privacy labels + case
   * =============================== */
  let studentBuilt = false;
  let currentStudentIndex = 0;

  function buildStudentPatientsOnce() {
    if (studentBuilt) return;
    const container = byId('studentPatientsContainer');
    if (!container) return;

    patients.forEach((p, i) => {
      const label = `Patient ${i + 1}`;
      const card = document.createElement('div');
      card.className = 'patient-card';
      card.innerHTML = `
        <h4>${label}</h4>
        <p><b>Age:</b> ${p.age} &nbsp;|&nbsp; <b>Weight:</b> ${p.weight}kg</p>
        <p><b>Case:</b> ${p.reason}</p>
        <button type="button">Open Case</button>
      `;
      card.addEventListener('click', () => loadStudentPatient(i));
      card.querySelector('button').addEventListener('click', (e) => { e.stopPropagation(); loadStudentPatient(i); });
      container.appendChild(card);
    });

    studentBuilt = true;
  }

  function autoSelectStudentFirst() {
    if (patients.length) {
      loadStudentPatient(0);
      markActiveCard('#studentPatientsContainer', 0);
    }
  }

  function loadStudentPatient(index) {
    currentStudentIndex = index;
    const p = patients[index];

    byId('studentSelectedName').textContent = `Patient ${index + 1} — ${p.reason}`;
    byId('studentSummaryBox').value = p.summaries.student || 'Teaching summary will appear here.';
    renderChips('studentTests', p.tests);

    markActiveCard('#studentPatientsContainer', index);
  }

  /* ===============================
   * Doctor: recording & summaries
   * =============================== */
  const startBtn = byId('startRecord');
  const stopBtn  = byId('stopRecord');
  const statusEl = byId('recordingStatus');
  const summary  = byId('summaryText');
  const sendBtn  = byId('sendEmail');
  const editBtn  = byId('editSummary');

  startBtn?.addEventListener('click', () => {
    statusEl.textContent = '🎙 Recording in progress...';
    statusEl.style.color = 'green';
    startBtn.disabled = true;
    stopBtn.disabled  = false;
  });

  stopBtn?.addEventListener('click', () => {
    statusEl.textContent = '✅ Recording stopped';
    statusEl.style.color = 'red';
    startBtn.disabled = false;
    stopBtn.disabled  = true;

    if (!summary.value.trim()) {
      summary.value = 'Doctor and patient discussed symptoms. Exam performed. Tests ordered. Initial therapy started.';
    }
  });

  editBtn?.addEventListener('click', (e) => {
    if (summary.hasAttribute('readonly')) {
      summary.removeAttribute('readonly');
      placeCursorAtEnd(summary);
      e.target.textContent = '💾 Save';
    } else {
      summary.setAttribute('readonly', true);
      e.target.textContent = '✏️ Edit';
      patients[currentDoctorIndex].summaries.doctor = summary.value.trim();
    }
  });

  sendBtn?.addEventListener('click', () => {
    const p = patients[currentDoctorIndex];
    if (!p.email) return alert('Please pick a patient first.');

    // Save doctor’s summary & generate audience versions
    p.summaries.doctor = summary.value.trim();
    const { patientText, nurseText, studentText } = makeAudienceSummaries(p, currentDoctorIndex);
    p.summaries.patient = patientText;
    p.summaries.nurse   = nurseText;
    p.summaries.student = studentText;

    // Broadcast updates so nurse/student views refresh
    document.dispatchEvent(new CustomEvent('patientUpdated', { detail: { index: currentDoctorIndex } }));

    alert(`Summary + tests sent to ${p.email} and synced to Nurse / Student views.`);
  });

  // Cross-screen refresh
  document.addEventListener('patientUpdated', (e) => {
    const i = e.detail.index;

    // Update nurse list preview
    const nurseCard = document.querySelectorAll('#nursePatientsContainer .patient-card')[i];
    if (nurseCard) {
      const ta = nurseCard.querySelector('textarea');
      ta.value = patients[i].summaries.nurse || 'No summary yet.';
    }

    // If nurse/student is open on same patient, refresh detail panel
    if (document.getElementById('nurseSection')?.classList.contains('active') && i === currentNurseIndex) {
      loadNursePatient(i);
    }
    if (document.getElementById('studentSection')?.classList.contains('active') && i === currentStudentIndex) {
      loadStudentPatient(i);
    }
  });

  /* ===============================
   * Helpers
   * =============================== */
  function markActiveCard(containerSel, index) {
    const cards = document.querySelectorAll(`${containerSel} .patient-card`);
    cards.forEach(c => c.classList.remove('active-patient'));
    if (cards[index]) cards[index].classList.add('active-patient');
  }

  function renderChips(containerId, items) {
    const box = byId(containerId);
    if (!box) return;
    box.innerHTML = '';
    items.forEach(t => {
      const s = document.createElement('span');
      s.className = 'chip';
      s.textContent = t;
      box.appendChild(s);
    });
  }

  function placeCursorAtEnd(el) {
    el.focus();
    const len = el.value.length;
    el.setSelectionRange(len, len);
  }

  function makeAudienceSummaries(p, idx) {
    const base = (p.summaries.doctor || '').trim();
    const patientLabel = `Patient ${idx + 1}`;

    const patientText =
`${p.name} (Age ${p.age}) visited for ${p.reason}.
What we discussed:
• Your symptoms and exam
• Tests ordered: ${p.tests.length ? p.tests.join(', ') : '—'}
• Next steps and follow-up

Summary:
${base || 'Your doctor will add your visit summary shortly.'}`;

    const nurseText =
`${p.name} (Age ${p.age}) — ${p.reason}
Handoff notes:
• Tests: ${p.tests.length ? p.tests.join(', ') : 'None'}
• Monitoring: vitals/symptoms; follow-up on results
• Education: meds adherence; red flags
Doctor notes:
${base || '—'}`;

    const studentText =
`${patientLabel}
Chief Concern: ${p.reason}
Assessment:
• Working Dx: (add)
• DDx: (add 2–3)
Plan:
• Tests: ${p.tests.length ? p.tests.join(', ') : 'None'}
• Treatment: (add)
Rationale:
${base || '—'}`;

    return { patientText, nurseText, studentText };
  }

  /* ===============================
   * Auto-init: keep home visible with video
   * =============================== */
  // Ensure the home screen is active on load (video visible)
  openScreen('homeSection');
});
