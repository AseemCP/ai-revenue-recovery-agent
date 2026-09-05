async function loadDashboard() {
  try {
    const response = await fetch("http://127.0.0.1:8000/dashboard/summary");

    if (!response.ok) {
      throw new Error("Failed to fetch dashboard data");
    }

    const data = await response.json();

    document.getElementById("failedPayments").textContent =
      data.total_failed_payments;

    document.getElementById("recoveryAttempts").textContent =
      data.total_recovery_attempts;

    document.getElementById("successfulRecoveries").textContent =
      data.successful_recoveries;

    document.getElementById("failedRetries").textContent = data.failed_retries;

    document.getElementById("pendingRecoveries").textContent =
      data.pending_recoveries;

    document.getElementById("recoveryRate").textContent =
      data.recovery_rate + "%";

    document.getElementById("amountRecovered").textContent =
      "₹" + Number(data.total_amount_recovered_inr).toFixed(2);

    updateRecoveryChart(data);
  } catch (error) {
    console.error("Failed to load dashboard:", error);
  }
}

async function loadRecoveryAttempts() {
  try {
    const response = await fetch(
      "http://127.0.0.1:8000/dashboard/recovery-attempts",
    );

    if (!response.ok) {
      throw new Error("Failed to fetch recovery attempts");
    }

    const attempts = await response.json();

    // -------------------------
    // AI MESSAGE
    // -------------------------

    const aiMessageElement = document.getElementById("aiMessage");

    if (aiMessageElement) {
      if (attempts.length > 0 && attempts[0].ai_message) {
        aiMessageElement.textContent = attempts[0].ai_message;
      } else {
        aiMessageElement.textContent = "Waiting for a recovery decision...";
      }
    }

    // -------------------------
    // RECOVERY ATTEMPTS TABLE
    // -------------------------

    const table = document.getElementById("attemptsTable");

    table.innerHTML = "";

    if (attempts.length === 0) {
      table.innerHTML = `
        <tr>
          <td colspan="8">No recovery attempts found</td>
        </tr>
      `;
      return;
    }

    attempts.forEach((attempt) => {
      const row = document.createElement("tr");

      const priority = attempt.priority || "N/A";
      const status = attempt.status || "N/A";

      row.innerHTML = `
        <td>${attempt.payment_id}</td>

        <td>₹${Number(attempt.amount).toFixed(2)}</td>

        <td>${attempt.action || "N/A"}</td>

        <td>
          <span class="priority ${priority.toLowerCase()}">
            ${priority}
          </span>
        </td>

        <td>${attempt.reason || "N/A"}</td>

        <td>${attempt.retry_count || 0}</td>

        <td>
          <span class="status ${status.toLowerCase()}">
            ${status}
          </span>
        </td>

        <td>
          ${
            attempt.retry_link
              ? `
                <a
                  href="${attempt.retry_link}"
                  target="_blank"
                  class="retry-button"
                >
                  Retry Payment
                </a>
              `
              : "-"
          }
        </td>
      `;

      table.appendChild(row);
    });
  } catch (error) {
    console.error("Failed to load recovery attempts:", error);
  }
}

// Load dashboard data
loadDashboard();
loadRecoveryAttempts();

setInterval(() => {
  loadDashboard();
  loadRecoveryAttempts();
}, 5000);

let recoveryChart = null;

function updateRecoveryChart(data) {
  const canvas = document.getElementById("recoveryChart");

  if (!canvas) {
    return;
  }

  if (recoveryChart) {
    recoveryChart.destroy();
  }

  recoveryChart = new Chart(canvas, {
    type: "bar",

    data: {
      labels: ["Successful", "Pending", "Failed"],

      datasets: [
        {
          label: "Recovery Attempts",

          data: [
            data.successful_recoveries,
            data.pending_recoveries,

            data.total_recovery_attempts -
              data.successful_recoveries -
              data.pending_recoveries,
          ],
        },
      ],
    },

    options: {
      responsive: true,

      maintainAspectRatio: false,

      plugins: {
        legend: {
          display: false,
        },
      },

      scales: {
        y: {
          beginAtZero: true,

          ticks: {
            precision: 0,
          },
        },
      },
    },
  });
}
