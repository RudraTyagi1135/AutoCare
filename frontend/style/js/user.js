(function(){

  function by(id){ return document.getElementById(id); }

  function riskClass(p){
    if(p>=70) return 'risk-high';
    if(p>=40) return 'risk-mid';
    return 'risk-low';
  }

  function createDoughnut(canvasId, percent, color){
    const canvas = by(canvasId);
    if(!canvas) return null;

    const ctx = canvas.getContext('2d');
    if(canvas._chart) canvas._chart.destroy();

    const chart = new Chart(ctx,{
      type:'doughnut',
      data:{
        labels:["Risk","Safe"],
        datasets:[{
          data:[percent,100-percent],
          backgroundColor:[color,"#eef2f7"],
          borderWidth:0
        }]
      },
      options:{
        responsive:true,
        plugins:{legend:{display:false}}
      }
    });

    canvas._chart = chart;
    return chart;
  }

  function createShapBars(canvasId, contributors){
    const canvas = by(canvasId);
    if(!canvas || !contributors) return;

    const ctx = canvas.getContext("2d");
    if(canvas._chart) canvas._chart.destroy();

    const labels = contributors.map(c => c.feature);
    const values = contributors.map(c => c.impact);

    const colors = values.map(v => v > 0 ? "#d9534f" : "#0b5ecf");

    const chart = new Chart(ctx,{
      type:'bar',
      data:{
        labels: labels,
        datasets:[{
          data: values,
          backgroundColor: colors
        }]
      },
      options:{
        indexAxis:'y',
        responsive:true,
        plugins:{legend:{display:false}},
        scales:{
          x:{beginAtZero:true}
        }
      }
    });

    canvas._chart = chart;
  }

  function updatePanel(diseaseKey, riskId, reasonId, donutId, shapId, color){

    const diseaseData = window.predictionData?.predictions?.[diseaseKey];
    if(!diseaseData) return;

    const percent = diseaseData.risk_percent;

    const riskEl = by(riskId);
    if(riskEl){
      riskEl.innerText = percent + "%";
      riskEl.className = "risk-badge " + riskClass(percent);
    }

    // 🔥 TEXT EXPLANATION
    const reasonEl = by(reasonId);
    if(reasonEl && diseaseData.explainability?.top_contributors){
      const contributors = diseaseData.explainability.top_contributors;

      let html="";
      contributors.slice(0,5).forEach((c,i)=>{
        html += `<li>
                   ${i+1}. ${c.feature}
                   <div class="reason-sub">
                     impact ${c.impact.toFixed(3)}
                   </div>
                 </li>`;
      });
      reasonEl.innerHTML = html;

      // 🔥 SHAP BAR CHART
      createShapBars(shapId, contributors.slice(0,5));
    }

    createDoughnut(donutId, percent, color);
  }

  document.addEventListener("DOMContentLoaded",function(){

    if(!window.predictionData){
      console.log("No prediction data available.");
      return;
    }

    updatePanel("diabetes",
      "risk-diabetes",
      "reasons-diabetes",
      "chart-diabetes-canvas",
      "shap-diabetes-canvas",
      "#0b5ecf"
    );

    updatePanel("heart",
      "risk-heart",
      "reasons-heart",
      "chart-heart-canvas",
      "shap-heart-canvas",
      "#d9534f"
    );

    updatePanel("stroke",
      "risk-stroke",
      "reasons-stroke",
      "chart-stroke-canvas",
      "shap-stroke-canvas",
      "#6f42c1"
    );

  });

})();
