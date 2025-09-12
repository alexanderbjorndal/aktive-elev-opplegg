function deleteOpplegg(oppleggId) {
  fetch("/delete-opplegg", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ oppleggId: oppleggId }),
  })
    .then((response) => {
      if (response.ok) {
        window.location.href = "/"; // Redirect on success
      } else {
        console.error("Error deleting opplegg:", response.status);
      }
    })
    .catch((error) => console.error("Fetch error:", error));
}

function toggleCheckbox(checkbox) {
  const label = document.querySelector(`label[for="${checkbox.id}"]`);
  const state = label.getAttribute("data-state");

  if (state === "not-selected") {
    // Change to selected
    label.setAttribute("data-state", "selected");
  } else if (state === "selected") {
    // Change to removed
    label.setAttribute("data-state", "removed");
  } else {
    // Change back to not selected
    label.setAttribute("data-state", "not-selected");
  }

  updateOppleggDetails();
}

function toggleHeart(heartImg) {
  if (heartImg.src.includes("Heart-empty.png")) {
    heartImg.src = heartFull;
  } else {
    heartImg.src = heartEmpty;
  }
}

function updateOppleggDetails() {
  const selectedTraits = Array.from(
    document.querySelectorAll('input[name="tag"]:checked')
  ).map((checkbox) => checkbox.value);

  const removedTraits = Array.from(
    document.querySelectorAll('input[name="tag"]')
  )
    .filter((checkbox) => {
      const label = checkbox.nextElementSibling;
      return label.getAttribute("data-state") === "removed";
    })
    .map((checkbox) => checkbox.value);

  const oppleggItems = document.querySelectorAll(".list-group-item");

  oppleggItems.forEach((item) => {
    const traits = item.getAttribute("data-traits").split(",");

    // Check if item matches selected traits
    const matchesAllTraits = selectedTraits.every((trait) =>
      traits.includes(trait)
    );

    // Check if item matches removed traits
    const matchesRemovedTraits = removedTraits.some((trait) =>
      traits.includes(trait)
    );

    // Show item if it matches all selected traits and does not match any removed traits
    if (matchesAllTraits && !matchesRemovedTraits) {
      item.classList.remove("hidden");
    } else {
      item.classList.add("hidden");
    }
  });
}

function removeAllFilters() {
  // Get all checkboxes
  const checkboxes = document.querySelectorAll('input[name="tag"]');

  // Uncheck all checkboxes and reset label states
  checkboxes.forEach((checkbox) => {
    checkbox.checked = false; // Uncheck the checkbox
    const label = checkbox.nextElementSibling; // Get the corresponding label
    label.setAttribute("data-state", "not-selected"); // Reset state to not-selected
  });

  // Call the function to update displayed items
  updateOppleggDetails();
}

// Function to reset filters
function resetFilters() {
  // Get all checkboxes
  const checkboxes = document.querySelectorAll('input[name="tag"]');

  // Uncheck each checkbox and set state to not-selected
  checkboxes.forEach((checkbox) => {
    checkbox.checked = false; // Uncheck the checkbox
    checkbox.nextElementSibling.setAttribute("data-state", "not-selected"); // Reset state to not-selected
  });

  // Update opplegg details to reflect the changes
  updateOppleggDetails();
}

// Call resetFilters on page load
window.onload = resetFilters;

// Update states of all labels based on checkbox states
const allCheckboxes = document.querySelectorAll('input[name="tag"]');
allCheckboxes.forEach((checkbox) => {
  const label = checkbox.nextElementSibling;
  if (checkbox.checked) {
    label.setAttribute("data-state", "selected");
  } else if (label.getAttribute("data-state") === "removed") {
    label.setAttribute("data-state", "removed");
  } else {
    label.setAttribute("data-state", "not-selected");
  }
});

function addEventListenerIfExists(selector, event, handler) {
  const element = document.getElementById(selector);
  if (element) {
    element.addEventListener(event, handler);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  addEventListenerIfExists("search-bar", "keyup", function () {
    const query = this.value.toLowerCase();
    const items = document.querySelectorAll(".list-group-item");

    items.forEach((item) => {
      const title = item.getAttribute("data-title").toLowerCase();
      const description = item.getAttribute("data-description").toLowerCase();

      // Sjekk om søkespørsmålet matcher tittelen eller beskrivelsen
      if (title.includes(query) || description.includes(query)) {
        item.style.display = ""; // Vis element
      } else {
        item.style.display = "none"; // Skjul element
      }
    });
  });
});

// Attach event listeners to checkboxes
document.querySelectorAll('input[name="tag"]').forEach((checkbox) => {
  checkbox.addEventListener("click", function () {
    const label = this.nextElementSibling;

    if (label.getAttribute("data-state") === "not-selected") {
      label.setAttribute("data-state", "selected");
    } else if (label.getAttribute("data-state") === "selected") {
      label.setAttribute("data-state", "removed");
      // Do not uncheck the checkbox here
    } else {
      label.setAttribute("data-state", "not-selected"); // If removed, revert to not-selected
      this.checked = false; // Uncheck the checkbox when reverting to not-selected
    }

    updateOppleggDetails(); // Update the displayed items based on the selected traits
  });
});

const oppleggId = new URLSearchParams(window.location.search).get("opplegg_id");

if (oppleggId) {
  document.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search); // Get query string params
    const oppleggId = urlParams.get("opplegg_id"); // Extract opplegg_id from URL
    console.log("Extracted opplegg_id from URL:", oppleggId); // Debugging

    if (oppleggId) {
      const results = await fetchComparison(oppleggId); // Make the fetch request
      if (results && results.length > 0) {
        displayResults(results); // Display the results in the boxes
      } else {
        console.error("No results found or the results are empty.");
      }
    } else {
      console.error("No opplegg_id found in the URL.");
    }
  });

  // Fetch comparison function
  async function fetchComparison(oppleggId) {
    const response = await fetch(
      `/compare?opplegg_id=${encodeURIComponent(oppleggId)}`
    ); // This calls /compare with opplegg_id
    if (!response.ok) {
      return [];
    }
    const data = await response.json(); // Parse the JSON response
    return data;
  }

  // Display results function
  function displayResults(results) {
    console.log("displayResults called", results); // Log the results to see the structure

    const opplegg1Link = document.getElementById("opplegg1-link");
    const opplegg1Box = document.getElementById("opplegg1-title");
    const opplegg1Description = document.getElementById("opplegg1-description");

    const opplegg2Link = document.getElementById("opplegg2-link");
    const opplegg2Box = document.getElementById("opplegg2-title");
    const opplegg2Description = document.getElementById("opplegg2-description");

    const opplegg3Link = document.getElementById("opplegg3-link");
    const opplegg3Box = document.getElementById("opplegg3-title");
    const opplegg3Description = document.getElementById("opplegg3-description");

    // Clear previous results
    opplegg1Box.innerHTML = "";
    opplegg1Description.innerHTML = "";
    opplegg2Box.innerHTML = "";
    opplegg2Description.innerHTML = "";
    opplegg3Box.innerHTML = "";
    opplegg3Description.innerHTML = "";

    // If no results, show a message
    if (results.length === 0) {
      opplegg1Box.innerText = "Ingen lignende opplegg funnet.";
      return;
    }

    // Display results in the boxes and set up links
    if (results[0]) {
      opplegg1Box.innerText = results[0].name;
      opplegg1Description.innerText = `${results[0].data}`;
      opplegg1Link.href = `/se-opplegg?opplegg_id=${results[0].id}`; // Use the id for the link
      console.log(
        `opplegg1 link set to: /se-opplegg?opplegg_id=${results[0].id}`
      ); // Debugging
    }
    if (results[1]) {
      opplegg2Box.innerText = results[1].name;
      opplegg2Description.innerText = `${results[1].data}`;
      opplegg2Link.href = `/se-opplegg?opplegg_id=${results[1].id}`; // Use the id for the link
      console.log(
        `opplegg2 link set to: /se-opplegg?opplegg_id=${results[1].id}`
      ); // Debugging
    }
    if (results[2]) {
      opplegg3Box.innerText = results[2].name;
      opplegg3Description.innerText = `${results[2].data}`;
      opplegg3Link.href = `/se-opplegg?opplegg_id=${results[2].id}`; // Use the id for the link
      console.log(
        `opplegg3 link set to: /se-opplegg?opplegg_id=${results[2].id}`
      ); // Debugging
    }
  }
}

let debounceTimer;
const searchBar = document.getElementById("search-bar");

if (searchBar) {
  searchBar.addEventListener("keyup", function () {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      const query = this.value.trim().toLowerCase();
      const items = Array.from(document.querySelectorAll(".list-group-item"));

      if (!query) {
        // show all if query is empty
        items.forEach((item) => (item.style.display = ""));
        return;
      }

      const queryWords = query.split(/\s+/); // split query into words

      // Compute a score for each item based on how many words match
      const scoredItems = items.map((item) => {
        const title = item.getAttribute("data-title").toLowerCase();
        const description = item.getAttribute("data-description").toLowerCase();
        const comments =
          item.getAttribute("data-comments")?.toLowerCase() || "";

        let score = 0;
        queryWords.forEach((word) => {
          if (title.includes(word)) score += 3; // give title more weight
          if (description.includes(word)) score += 2;
          if (comments.includes(word)) score += 1;
        });

        return { item, score };
      });

      // Hide items with zero score and show the rest
      scoredItems.forEach(
        (si) => (si.item.style.display = si.score > 0 ? "" : "none")
      );

      // Sort items in the DOM by score descending
      const parent = items[0].parentNode;
      scoredItems
        .filter((si) => si.score > 0)
        .sort((a, b) => b.score - a.score)
        .forEach((si) => parent.appendChild(si.item));
    }, 300); // debounce
  });
}

document.querySelectorAll(".opplegg-delete").forEach((button) => {
  button.addEventListener("click", function (event) {
    event.preventDefault();
    event.stopPropagation();

    const oppleggId = this.getAttribute("data-opplegg-id");
    deleteOpplegg(oppleggId);
  });
});

// Function to toggle visibility of non-favorited opplegg
function toggleFavorites() {
  const button = document.getElementById("toggle-favorites");
  const oppleggItems = document.querySelectorAll(".list-group-item");

  if (button) {
    // Toggle the button text
    if (button.innerText === "Vis kun favoritter") {
      button.innerText = "Vis alle opplegg";
      oppleggItems.forEach((item) => {
        if (item.getAttribute("data-is-favorite") === "false") {
          item.style.display = "none";
        }
      });
    } else {
      button.innerText = "Vis kun favoritter";
      oppleggItems.forEach((item) => {
        item.style.display = "grid";
      });
    }
  }
}

function disableSubmitButton() {
  const submitButton = document.getElementById("submit-button");
  if (submitButton) {
    submitButton.disabled = true;
  }
}

// This function will get the opplegg_id from the URL
function getOppleggIdFromUrl() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get("opplegg_id");
}

let debounceTimer2;

async function fetchSimilarOpplegg() {
  const name = document.getElementById("opplegg").value;
  const description = document.getElementById("data").value;
  const selectedTraits = [
    ...document.querySelectorAll("input[name='tags']:checked"),
  ].map((cb) => cb.value);

  const response = await fetch("/live-compare", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description, traits: selectedTraits }),
  });

  if (!response.ok) return;

  const results = await response.json();

  const container = document.getElementById("similarity-list");
  const warningContainer = document.getElementById("similarity-warning");
  container.innerHTML = "";
  warningContainer.innerHTML = ""; // clear previous warning

  if (results.length === 0) {
    container.innerText = "Ingen lignende opplegg funnet.";
    return;
  }

  // Sort results by similarity descending
  results.sort((a, b) => b.similarity_score - a.similarity_score);

  // Check for high similarity (>70%) on the first opplegg
  const first = results[0];
  if (first.similarity_score > 0.7) {
    const percent = (first.similarity_score * 100).toFixed(0);
    warningContainer.innerHTML = `
        <div style="background-color: #fff3cd; padding: 10px; border-left: 5px solid #ffeeba; border-radius: 5px; margin-bottom: 10px; font-weight: 500;">
            Er du sikker på at opplegget ditt ikke er det samme som 
            <a href="/se-opplegg?opplegg_id=${first.id}" style="text-decoration: underline; color: #0a58ca;">${first.name}</a> 
            ?<br>
            Du kan også skrive kommentar under 
            <a href="/se-opplegg?opplegg_id=${first.id}#comments" style="text-decoration: underline; color: #0a58ca;">${first.name}</a> 
            for å forklare en variant av opplegget.
        </div>
    `;
  }

  // Display all results
  results.forEach((opplegg, index) => {
    const div = document.createElement("div");
    const percent = (opplegg.similarity_score * 100).toFixed(1);
    div.innerHTML = `
        <a href="/se-opplegg?opplegg_id=${opplegg.id}">
          <strong>${opplegg.name}</strong>
        </a>
        <p>${opplegg.data}</p>
        <small>Likhet: ${percent}%</small>
        <hr>
    `;
    // Only highlight the first if similarity > 70%
    if (index === 0 && opplegg.similarity_score > 0.7) {
      div.style.backgroundColor = "#fff3cd"; // subtle light yellow
      div.style.borderLeft = "4px solid #ffeeba"; // soft border
      div.style.borderRadius = "5px";
      div.style.padding = "5px 10px";
    }
    container.appendChild(div);
  });
}

// Debounce function to reduce server calls
function debounceFetch() {
  clearTimeout(debounceTimer2);
  debounceTimer2 = setTimeout(fetchSimilarOpplegg, 300);
}

// Event listeners
document.getElementById("opplegg").addEventListener("input", debounceFetch);
document.getElementById("data").addEventListener("input", debounceFetch);
document.querySelectorAll("input[name='tags']").forEach((cb) => {
  cb.addEventListener("change", debounceFetch);
});
