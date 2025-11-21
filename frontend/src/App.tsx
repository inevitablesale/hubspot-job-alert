import Dashboard from "./components/Dashboard";

function App() {
  return (
    <div className="app-shell">
      <header>
        <h1>HubSpot Job Alert</h1>
        <p>Monitor partner sites for HubSpot-related openings.</p>
      </header>
      <Dashboard />
    </div>
  );
}

export default App;
