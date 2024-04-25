function addListeners() {
  console.log('adding listeners');
  const body = document.querySelector("body"),
        sidebar = body.querySelector("#nav"),
        toggle = body.querySelector(".toggle"),
        searchBtn = body.querySelector(".search-box"),
        modeSwitch = body.querySelector(".toggle-switch"),
        modeText = document.querySelector(".mode-text");

  if (!sidebar) {
    console.error("Unable to find sidebar element");
    return;
  }

  // Swipe handling for mobile devices
  let touchStartX = 0, touchEndX = 0;
  let swipeableArea = body;
  let delta = 0;

  swipeableArea.addEventListener('touchstart', function(event) {
    const screenWidth = window.innerWidth;
    const touchX = event.touches[0].clientX;
    touchStartX = touchX < screenWidth * 0.2 ? touchX : 0;
  });

  swipeableArea.addEventListener('touchmove', function(event) {
    if (touchStartX > 0) {
      touchEndX = event.touches[0].clientX;
      delta = touchEndX - touchStartX;

      if (sidebar && delta < -80 && !sidebar.classList.contains('close')) {
        sidebar.classList.add('close');
        document.getElementById("page-content").classList.add('close');
      } else if (sidebar && delta > 80 && sidebar.classList.contains('close')) {
        sidebar.classList.remove('close');
        document.getElementById("page-content").classList.remove('close');
      }
    }
  });

  swipeableArea.addEventListener('touchend', function(event) {
    if (touchStartX > 0) {
      touchEndX = event.changedTouches[0].clientX;
      delta = touchEndX - touchStartX;

      if (sidebar && delta < -80 && !sidebar.classList.contains('close')) {
        sidebar.classList.add('close');
        document.getElementById("page-content").classList.add('close');
      } else if (sidebar && delta > 80 && sidebar.classList.contains('close')) {
        sidebar.classList.remove('close');
        document.getElementById("page-content").classList.remove('close');
      }

      touchStartX = 0;
    }
  });

  // Click handling for desktop devices
  if (toggle) {
    toggle.addEventListener("click", function() {
      sidebar.classList.toggle("close");
      document.getElementById("page-content").classList.toggle("close");
    });
  }
  // Click handling to close sidebar when clicking outside of it
  document.addEventListener("click", function(event) {
    if (sidebar && !sidebar.contains(event.target) && event.target !== toggle) {
      sidebar.classList.add("close");
      document.getElementById("page-content").classList.add("close");
    }
  });
}

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function addListenersModalFilter() {
  console.log('adding listeners modalfilter');
  const body = document.querySelector("body"),
        modal = body.querySelector("#modalfilter"),
        toggle = body.querySelector(".toggle-right"),
        searchBtn = body.querySelector(".search-box"),
        modeSwitch = body.querySelector(".toggle-switch"),
        modeText = document.querySelector(".mode-text");

  if (!modal) {
    console.error("Unable to find modal element");
    return;
  }

  // Swipe handling for mobile devices
  let touchStartX = 0, touchEndX = 0;
  let swipeableArea = body;
  let delta = 0;

  swipeableArea.addEventListener('touchstart', function(event) {
    const screenWidth = window.innerWidth;
    const touchX = event.touches[0].clientX;
    touchStartX = touchX < screenWidth * 0.2 ? touchX : 0;
  });

  swipeableArea.addEventListener('touchmove', function(event) {
    if (touchStartX > 0) {
      touchEndX = event.touches[0].clientX;
      delta = touchEndX - touchStartX;

      if (modal && delta < -80 && !modal.classList.contains('close')) {
        modal.classList.add('close');
        document.getElementById("page-content").classList.add('close');
      } else if (modal && delta > 80 && modal.classList.contains('close')) {
        modal.classList.remove('close');
        document.getElementById("page-content").classList.remove('close');
      }
    }
  });

  swipeableArea.addEventListener('touchend', function(event) {
    if (touchStartX > 0) {
      touchEndX = event.changedTouches[0].clientX;
      delta = touchEndX - touchStartX;

      if (modal && delta < -80 && !modal.classList.contains('close')) {
        modal.classList.add('close');
        document.getElementById("page-content").classList.add('close');
      } else if (modal && delta > 80 && modal.classList.contains('close')) {
        modal.classList.remove('close');
        document.getElementById("page-content").classList.remove('close');
      }

      touchStartX = 0;
    }
  });

  // Click handling for desktop devices
  if (toggle) {
    toggle.addEventListener("click", function() {
      modal.classList.toggle("close-modal");
      document.getElementById("page-content").classList.toggle("close-modal");
    });
  }

  // Click handling to close sidebar when clicking outside of it
  document.addEventListener("click", function(event) {
    if (modal && !modal.contains(event.target) && event.target !== toggle) {
      modal.classList.add("close");
      document.getElementById("page-content").classList.add("close");
    }
  });
}

window.addEventListener("load", function() {
  addListeners();
  addListenersModalFilter();
});
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////



// Get the select-value element
var selectValueElement = document.querySelector('.Select-value');

// Attach a click event listener to the select-value element
selectValueElement.addEventListener('click', function() {

  // Get the currently selected value(s) from the dropdown
  var currentValue = document.querySelector('#Level0NameSelect').value;

  // If there is a selected value, remove it and update the dropdown
  if (currentValue) {
    // If the selected value is an array, remove the last element
    if (Array.isArray(currentValue)) {
      currentValue.pop();
    } 
    // If the selected value is a string, remove it completely
    else {
      currentValue = null;
    }
    // Update the dropdown with the new selected value
    Plotly.d3.select('#Level0NameSelect').property('value', currentValue);
  }

});
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////

var section = $('li');

function toggleAccordion() {
  section.removeClass('active');
  $(this).addClass('active');
}

section.on('click', toggleAccordion);