// Polls job status for rows not yet finished and updates status/download link.
function pollJobs() {
  document.querySelectorAll("#jobs-table tr[data-job-id]").forEach((row) => {
    const statusCell = row.querySelector(".status");
    const currentStatus = statusCell.textContent.trim();
    if (currentStatus === "done" || currentStatus === "error") {
      return;
    }

    const jobId = row.getAttribute("data-job-id");
    fetch(`/jobs/${jobId}`)
      .then((response) => response.json())
      .then((job) => {
        statusCell.textContent = job.status;
        if (job.status === "done") {
          row.querySelector(".download-cell").innerHTML =
            `<a href="/jobs/${jobId}/download">Herunterladen</a>`;
        } else if (job.status === "error") {
          row.querySelector(".download-cell").textContent = job.error_message || "Fehler";
        }
      });
  });
}

setInterval(pollJobs, 3000);
