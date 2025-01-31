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

let debounceTimer;
const searchBar = document.getElementById("search-bar");
if (searchBar) {
  searchBar.addEventListener("keyup", function () {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      const query = this.value.toLowerCase();
      const items = document.querySelectorAll(".list-group-item");

      items.forEach((item) => {
        const title = item.getAttribute("data-title").toLowerCase();
        const description = item.getAttribute("data-description").toLowerCase();
        item.style.display =
          title.includes(query) || description.includes(query) ? "" : "none";
      });
    }, 300);
  });

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
        oppleggItems.forEach(item => {
          if (item.getAttribute("data-is-favorite") === "false") {
            item.style.display = "none";
          }
        });
      } else {
        button.innerText = "Vis kun favoritter";
        oppleggItems.forEach(item => {
          item.style.display = "grid";
        });
      }
    }
  }

  function disableSubmitButton() {
    const submitButton = document.getElementById('submit-button');
    if (submitButton) {
      submitButton.disabled = true;
    }
  }

  document.addEventListener("DOMContentLoaded", async () => {
    const oppleggNameInput = document.getElementById("oppleggNameInput");

    // Sjekk om oppleggNameInput eksisterer og har en verdi  
    if (oppleggNameInput) {
      const oppleggName = oppleggNameInput.value.trim();
      if (oppleggName) {
        const results = await fetchComparison(oppleggName);
        displayResults(results);
      } else {
        // Hvis oppleggNameInput er tom, kan du sette et standard oppleggnavn  
        const defaultOppleggName = "Forrest Gump"; // Endre dette til ønsket standard opplegg  
        const results = await fetchComparison(defaultOppleggName);
        displayResults(results);
      }
    }
  });

  // Fetch comparison function  
async function fetchComparison(oppleggName) {
    console.log(`Fetching comparison for: ${oppleggName}`);
    const response = await fetch(`/compare?opplegg_name=${encodeURIComponent(oppleggName)}`);
    if (!response.ok) {
        console.error("Failed to fetch comparison data");
        return [];
    }
    const data = await response.json();
    return data;
}

// Display results function  
function displayResults(results) {
    const opplegg1Box = document.getElementById("opplegg1-title");
    const opplegg1Description = document.getElementById("opplegg1-description");
    const opplegg2Box = document.getElementById("opplegg2-title");
    const opplegg2Description = document.getElementById("opplegg2-description");
    const opplegg3Box = document.getElementById("opplegg3-title");
    const opplegg3Description = document.getElementById("opplegg3-description");

    // Clear previous results
    opplegg1Box.innerHTML = '';
    opplegg1Description.innerHTML = '';
    opplegg2Box.innerHTML = '';
    opplegg2Description.innerHTML = '';
    opplegg3Box.innerHTML = '';
    opplegg3Description.innerHTML = '';

    // If no results, show a message
    if (results.length === 0) {
        opplegg1Box.innerText = "Ingen lignende opplegg funnet.";
        return;
    }

    // Display results in the boxes
    if (results[0]) {
        opplegg1Box.innerText = results[0].name;
        opplegg1Description.innerText = `Similarity: ${(results[0].similarity_score * 100).toFixed(2)}%`;
    }
    if (results[1]) {
        opplegg2Box.innerText = results[1].name;
        opplegg2Description.innerText = `Similarity: ${(results[1].similarity_score * 100).toFixed(2)}%`;
    }
    if (results[2]) {
        opplegg3Box.innerText = results[2].name;
        opplegg3Description.innerText = `Similarity: ${(results[2].similarity_score * 100).toFixed(2)}%`;
    }
}
}