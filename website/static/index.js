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

document.getElementById("search-bar").addEventListener("keyup", function () {
  const query = this.value.toLowerCase();
  const items = document.querySelectorAll(".list-group-item");

  items.forEach((item) => {
    const title = item.getAttribute("data-title").toLowerCase();
    const description = item.getAttribute("data-description").toLowerCase();

    // Check if the query matches the title or description
    if (title.includes(query) || description.includes(query)) {
      item.style.display = ""; // Show item
    } else {
      item.style.display = "none"; // Hide item
    }
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
  
  // Toggle the button text
  if (button.innerText === "Vis kun favoritter") {
    button.innerText = "Vis alle opplegg";
    oppleggItems.forEach(item => {
      // If the item is not favorited, hide it
      if (item.getAttribute("data-is-favorite") === "false") {
        item.style.display = "none";
      }
    });
  } else {
    button.innerText = "Vis kun favoritter";
    oppleggItems.forEach(item => {
      // Show all items
      item.style.display = "grid";
    });
  }
}

function disableSubmitButton() {
  document.getElementById('submit-button').disabled = true;
}