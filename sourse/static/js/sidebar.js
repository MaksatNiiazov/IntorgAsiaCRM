const body = document.querySelector("body");
const darkLight = document.querySelector("#darkLight");
const sidebar = document.querySelector(".sidebar");
const submenuItems = document.querySelectorAll(".submenu_item");
const sidebarOpen = document.querySelector("#sidebarOpen");
const sidebarClose = document.querySelector(".collapse_sidebar");
const sidebarExpand = document.querySelector(".expand_sidebar");
const content = document.querySelector(".content");
const otherElement = document.querySelector(".dark-light");

sidebarOpen.addEventListener("click", () => {
  sidebar.classList.toggle("close");
  content.classList.toggle("expanded");
  if (sidebar.classList.contains("close")) {
    content.style.marginLeft = "0";
  } else {
    content.style.marginLeft = "260px";
  }
});

sidebarClose.addEventListener("click", () => {
  sidebar.classList.add("close", "hoverable");
  content.classList.remove("expanded");
  content.style.marginLeft = "80px";
});

sidebarExpand.addEventListener("click", () => {
  sidebar.classList.remove("close", "hoverable");
  content.classList.add("expanded");
  content.style.marginLeft = "260px";
});

sidebar.addEventListener("mouseenter", () => {
  if (sidebar.classList.contains("hoverable")) {
    sidebar.classList.remove("close");
    content.classList.add("expanded");
    content.style.marginLeft = "260px";
  }
});

sidebar.addEventListener("mouseleave", () => {
  if (sidebar.classList.contains("hoverable")) {
    sidebar.classList.add("close");
    content.classList.remove("expanded");
    content.style.marginLeft = "80px";
  }
});

darkLight.addEventListener("click", () => {
  body.classList.toggle("dark");
  if (body.classList.contains("dark")) {
    darkLight.classList.replace("bx-sun", "bx-moon");
    otherElement.classList.replace("dark");
  } else {
    darkLight.classList.replace("bx-moon", "bx-sun");
    otherElement.classList.replace("dark");
  }
});

submenuItems.forEach((item, index) => {
  item.addEventListener("click", () => {
    item.classList.toggle("show_submenu");
    submenuItems.forEach((item2, index2) => {
      if (index !== index2) {
        item2.classList.remove("show_submenu");
      }
    });
  });
});

// Initial setup based on screen width
function updateSidebarLayout() {
  if (window.innerWidth < 768) {
    sidebar.classList.add("close");
    content.classList.add("expanded");
    content.style.marginLeft = "0";
  } else {
    sidebar.classList.remove("close");
    content.classList.remove("expanded");
    content.style.marginLeft = "260px";
  }
}

window.addEventListener("resize", updateSidebarLayout);
updateSidebarLayout(); // Run the initial setup on page load
