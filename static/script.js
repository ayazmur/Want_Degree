document.addEventListener("DOMContentLoaded", function () {
  const queryForm = document.getElementById("queryForm");
  const resultDiv = document.getElementById("result");

  queryForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const formData = new FormData(queryForm);
    const query = formData.get("query");

    try {
      const response = await fetch("/query/", {
        method: "POST",
        body: new URLSearchParams({query}),
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
      const html = await response.text();
      resultDiv.innerHTML = html;
    } catch (error) {
      resultDiv.innerHTML = `<p>Error: ${error}</p>`;
    }
  });
});
