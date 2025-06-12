document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  const locale = urlParams.get("locale") || "US";

  fetch("ssd_prices.json")
    .then(res => res.json())
    .then(data => {
      const filtered = data.filter(item => item.locale === locale);
      renderTable(filtered);
    })
    .catch(err => {
      console.error("Failed to load SSD prices:", err);
      document.getElementById("ssd-body").innerHTML = "<tr><td colspan='5'>Failed to load prices.</td></tr>";
    });
});

function renderTable(data) {
  const tableBody = document.getElementById("ssd-body");
  tableBody.innerHTML = "";

  data.forEach(item => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td><img src="${item.image}" alt="${item.title}" /></td>
      <td><a href="${item.url}" target="_blank">${item.title}</a></td>
      <td>${item.capacity}</td>
      <td>${item.price ? `${item.currency} ${item.price}` : "N/A"}</td>
      <td>${item.price_per_tb !== "N/A" ? `${item.currency} ${item.price_per_tb}` : "N/A"}</td>
    `;

    tableBody.appendChild(row);
  });

  setupSorting(data);
}

function setupSorting(data) {
  document.querySelectorAll(".sortable").forEach(th => {
    th.addEventListener("click", () => {
      const key = th.getAttribute("data-key");
      const ascending = !th.classList.contains("asc");

      // Clear all arrows
      document.querySelectorAll(".sortable").forEach(t => t.classList.remove("asc", "desc"));

      // Set current arrow
      th.classList.add(ascending ? "asc" : "desc");

      // Sort data
      const sorted = [...data].sort((a, b) => {
        const valA = a[key];
        const valB = b[key];

        if (valA === "N/A") return 1;
        if (valB === "N/A") return -1;
        if (typeof valA === "number" && typeof valB === "number") {
          return ascending ? valA - valB : valB - valA;
        }
        return ascending
          ? valA.toString().localeCompare(valB, undefined, { numeric: true })
          : valB.toString().localeCompare(valA, undefined, { numeric: true });
      });

      renderTable(sorted);
    });
  });
}
