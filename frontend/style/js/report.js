// js/report.js — Backend PDF Trigger Only

(function () {

  console.log("📄 AutoCare Report System Loaded");

  function by(id) { return document.getElementById(id); }

  const preview = by("reportPreview");
  const genBtn = by("genReport");
  const dlBtn = by("dlReport");

  preview.innerHTML = `
    <div class="preview-line muted">
      Click "Generate PDF" to download your medical report.
    </div>
  `;

  genBtn.addEventListener("click", function () {

    genBtn.disabled = true;
    genBtn.innerText = "Generating...";

    window.location.href = "/download-report";

    setTimeout(() => {
      genBtn.disabled = false;
      genBtn.innerText = "Generate PDF";
    }, 2000);

  });

})();
