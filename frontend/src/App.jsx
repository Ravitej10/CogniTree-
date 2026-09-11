import { useState, useEffect } from "react";
import HomePage from "./pages/HomePage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import SignupPage from "./pages/SignupPage.jsx";
import Dashboard from "./pages/Dashboard.jsx";

export function navigate(to) {
  if (window.location.pathname !== to) {
    window.history.pushState({}, "", to);
    window.dispatchEvent(new PopStateEvent("popstate"));
  }
}

export default function App() {
  const [currentPath, setCurrentPath] = useState(window.location.pathname);

  useEffect(() => {
    function handleLocationChange() {
      setCurrentPath(window.location.pathname);
    }

    window.addEventListener("popstate", handleLocationChange);

    // Intercept clicks on internal relative links to make SPA navigation seamless
    function handleLinkClick(e) {
      const anchor = e.target.closest("a");
      if (!anchor) return;
      const href = anchor.getAttribute("href");
      if (
        href &&
        href.startsWith("/") &&
        !href.startsWith("//") &&
        !anchor.hasAttribute("download") &&
        anchor.target !== "_blank" &&
        !e.ctrlKey &&
        !e.metaKey &&
        !e.shiftKey &&
        !e.altKey
      ) {
        // If it has a hash link like /#how-it-works on the homepage, allow standard behavior if already on /
        if (href.startsWith("/#") && window.location.pathname === "/") {
          return;
        }
        e.preventDefault();
        navigate(href);
      }
    }

    document.addEventListener("click", handleLinkClick);

    return () => {
      window.removeEventListener("popstate", handleLocationChange);
      document.removeEventListener("click", handleLinkClick);
    };
  }, []);

  let PageComponent = HomePage;
  if (currentPath === "/login") {
    PageComponent = LoginPage;
  } else if (currentPath === "/signup") {
    PageComponent = SignupPage;
  } else if (currentPath === "/dashboard") {
    PageComponent = Dashboard;
  }

  return <PageComponent />;
}
